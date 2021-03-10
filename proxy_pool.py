import requests
from bs4 import BeautifulSoup
from time import sleep

"""
overall logic
use a singleton class Proxy
has a method of getting the proxy from free proxy website and store them in a list
has a method of testing each proxy before using
can cycle through the proxies in random order

possible proxies website
https://www.7yip.cn/free/?action=china&page=1
"""

def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner


@singleton
class Proxy(object):
    def __init__(self):
        self.proxies = []

    @staticmethod
    def get_page(url, proxy=None):
        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
            'sec-ch-ua-mobile': '?0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        try:
            if proxy is None:
                page = requests.get(url, headers=headers)
            else:
                page = requests.get(url, headers=headers, proxies={'https': proxy})

            if page.status_code == 200:
                return page.text
            return None
        except Exception as e:
            print(str(e))
            return None

    def extract_proxies(self, page):
        bs = BeautifulSoup(page, 'html.parser')
        rows = bs.find_all('tr')
        for row in rows:
            anonymity_cell = row.find('td', {'data-title': '匿名度'})
            if anonymity_cell is not None\
                    and anonymity_cell.text == '高匿':
                if row.find('td', {'data-title': '类型'}).text == 'HTTPS':
                    proxy = 'https://' + row.find('td', {'data-title': 'IP'}).text + ':'\
                            + row.find('td', {'data-title': 'PORT'}).text
                    print(proxy)
                    if self.test_proxy(proxy):
                        self.proxies.append(proxy)


        # code for extracting from 'http://www.goubanjia.com/' not working
        # anonymity_tds = bs.find_all('td', text='高匿')
        # for td in anonymity_tds:
        #     if td.find_next_sibling('td').text == 'https':
        #         self.proxies.append(td.parent.text)

    def test_proxy(self, proxy):
        test_url = 'https://www.douban.com/'
        page = self.get_page(test_url, proxy)
        if page is None:
            return False
        print(page)
        return True


    def get_proxies(self):
        page_num = 1
        while len(self.proxies) < 1:
            proxies_website = 'https://www.7yip.cn/free/?action=china&page=1'
            page = self.get_page(proxies_website)
            if page is None:
                break
            self.extract_proxies(page)
            page_num += 1
            sleep(1)


a = Proxy()
a.get_proxies()
# b = a.test_proxy('http://119.122.212.23:9000')
# for i, proxy in enumerate(a.proxies):
#     print(a.test_proxy(proxy))
