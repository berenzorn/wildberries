import re
import random
import requests
import proxy_list
import user_agent_list
from bs4 import BeautifulSoup

proxy_number = 667
user_agent_number = 7345


class HtmlPage:

    def __init__(self, url):
        self.url = url

    def get_html(self):
        have_a_try = 3
        while have_a_try:
            user_agent = user_agent_list.get_user_agent(int(random.random() * user_agent_number))
            user_agent_dict = {'user-agent': user_agent}
            proxy = proxy_list.get_proxy(int(random.random() * proxy_number))
            proxy_dict = {'http': proxy}
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
