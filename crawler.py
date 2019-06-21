import re
from bag import Bag
import table
from html_page import HtmlPage
from bs4 import BeautifulSoup
from configparser import ConfigParser

# https://hidemyname.org/ru/proxy-list/?country=FRITRUUAUS&code=940706186043098&maxtime=1000&type=h&out=js
# http://hidemyna.me/ru/api/proxylist.php?code=940706186043098&maxtime=1000&type=h&out=js
proxy_number = 667
user_agent_number = 7345


def read_config():
    config = ConfigParser()
    config.read('config.ini')
    mysql_user = config.get('mysql', 'mysql_user')
    mysql_pass = config.get('mysql', 'mysql_pass')
    mysql_host = config.get('mysql', 'mysql_host')
    mysql_base = config.get('mysql', 'mysql_base')
    time_secs = config.get('params', 'timeout_between_urls')
    return mysql_user, mysql_pass, mysql_host, mysql_base, time_secs


def parse_pages(wb_start_page):

    first_page = HtmlPage(wb_start_page)
    html = first_page.get_html()

    if html:
        soup = BeautifulSoup(html, 'html.parser')

        # 1st page
        arts_dict = {}
        print(wb_start_page)
        for i in soup.findAll('div', class_="dtList i-dtList"):
            art_num = re.search(r'\d+', i.get('data-catalogercod1s'))
            arts_dict[art_num[0]] = i.find('a')['href']
        for art, url in arts_dict.items():
            if not mysql_table.table_check_presence(art):
                handbag = Bag()
                handbag.get_bag_page(art, url, quiet_output, timeout)
                mysql_table.table_append(handbag)
        mysql_table.cnx.commit()

        # 2nd page and further
        for i in range(2, pages + 1):
            if "page" in wb_start_page:
                break
            if "?" not in wb_start_page:
                page = f"{str.rstrip(wb_start_page)}?page={str(i)}"
            else:
                page = f"{str.rstrip(wb_start_page)}&page={str(i)}"
            print(page)
            further_page = HtmlPage(page)
            arts_dict = further_page.get_wb_page()
            if arts_dict:
                for art, url in arts_dict.items():
                    if not mysql_table.table_check_presence(art):
                        handbag = Bag()
                        handbag.get_bag_page(art, url, quiet_output, timeout)
                        mysql_table.table_append(handbag)
                mysql_table.cnx.commit()
            else:
                mysql_table.cnx.commit()
                print("Network error.")


def push_and_pull(wb_start_page):
    push_page_name = str.rstrip(wb_start_page) + "?sort=priceup"
    parse_pages(push_page_name)
    pull_page_name = str.rstrip(wb_start_page) + "?sort=pricedown"
    parse_pages(pull_page_name)


if __name__ == '__main__':
    cred_tuple = read_config()

    name_table = input("Какую базу заполняем?: ")
    mysql_table = table.Table(name_table, cred_tuple)
    mysql_table.table_check()

    quiet_ask = input("Нужен расширенный вывод? (y/n): ")
    quiet_output = False if quiet_ask in 'Yy' else True
    timeout = cred_tuple[4]

    # Example
    # https://www.wildberries.ru/catalog/aksessuary/sumki-i-ryukzaki/sumki/sumki-meshki
    wb_start_page = input("Откуда начинать? (URL страницы): ")
    main_page = HtmlPage(wb_start_page)
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
            push_and_pull(wb_start_page)
        if pages <= 100:
            parse_pages(wb_start_page)

    mysql_table.end_table_connect()
