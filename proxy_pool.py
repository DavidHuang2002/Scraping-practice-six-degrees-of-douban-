import requests
from bs4 import BeautifulSoup
import concurrent.futures
import json
import re
import chardet
import time
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
    def __init__(self, desired_proxies_num=5, crawl_delay=5):
        self.proxies = []
        self.proxies_websites = {
            '7yip': 'https://www.7yip.cn/free/?action=china&page={page_num}',
            '66ip': 'http://www.66ip.cn/{page_num}.html',
            'ip3366': 'http://www.ip3366.net/?stype=1&page={page_num}',

        }

        # stores methods for extracting proxies from each supported website
        self.extraction_methods = {
            '7yip': self.extract_from_7yip,
            '66ip': self.extract_from_66ip,
            'ip3366': self.extract_from_ip3366,

        }

        self.desired_proxies_num = desired_proxies_num
        self.proxies_file = None
        self.counter = 0
        self.time_tracker = time.time()
        # the crawl delay for scraping the site in seconds
        self.crawl_delay = crawl_delay

    def get_proxies(self):
        self.get_proxies_from_file()
        self.get_proxies_from_web()

    def get_proxies_from_file(self):
        if self.proxies_file is None:
            print('the attribute self.proxies_file is not set, no file to extract. Skip get_proxies_from_file')
            return
        proxies_to_test = self.extract_proxies_from_file(self.proxies_file)
        self.test_and_add_proxies(proxies_to_test)
        print(self.proxies)


    def get_proxies_from_web(self):
        page_num = 1
        while len(self.proxies) < self.desired_proxies_num:
            pages = {}
            # getting all the first pages from the proxy websites
            for site, url in self.proxies_websites.items():
                # the first page of 66ip behaves a little differently, use this if statement to handle it
                if site == '66ip' and page_num == 1:
                    url = url.format(page_num='index')
                else:
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
            if page_num >= 5:
                print('there probably are no more working proxies')
                print('this is what we got so far', self.proxies)

    @staticmethod
    def extract_proxies_from_file(path, proxies_to_test=[]):
        try:
            with open(path, mode='r') as file:
                lines = file.readlines()
                for line in lines:
                    line = line.strip()
                    if re.match('^(.+):(.+)$', line):
                        proxies_to_test.append('http://'+line)
        except FileNotFoundError:
            print('!'*15)
            print('the proxies file designated is incorrect')
        return proxies_to_test

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
                # to accommodate for different character encoding used in chinese websites besides unicode
                page.encoding = chardet.detect(page.content)['encoding']
                return page.text
            return None
        except Exception as e:
            return None

    def extract_all_proxies(self, pages):
        proxies_to_test = []
        for site, page in pages.items():
            bs = BeautifulSoup(page, 'html.parser')
            try:
                self.extraction_methods[site](bs, proxies_to_test)
            except AttributeError as e:
                print('-' * 15)
                print('something is wrong with extraction method for', site, 'error message:')
                print(str(e))
        return proxies_to_test

    @staticmethod
    def extract_from_7yip(bs, proxies_to_test):
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

    # Does not work because there is something wrong with the character encoding but not sure where is wrong
    @staticmethod
    def extract_from_66ip(bs, proxies_to_test):
        anonymity_cells = bs.find_all('td', text='高匿代理')
        for anonymity_cell in anonymity_cells:
            previous_cells = anonymity_cell.find_previous_siblings('td')
            port = previous_cells[1].text
            ip = previous_cells[2].text
            proxy = 'http://'+ip+':'+port
            proxies_to_test.append(proxy)
        return proxies_to_test

    @staticmethod
    def extract_from_ip3366(bs, proxies_to_test):
        anonymity_cells = bs.find_all('td', text='高匿代理IP')
        for anonymity_cell in anonymity_cells:
            if anonymity_cell.find_next_sibling('td').text == 'HTTPS':
                port_cell = anonymity_cell.find_previous_sibling('td')
                ip_cell = port_cell.find_previous_sibling('td')
                proxy = 'http://' + ip_cell.text + ':' + port_cell.text
                proxies_to_test.append(proxy)
        return proxies_to_test

    def test_and_add_proxies(self, proxies):
        print('running the threading on ', proxies)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.add_proxy, proxies)

    def add_proxy(self, proxy):
        if len(self.proxies) >= self.desired_proxies_num:
            return
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

        # use regex to extract the proxy ip number only and compare against the origin
        if ip != re.search('http://(.*):(.*)', proxy).group(1):
            return False
        print(proxy)
        return True

    # Codes for getting proxies from the proxy pool
    def rotate_proxies(self):
        if len(self.proxies) == 0:
            raise Exception('All proxies are invalid. No more proxies available ')

        if self.counter >= len(self.proxies):
            self.counter = 0
            # make sure every proxy has waited at least a crawl delay
            time_diff = time.time() - self.time_tracker
            if time_diff < self.crawl_delay:
                time.sleep(self.crawl_delay - time_diff)
                self.time_tracker = time.time()

        proxy = self.proxies[self.counter]
        if self.test_proxy(proxy):
            self.counter += 1
            return proxy
        else:
            # when the proxy is invalid remove it from the list and keep rotating to get the next working proxy
            # TODO add a thread that finds a new proxy to add to the list
            self.proxies.remove(self.counter)
            return self.rotate_proxies()









a = Proxy()
a.proxies_file = './proxies_to_test.txt'
a.get_proxies()
print(a.proxies)
a.crawl_delay = 1
for i in range(20):
    proxy = a.rotate_proxies()
    print(i, ':', a.counter, proxy)


# # page = a.get_page('http://www.ip3366.net/?stype=1&page=1')
# # bs = BeautifulSoup(page, 'html.parser')
# # b = []
# # a.extract_from_ip3366(bs, b)
# # print(b)
# b = a.extract_proxies_from_file('./proxies_to_test.txt')
# print(b)
# print(len(b))