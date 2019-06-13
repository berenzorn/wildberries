import re
import time
import table
import random
import requests
import proxy_list
import mysql.connector
import user_agent_list
from bs4 import BeautifulSoup
from configparser import ConfigParser


# https://hidemyname.org/ru/proxy-list/?country=FRITRUUAUS&maxtime=1000&type=s#list
proxy_number = 665
user_agent_number = 7360


def read_config():
    config = ConfigParser()
    config.read('config.ini')
    mysql_user = config.get('mysql', 'mysql_user')
    mysql_pass = config.get('mysql', 'mysql_pass')
    mysql_host = config.get('mysql', 'mysql_host')
    mysql_base = config.get('mysql', 'mysql_base')
    timeout = config.get('params', 'timeout_between_urls')
    return mysql_user, mysql_pass, mysql_host, mysql_base, timeout


def get_html(html):
    """
    Read and returns big 100-bag html with random user agent and proxy from .py modules
    :param html: big html url
    :return: big html in text
    """
    have_a_try = 3
    while have_a_try:
        user_agent = user_agent_list.get_user_agent(int(random.random() * user_agent_number))
        user_agent_dict = {'user-agent': user_agent}
        proxy = proxy_list.get_proxy(int(random.random() * proxy_number))
        proxy_dict = {'https': proxy}
        try:
            result = requests.get(str.rstrip(html), headers=user_agent_dict, proxies=proxy_dict)
            result.raise_for_status()
            return result.text
        except(requests.RequestException, ValueError):
            print("Bad proxy. One more try.")
            have_a_try -= 1
    return False


def get_wb_page(page):
    """
    Read big 100-bag html and form dict with 100 little bag pages {article : url}
    :param page: big 100-bag html
    :return: dict {article : url}
    """
    html = get_html(page)
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        articles = {}
        for index in soup.findAll('div', class_="dtList i-dtList"):
            article_number = re.search(r'\d+', index.get('data-catalogercod1s'))
            articles[article_number[0]] = index.find('a')['href']
        return articles
    return False


def get_bag_page(article, url):
    """
    Form list for insert sql query. Query format:
    article, name, image, url, price, price_sale, rating, review, sold, timestamp
    :param article: article number
    :param url: little bag page from get_wb_page dict
    :return:
    """
    bag_html = get_html(url)

    if bag_html:
        # article
        insert_array = [str(article)]
        bag_soup = BeautifulSoup(bag_html, 'html.parser')
        # name
        name_field = bag_soup.find('meta', itemprop="name")['content']
        name = re.findall(r'[А-Яа-яA-Za-z]+', name_field)
        insert_array.append(" ".join(name))
        # image
        image = bag_soup.find('meta', itemprop="image")['content']
        if image.startswith('//'):
            image = 'https:' + image
        insert_array.append(image)
        # url
        insert_array.append(url.split('?')[0])
        # price
        bag_price = re.search(r"\Dprice\D\S\d+", bag_html)
        insert_array.append(int(bag_price.group(0).split(':')[1]))
        # sale_price
        bag_sale_price = re.search(r"\DpriceWithSale\D\S\d+", bag_html)
        insert_array.append(int(bag_sale_price.group(0).split(':')[1]))
        # rating
        try:
            rating = bag_soup.find('meta', itemprop="ratingValue")['content']
        except TypeError:
            rating = 0
        insert_array.append(rating)
        # reviews
        try:
            reviews = bag_soup.find('meta', itemprop="reviewCount")['content']
        except TypeError:
            reviews = 0
        insert_array.append(reviews)
        # sold
        bag_order_count = re.search(r"\DordersCount\D\S\d+", bag_html)
        insert_array.append(int(bag_order_count.group(0).split(':')[1]))
        # timestamp
        insert_array.append(int(time.time()))

        mysql_table.table_append(name_table, insert_array)
    return False


def get_bag_page_with_timeout(article, url, quiet):
    if not quiet:
        print(url)
    get_bag_page(article, url)
    timeout = int(random.random() * int(cred_tuple[4]))
    if not quiet:
        print(f"Таймаут {timeout} сек")
    time.sleep(timeout)


# TODO: proxy list daily former
# TODO: add material into table


if __name__ == '__main__':
    cred_tuple = read_config()

    name_table = input("Какую базу заполняем?: ")
    mysql_table = table.Table(name_table, cred_tuple)

    quiet = input("Нужен расширенный вывод? (y/n): ")
    quiet_output = False if quiet in 'Yy' else True

    mysql_table.cursor.execute("USE sys;")

    try:
        execute = f"SELECT * FROM {name_table};"
        mysql_table.cursor.execute(execute)
    except mysql.connector.errors.ProgrammingError:
        mysql_table.table_make(name_table)

    # Example
    # https://www.wildberries.ru/catalog/aksessuary/sumki-i-ryukzaki/sumki/sumki-meshki
    wb_start_page = input("Откуда начинать? (URL страницы): ")

    main_html = get_html(wb_start_page)
    if main_html:
        soup = BeautifulSoup(main_html, 'html.parser')
        items = soup.find('span', class_="total many").find('span').text
        print(f"{items} товаров")
        pages = int(int(items) / 100 + 1)
        print(f"{str(pages)} страниц")

        # 1st page
        # = start page
        arts_dict = {}
        print(wb_start_page)
        for i in soup.findAll('div', class_="dtList i-dtList"):
            art_num = re.search(r'\d+', i.get('data-catalogercod1s'))
            arts_dict[art_num[0]] = i.find('a')['href']
        for art, url in arts_dict.items():
            get_bag_page_with_timeout(art, url, quiet_output)

        mysql_table.cnx.commit()

        # 2nd page and further
        # https://www.wildberries.ru/catalog/aksessuary/sumki-i-ryukzaki/sumki/sumki-meshki?page=X
        for i in range(2, pages + 1):
            further_page = str.rstrip(wb_start_page) + "?page=" + str(i)
            print(further_page)
            arts_dict = get_wb_page(further_page)
            if arts_dict:
                for art, url in arts_dict.items():
                    get_bag_page_with_timeout(art, url, quiet_output)
                    mysql_table.cnx.commit()
            else:
                mysql_table.cnx.commit()
                print("Network error.")

    mysql_table.end_table_connect()

