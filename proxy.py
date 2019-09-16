import random
import table
import requests
import crawler


class Proxy:

    def __init__(self, proto, url):
        self.proto = proto
        self.url = url

    def proxy_download(self):
        try:
            result = requests.get(str.rstrip(self.url))
            result.raise_for_status()
            return result.text
        except requests.RequestException:
            return False

    def form_table(self, clear):
        t = table.Table('proxy_list', crawler.read_config())
        t.table_check()
        if clear:
            t.table_truncate()

        http_list = self.proxy_download().split('\r')
        if http_list:
            table_list = [f'{self.proto}://{str.lstrip(i)}' for i in http_list]
            table_list.pop()
            http_list.clear()
            for i in table_list:
                t.proxy_append(self.proto, i)
            return len(table_list)
        return False

    @staticmethod
    def read_table_string(list_len):
        tbl = table.Table('proxy_list', crawler.read_config())
        number = int(random.random() * list_len)
        return tbl.table_read(number)
