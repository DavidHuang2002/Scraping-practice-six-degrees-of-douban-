import requests
from bs4 import BeautifulSoup
from queue import Queue
from time import sleep


# IP got banned after scraping for a while. Maybe sleep(0.5) is not enough
# TODO
# rotate IP address and save progress to pick up


def get_page(url):
    try:
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
        req = requests.get(url, headers=headers)
    except requests.exceptions.RequestException:
        print('requesting url meet with an error')
        return None

    return BeautifulSoup(req.text, 'html.parser')


def get_film_name(page: BeautifulSoup):
    try:
        film_name = page.find('h1').text.replace('\n', '')
    except AttributeError as e:
        print('no title found')
        return None
    return film_name


def get_recommendations_urls(page: BeautifulSoup):
    try:
        link_tags = page.find(id='recommendations').find_all('a')
    except AttributeError as e:
        print('recommendation section not found')
        return None

    recommendations_urls = set()
    for tag in link_tags:
        recommendations_urls.add(tag.attrs['href'])
    return recommendations_urls


def record_progress(current_path):
    with open('record.txt', 'w') as outfile:
        outfile.write(current_path)


# TODO
# idea: add the url visited to a txt file each time visit a new url
# continually update a txt file to save the queue
visited = set()
queue = Queue(0)
def BFS(end_film):
    global visited
    global queue

    if queue.empty():
        print('does not exist a path to such film')
        return ''

    url, path = queue.get()
    current_page = get_page(url)
    if current_page is not None:
        name = get_film_name(current_page)
        print(name)
        if name is not None:
            path += name + '/'
            record_progress(path)
        else:
            path += url + '/'

        if name == end_film:
            print('Film found. Search ends')
            return path

        rec_urls = get_recommendations_urls(current_page)

        if rec_urls is not None:
            for url in rec_urls:
                if url not in visited:
                    visited.add(url)
                    queue.put((url, path))

        sleep(1)
        path = BFS(end_film)
        return path


# urls found by get_recommendations_urls() are in the form like
# https://movie.douban.com/subject/24733428/?from=subject-page
# therefore, for consistency, the start page should also include the query ?from=subject-page
start_page = 'https://movie.douban.com/subject/24733428/?from=subject-page'
visited.add(start_page)
queue.put((start_page, ''))

film_path = BFS('盗梦空间 Inception(2010)')
print(film_path)
