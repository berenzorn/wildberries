import re
from bag import Bag
import table
from html_page import HtmlPage
from bs4 import BeautifulSoup
from configparser import ConfigParser

# https://hidemyname.org/ru/proxy-list/?country=FRITRUUAUS&maxtime=1000&type=s#list
proxy_number = 667
user_agent_number = 7345


def read_config():
    config = ConfigParser()
    config.read('config.ini')
    mysql_user = config.get('mysql', 'mysql_user')
    mysql_pass = config.get('mysql', 'mysql_pass')
    mysql_host = config.get('mysql', 'mysql_host')
    mysql_base = config.get('mysql', 'mysql_base')
    timeout = config.get('params', 'timeout_between_urls')
    return mysql_user, mysql_pass, mysql_host, mysql_base, timeout


if __name__ == '__main__':
    cred_tuple = read_config()

    name_table = input("Какую базу заполняем?: ")
    mysql_table = table.Table(name_table, cred_tuple)
    mysql_table.table_check()

    quiet = input("Нужен расширенный вывод? (y/n): ")
    quiet_output = False if quiet in 'Yy' else True

    # Example
    # https://www.wildberries.ru/catalog/aksessuary/sumki-i-ryukzaki/sumki/sumki-meshki
    wb_start_page = input("Откуда начинать? (URL страницы): ")
    first_page = HtmlPage(wb_start_page)
    main_html = first_page.get_html()

    if main_html:
        soup = BeautifulSoup(main_html, 'html.parser')
        items = soup.find('span', class_="total many").find('span').text
        print(f"{items} товаров")
        pages = int(int(items) / 100 + 1)
        print(f"{str(pages)} страниц")

        # 1st page
        arts_dict = {}
        print(wb_start_page)
        for i in soup.findAll('div', class_="dtList i-dtList"):
            art_num = re.search(r'\d+', i.get('data-catalogercod1s'))
            arts_dict[art_num[0]] = i.find('a')['href']
        for art, url in arts_dict.items():
            handbag = Bag()
            handbag.get_bag_page(art, url, quiet_output, cred_tuple[4])
            mysql_table.table_append(handbag)
        mysql_table.cnx.commit()

        # 2nd page and further
        for i in range(2, pages + 1):
            if "page" in wb_start_page:
                break
            if "?" not in wb_start_page:
                page = str.rstrip(wb_start_page) + "?page=" + str(i)
            else:
                page = str.rstrip(wb_start_page) + "&page=" + str(i)
            print(page)
            further_page = HtmlPage(page)
            arts_dict = further_page.get_wb_page()
            if arts_dict:
                for art, url in arts_dict.items():
                    handbag = Bag()
                    handbag.get_bag_page(art, url, quiet_output, cred_tuple[4])
                    mysql_table.cnx.commit()
            else:
                mysql_table.cnx.commit()
                print("Network error.")

    mysql_table.end_table_connect()

