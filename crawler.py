import re
import time
import bag
import table
import proxy
import random
import argparse
import html_page
from bs4 import BeautifulSoup
from configparser import ConfigParser


def read_config():
    config = ConfigParser()
    config.read('config.ini')
    mysql_user = config.get('mysql', 'mysql_user')
    mysql_pass = config.get('mysql', 'mysql_pass')
    mysql_host = config.get('mysql', 'mysql_host')
    mysql_base = config.get('mysql', 'mysql_base')
    time_secs = config.get('params', 'timeout_between_urls')
    proxy_list_keys = config.get('params', 'proxy_list_key')
    return mysql_user, mysql_pass, mysql_host, mysql_base, time_secs, proxy_list_keys


def parse_pages(start_page, pages, debug, timeout, sql_table):

    first_page = html_page.HtmlPage(start_page)
    html = first_page.get_html()

    if html:
        soup = BeautifulSoup(html, 'html.parser')

        # 1st page
        arts_dict = {}
        print(start_page)
        for i in soup.findAll('div', class_="dtList i-dtList"):
            art_num = re.search(r'\d+', i.get('data-catalogercod1s'))
            arts_dict[art_num[0]] = i.find('a')['href']
        for art, url in arts_dict.items():
                if not sql_table.table_check_presence(art):
                    handbag = bag.Bag()
                    handbag.get_bag_page(art, url, debug, timeout)
                    sql_table.table_append(handbag)
        sql_table.cnx.commit()

        # 2nd page and further
        for i in range(2, pages + 1):
            if "page" in start_page:
                break
            param = "&" if "?" in start_page else "?"
            page = f"{str.rstrip(start_page)}{param}page={str(i)}"
            print(page)
            further_page = html_page.HtmlPage(page)
            arts_dict = further_page.get_wb_page()
            if arts_dict:
                for art, url in arts_dict.items():
                    if not sql_table.table_check_presence(art):
                        handbag = bag.Bag()
                        handbag.get_bag_page(art, url, debug, timeout)
                        sql_table.table_append(handbag)
                sql_table.cnx.commit()
            else:
                sql_table.cnx.commit()
                print(f"Page {str(i)} parse error. Next page.")


def push_and_pull(start_page, pages, debug, timeout, sql_table):
    param = "&" if "?" in start_page else "?"
    push_page_name = f"{str.rstrip(start_page)}{param}sort=priceup"
    parse_pages(push_page_name, 100, debug, timeout, sql_table)
    pull_page_name = f"{str.rstrip(start_page)}{param}sort=pricedown"
    parse_pages(pull_page_name, pages - 100, debug, timeout, sql_table)


if __name__ == '__main__':
    cred_tuple = read_config()

    parser = argparse.ArgumentParser()
    parser.add_argument("database", help="База данных для заполнения")
    parser.add_argument("source", help="URL страницы, откуда начинать")
    parser.add_argument("-c", "--clean", action="store_true", help="Очистить базу данных")
    parser.add_argument("-d", "--debug", action="store_true", help="Расширенный вывод")
    parser.add_argument("-u", "--update", action="store_true", help="Обновить базу http прокси")
    parser.add_argument("-s", "--https", action="store_true", help="Использовать и https прокси")
    parser.add_argument("-m", "--material", action="store_true", help="Заполнить недостающие материалы")
    args = parser.parse_args()

    mysql_table = table.Table(args.database, cred_tuple)
    table_exist = mysql_table.table_check()
    if table_exist:
        if args.clean:
            mysql_table.table_truncate()
    else:
        mysql_table.table_make()

    url = f'http://hidemyna.me/ru/api/proxylist.php?code={cred_tuple[5]}&maxtime=1000&type=h&out=plain'
    urls = f'http://hidemyna.me/ru/api/proxylist.php?code={cred_tuple[5]}&maxtime=1000&type=s&out=plain'

    if args.update or args.https:
        clear_table = True
        h = proxy.Proxy('http', url)
        s = proxy.Proxy('https', urls)
        len_table = h.form_table(clear_table)
        if args.https:
            print(f"В базе {len_table} прокси.")
            clear_table = False
            time.sleep(60)
            len_table += s.form_table(clear_table)
        print(f"В базе {len_table} прокси.")

    main_page = html_page.HtmlPage(args.source)
    main_html = main_page.get_html()

    if main_html and not args.material:
        if "page" in args.source:
            parse_pages(args.source, 1, args.debug, cred_tuple[4], mysql_table)
        else:
            main_soup = BeautifulSoup(main_html, 'html.parser')
            items = main_soup.find('span', class_="total many").find('span').text
            print(f"{items} товаров")
            pages = int(int(items) / 100)
            if int(items) % 100 != 0:
                pages += 1
            if pages > 200:
                pages = 200
            print(f"{str(pages)} страниц")
            if 100 < pages <= 200:
                push_and_pull(args.source, pages, args.debug, cred_tuple[4], mysql_table)
            if pages <= 100:
                parse_pages(args.source, pages, args.debug, cred_tuple[4], mysql_table)

    check_list = mysql_table.table_check_material()
    have_a_try = 3
    while len(check_list) and have_a_try:
        print(f"Пустых {len(check_list)} материалов. Заполняем...")
        for index in check_list:
            secs = int(random.random() * int(cred_tuple[4]))
            time.sleep(secs)
            empty_math_page = html_page.HtmlPage(f"https://www.wildberries.ru/catalog/{index[1]}/detail.aspx")
            text = empty_math_page.get_html()
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
