import requests
from bs4 import BeautifulSoup
import concurrent.futures
import json
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
        self.proxies_websites = {
            '7yip': 'https://www.7yip.cn/free/?action=china&page={page_num}',
        }

        # stores methods for extracting proxies from each supported website
        self.extraction_methods = {
            '7yip': self.extract_from_7yip,
        }

    def get_proxies(self):
        page_num = 1
        while len(self.proxies) < 1:
            pages = {}
            # getting all the first pages from the proxy websites
            for site, url in self.proxies_websites.items():
                url = url.format(page_num=page_num)
                page = self.get_page(url)
                if page is not None:
                    print(url)
                    pages.update({site: page})

            # in case when all the proxy websites are down
            if len(pages) == 0:
                print('cannot access any proxies websites')
                return

            proxies_to_test = self.extract_all_proxies(pages)
            self.test_and_add_proxies(proxies_to_test)
            print(self.proxies)
            page_num += 1

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

    def extract_all_proxies(self, pages):
        proxies_to_test = []
        for site, page in pages.items():
            self.extraction_methods[site](page, proxies_to_test)
        return proxies_to_test

    @staticmethod
    def extract_from_7yip(page, proxies_to_test):
        bs = BeautifulSoup(page, 'html.parser')
        rows = bs.find_all('tr')
        for row in rows:
            anonymity_cell = row.find('td', {'data-title': '匿名度'})
            if anonymity_cell is not None \
                    and anonymity_cell.text == '高匿':
                if row.find('td', {'data-title': '类型'}).text == 'HTTPS':
                    proxy = 'http://' + row.find('td', {'data-title': 'IP'}).text + ':' \
                            + row.find('td', {'data-title': 'PORT'}).text
                    proxies_to_test.append(proxy)
        return proxies_to_test
        # failed code for extracting from 'http://www.goubanjia.com/' not working
        # anonymity_tds = bs.find_all('td', text='高匿')
        # for td in anonymity_tds:
        #     if td.find_next_sibling('td').text == 'https':
        #         self.proxies.append(td.parent.text)

    def test_and_add_proxies(self, proxies):
        print('running the threading on ', proxies)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(self.add_proxy, proxies)

    def add_proxy(self, proxy):
        if self.test_proxy(proxy):
            self.proxies.append(proxy)

    def test_proxy(self, proxy):
        test_url = 'https://httpbin.org/ip'
        page = self.get_page(test_url, proxy)
        if page is None:
            return False
        print(page)
        ip = json.loads(page)['origin']
        # the logic is pretty clumsy because I haven't found a usable non-anonymous proxy
        # so I am not sure how the site behaves in light of that.
        # TODO improve this after finding a usable non-anonymous proxy
        if type(ip) is not str:
            return False
        if ip.find('153.0.156.52') != -1:
            return False
        return True


a = Proxy()
# a.get_proxies()
b = a.test_proxy('http://190.144.127.234:3128')
print(b)
