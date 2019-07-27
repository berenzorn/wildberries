import re
import time
import random
from html_page import HtmlPage
from bs4 import BeautifulSoup


class Bag:

    def __init__(self, article=0, name="", image="", url="", material="",
                 price=0, price_sale=0, rating=0, reviews=0, sold=0):
        self.article = article
        self.name = name
        self.image = image
        self.url = url
        self.material = material
        self.price = price
        self.price_sale = price_sale
        self.rating = rating
        self.reviews = reviews
        self.sold = sold

    def set_article(self, article):
        self.article = article

    def set_name(self, soup):
        field = soup.find('meta', itemprop="name")['content']
        name = re.findall(r'[А-Яа-яA-Za-z]+', field)
        self.name = " ".join(name)

    def set_image(self, soup):
        image = soup.find('meta', itemprop="image")['content']
        if image.startswith('//'):
            image = 'https:' + image
        self.image = image

    def set_url(self, url):
        self.url = url.split('?')[0]

    def set_material(self, soup, debug):
        try:
            field = soup.find('p', class_='composition').text.strip()
            material = [x for x in field.split("   ")]
            self.material = material[-1].strip()
        except AttributeError:
            if debug:
                print("Can't find material.")
            self.material = "---"

    def set_price(self, soup, page):
        try:
            price = soup.find('del', class_="c-text-base").text
            price = re.sub('\\xa0', '', price)[:-1]
            self.price = (int(price))
        except AttributeError:
            price = re.search(r"\Dprice\D\S\d+", page)
            try:
                self.price = (int(price.group(0).split(':')[1]))
            except IndexError:
                self.price = 0

    def set_price_sale(self, soup, page):
        try:
            price_sale = soup.find('span', class_="add-discount-text-price j-final-saving").text
            price_sale = re.sub('\\xa0', '', price_sale)[:-1]
            self.price_sale = (int(price_sale))
        except AttributeError:
            try:
                price_sale = int(soup.find('meta', itemprop='price')['content'].split('.')[0])
                self.price_sale = price_sale
            except TypeError:
                price_sale = re.search(r"\DpriceWithSale\D\S\d+", page)
                try:
                    self.price_sale = (int(price_sale.group(0).split(':')[1]))
                except IndexError:
                    self.price_sale = 0

    def set_rating(self, soup):
        try:
            self.rating = soup.find('meta', itemprop="ratingValue")['content']
        except TypeError:
            self.rating = 0

    def set_reviews(self, soup):
        try:
            self.reviews = soup.find('meta', itemprop="reviewCount")['content']
        except TypeError:
            self.reviews = 0

    def set_sold(self, page):
        orders = re.search(r"\DordersCount\D\S\d+", page)
        try:
            self.sold = (int(orders.group(0).split(':')[1]))
        except IndexError:
            self.sold = 0

    def set_bag_fields(self, article, url, debug, creds, proxy_pass):
        h = HtmlPage(url)
        page = h.get_html(creds, proxy_pass)
        if page:
            soup = BeautifulSoup(page, 'html.parser')
            self.set_article(article)
            self.set_name(soup)
            self.set_image(soup)
            self.set_url(url)
            self.set_material(soup, debug)
            self.set_price(soup, page)
            self.set_price_sale(soup, page)
            self.set_rating(soup)
            self.set_reviews(soup)
            self.set_sold(page)
        return False

    def get_bag_page(self, article, url, debug, creds, proxy_pass):
        self.set_bag_fields(article, url, debug, creds, proxy_pass)
        timeout = round(random.random() * int(creds[4]), 1)
        if debug:
            print(url)
            print(f"Таймаут {timeout} сек")
        time.sleep(timeout)
