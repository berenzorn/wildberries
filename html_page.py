import re
import random
import requests
import table
import user_agent_list
from bs4 import BeautifulSoup
from crawler import read_config


class HtmlPage:

    user_agent_number = 7345

    def __init__(self, url):
        self.url = url

    def get_html(self):
        have_a_try = 3
        creds = read_config()
        while have_a_try:
            t = table.Table('proxy_list', creds=creds)
            user_agent = user_agent_list.get_user_agent(int(random.random() * self.user_agent_number))
            user_agent_dict = {'user-agent': user_agent}
            table_exist = t.table_check()
            if not table_exist:
                print("Proxy table corrupted.")
                return False
            tab_length = t.table_len()
            try:
                proxy = t.table_read(int(random.random() * (tab_length[0] - 1)) + 1)
                proxy_dict = {proxy[1]: proxy[2]}
            except TypeError:
                print("Fatal error. Smth bad in proxy list.")
                return False
            try:
                result = requests.get(str.rstrip(self.url), headers=user_agent_dict, proxies=proxy_dict)
                result.raise_for_status()
                return result.text
            except(requests.RequestException, ValueError):
                print("Bad proxy. One more try.")
                have_a_try -= 1
        print("Network error. Update proxy list.")
        return False

    def get_wb_page(self):
        html = self.get_html()
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            articles = {}
            for index in soup.findAll('div', class_="dtList i-dtList"):
                article_number = re.search(r'\d+', index.get('data-catalogercod1s'))
                articles[article_number[0]] = index.find('a')['href']
            return articles
        return False
