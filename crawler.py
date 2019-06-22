import re
import time
import bag
import table
import proxy
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


def parse_pages(start_page, pages, quiet_output, timeout, mysql_table):

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
                if not mysql_table.table_check_presence(art):
                    handbag = bag.Bag()
                    handbag.get_bag_page(art, url, quiet_output, timeout)
                    mysql_table.table_append(handbag)
        mysql_table.cnx.commit()

        # 2nd page and further
        for i in range(2, pages + 1):
            if "page" in start_page:
                break
            if "?" not in start_page:
                page = f"{str.rstrip(start_page)}?page={str(i)}"
            else:
                page = f"{str.rstrip(start_page)}&page={str(i)}"
            print(page)
            further_page = html_page.HtmlPage(page)
            arts_dict = further_page.get_wb_page()
            if arts_dict:
                for art, url in arts_dict.items():
                    if not mysql_table.table_check_presence(art):
                        handbag = bag.Bag()
                        handbag.get_bag_page(art, url, quiet_output, timeout)
                        mysql_table.table_append(handbag)
                mysql_table.cnx.commit()
            else:
                mysql_table.cnx.commit()
                print("Network error.")


def push_and_pull(start_page, pages, quiet_output, timeout, mysql_table):
    push_page_name = str.rstrip(start_page) + "?sort=priceup"
    parse_pages(push_page_name, pages, quiet_output, timeout, mysql_table)
    pull_page_name = str.rstrip(start_page) + "?sort=pricedown"
    parse_pages(pull_page_name, pages, quiet_output, timeout, mysql_table)


if __name__ == '__main__':
    cred_tuple = read_config()

    name_table = input("Какую базу заполняем?: ")
    mysql_table = table.Table(name_table, cred_tuple)
    table_exist = mysql_table.table_check()
    if table_exist:
        table_clean = input("Таблица существует. Очистить? (y/n): ")
        if table_clean in 'Yy':
            mysql_table.table_truncate()
    else:
        mysql_table.table_make()

    quiet_ask = input("Нужен расширенный вывод? (y/n): ")
    quiet_output = False if quiet_ask in 'Yy' else True
    timeout = cred_tuple[4]

    # Example
    # https://www.wildberries.ru/catalog/aksessuary/sumki-i-ryukzaki/sumki/sumki-meshki
    wb_start_page = input("Откуда начинать? (URL страницы): ")

    url = f'http://hidemyna.me/ru/api/proxylist.php?code={cred_tuple[5]}&maxtime=1000&type=h&out=plain'
    urls = f'http://hidemyna.me/ru/api/proxylist.php?code={cred_tuple[5]}&maxtime=1000&type=s&out=plain'

    proxy_table = input("Обновить базу прокси? (y/n): ")
    if proxy_table in 'Yy':
        clear_table = True

        h = proxy.Proxy('http', url)
        s = proxy.Proxy('https', urls)

        len_table = h.form_table(clear_table)
        print(f"В базе {len_table} прокси.")
        delay = input("Сливаем https лист? Пауза 60 сек. (y/n): ")
        if delay in 'Yy':
            clear_table = False
            time.sleep(60)
            len_table += s.form_table(clear_table)
            print(f"В базе {len_table} прокси.")

    main_page = html_page.HtmlPage(wb_start_page)
    main_html = main_page.get_html()

    if main_html:
        main_soup = BeautifulSoup(main_html, 'html.parser')
        items = main_soup.find('span', class_="total many").find('span').text
        print(f"{items} товаров")
        pages = int(int(items) / 100 + 1)
        if pages > 200:
            pages = 200
        print(f"{str(pages)} страниц")
        if 100 < pages <= 200:
            push_and_pull(wb_start_page, pages, quiet_output, timeout, mysql_table)
        if pages <= 100:
            parse_pages(wb_start_page, pages, quiet_output, timeout, mysql_table)

    mysql_table.end_table_connect()
