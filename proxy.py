import random
import time
import table
import requests
from crawler import cred_tuple


class Proxy:

    def __init__(self, proto, addr):
        self.proto = proto
        self.addr = addr

    @staticmethod
    def proxy_download(url):
        try:
            result = requests.get(str.rstrip(url))
            result.raise_for_status()
            return result.text
        except requests.RequestException:
            return False

    def form_table(self, clear):
        t = table.Table('proxy_list', cred_tuple)
        t.proxy_check()
        if clear:
            t.proxy_truncate()

        httplist = self.proxy_download(self.addr).split('\n')
        if httplist:
            tablelist = [f'{proto}://{i}' for i in httplist]
            httplist.clear()
            for i in tablelist:
                t.proxy_append(proto, i)
            return len(tablelist)
        return False

    def read_table_string(self, list_len):
        tbl = table.Table('proxy_list', cred_tuple)
        number = int(random.random() * list_len)
        return tbl.proxy_read(number)


# if __name__ == '__main__':
#     url = 'http://hidemyna.me/ru/api/proxylist.php?code=940706186043098&maxtime=1000&type=h&out=plain'
#     urls = 'http://hidemyna.me/ru/api/proxylist.php?code=940706186043098&maxtime=1000&type=s&out=plain'
#     clear_table = True
#
#     len_table = form_table('http', url, clear_table)
#     delay = input("Download 2nd list? Delay 60 sec. (y/n): ")
#     if delay in 'Yy':
#         clear_table = False
#         time.sleep(60)
#         len_table = form_table('https', urls, clear_table)
