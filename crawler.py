import re
import time
import bag
import url
import table
import proxy
import random
import argparse
import html_page
from math import ceil
from bs4 import BeautifulSoup
from configparser import ConfigParser


def read_config():
    config = ConfigParser()
    config.read('config.ini')
    mysql_user = config.get('mysql', 'mysql_user')
    mysql_pass = config.get('mysql', 'mysql_pass')
    mysql_host = config.get('mysql', 'mysql_host')
    mysql_base = config.get('mysql', 'mysql_base')
    expiry_hours = config.get('params', 'expiry_hours')
    time_secs = config.get('params', 'timeout_between_urls')
    proxy_list_keys = config.get('params', 'proxy_list_key')
    #      0           1           2           3           4          5                6
    return mysql_user, mysql_pass, mysql_host, mysql_base, time_secs, proxy_list_keys, expiry_hours


def parse_pages(start_page, pages, debug, sql_table, creds, proxy_pass):

    import url
    parse_page = url.Url(start_page)
    first_page = html_page.HtmlPage(parse_page.get_url())
    html = first_page.get_html(creds, proxy_pass)

    if html:
        soup = BeautifulSoup(html, 'html.parser')

        # 1st page
        arts_dict = {}
        print(parse_page.get_url())
        for i in soup.findAll('div', class_="dtList i-dtList j-card-item"):
            art_num = re.search(r'\d+', i.get('data-catalogercod1s'))
            arts_dict[art_num[0]] = i.find('a')['href']
        for art, url in arts_dict.items():
                if not sql_table.table_check_presence(art, creds[6]):
                    handbag = bag.Bag()
                    handbag.get_bag_page(art, url, debug, creds, proxy_pass)
                    sql_table.table_append(handbag)
        sql_table.cnx.commit()

        # after 1st page
        if parse_page.check_key('page'):
            return 0
        else:
            parse_page.add_key('page', '1')

        # 2nd page and further
        for i in range(2, pages + 1):
            parse_page.change_key('page', str(i))
            print(parse_page.get_url())
            have_a_try = 3
            if have_a_try:
                further_page = html_page.HtmlPage(parse_page.get_url())
                arts_dict = further_page.get_wb_page(creds, proxy_pass)
                if arts_dict:
                    for art, url in arts_dict.items():
                        if not sql_table.table_check_presence(art, creds[6]):
                            handbag = bag.Bag()
                            handbag.get_bag_page(art, url, debug, creds, proxy_pass)
                            sql_table.table_append(handbag)
                    sql_table.cnx.commit()
                    continue
                else:
                    sql_table.cnx.commit()
                    print(f"Page {str(i)} parse error. Trying again.")
                    have_a_try -= 1
            else:
                sql_table.cnx.commit()
                print(f"No luck. Next page.")


def push_and_pull(start_page, pages, debug, sql_table, creds, proxy_pass):
    pnp_start = url.Url(start_page)
    pnp_start.add_key('sort', 'priceup')
    parse_pages(pnp_start.get_url(), 100, debug, sql_table, creds, proxy_pass)
    pnp_start.change_key('sort', 'pricedown')
    parse_pages(pnp_start.get_url(), pages - 100, debug, sql_table, creds, proxy_pass)


if __name__ == '__main__':
    cred_tuple = read_config()
    parser = argparse.ArgumentParser()
    parser.add_argument("database", help="База данных для заполнения")
    parser.add_argument("source", type=str, help="URL страницы, откуда начинать")
    parser.add_argument("-c", "--clean", action="store_true", help="Очистить базу данных")
    parser.add_argument("-d", "--debug", action="store_true", help="Расширенный вывод")
    parser.add_argument("-u", "--update", action="store_true", help="Обновить базу http прокси")
    parser.add_argument("-s", "--https", action="store_true", help="Использовать и https прокси")
    parser.add_argument("-n", "--no-proxy", dest="noproxy", action="store_true", help="Не использовать прокси")
    parser.add_argument("-m", "--material", action="store_true", help="Заполнить недостающие материалы")
    args = parser.parse_args()
    http_url = f'http://hidemyna.me/ru/api/proxylist.php?code={cred_tuple[5]}&maxtime=1000&type=h&out=plain'
    https_url = f'http://hidemyna.me/ru/api/proxylist.php?code={cred_tuple[5]}&maxtime=1000&type=s&out=plain'

    mysql_table = table.Table(args.database, cred_tuple)
    table_exist = mysql_table.table_check()
    if table_exist:
        if args.clean:
            mysql_table.table_truncate()
    else:
        mysql_table.table_make()

    if args.update or args.https:
        clear_table = True
        h = proxy.Proxy('http', http_url)
        s = proxy.Proxy('https', https_url)
        len_table = h.form_table(clear_table)
        if args.https:
            print(f"В базе {len_table} прокси.")
            clear_table = False
            time.sleep(60)
            len_table += s.form_table(clear_table)
        print(f"В базе {len_table} прокси.")

    url = url.Url(args.source)
    main_page = html_page.HtmlPage(url.get_url())
    main_html = main_page.get_html(cred_tuple, args.noproxy)

    if main_html and not args.material:
        if url.check_key('page'):
            parse_pages(url.get_url(), 1, args.debug, mysql_table, cred_tuple, args.noproxy)
        else:
            main_soup = BeautifulSoup(main_html, 'html.parser')
            try:
                items = main_soup.find('span', class_="total many").find('span').text
            except AttributeError:
                print("Bad first page. Try to run again.")
                raise Exception
            print(f"{items} товаров")
            pages = ceil(int(items) / 100)
            if pages > 200:
                pages = 200
            print(f"{str(pages)} страниц")
            if 100 < pages <= 200:
                push_and_pull(url.get_url(), pages, args.debug, mysql_table, cred_tuple, args.noproxy)
            if pages <= 100:
                parse_pages(url.get_url(), pages, args.debug, mysql_table, cred_tuple, args.noproxy)

    check_list = mysql_table.table_check_material()
    have_a_try = 3
    while len(check_list) and have_a_try:
        print(f"Пустых {len(check_list)} материалов. Заполняем...")
        for index in check_list:
            secs = int(random.random() * int(cred_tuple[4]))
            time.sleep(secs)
            empty_math_page = html_page.HtmlPage(f"https://www.wildberries.ru/catalog/{index[1]}/detail.aspx")
            text = empty_math_page.get_html(cred_tuple, args.noproxy)
            if text:
                empty_soup = BeautifulSoup(text, 'html.parser')
                empty_bag = bag.Bag()
                empty_bag.set_material(empty_soup, args.debug)
                mysql_table.table_update_material(index[0], empty_bag.material)
            mysql_table.cnx.commit()
        check_list = mysql_table.table_check_material()
        have_a_try -= 1

    print("Готово.")
    mysql_table.end_table_connect()
