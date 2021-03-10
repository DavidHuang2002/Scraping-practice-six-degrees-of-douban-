import requests
from bs4 import BeautifulSoup
from queue import Queue
from time import sleep
import pymysql

''' 
Outline
- Getting the page
Pick one proxy from the proxy pool
Use the proxy to get_page (sleep 5s according to the rule in robots.txt)

- Extracting info
Pick out the title
Pick out the hot comments' user names
Get the 10 links in the recommendation section
! remember exception handling

- Crawl around
If the pages that the link links to has not been visited, enqueue the link
(Use recursion)

- Storing the info into MySQL
page url, title, whether visited into a table
link from one page to another into a table
user names into a table
! remember to check if it already exists before storing

- Saving and resuming
no special action required in saving 
to resume, go to pages whose visited is False, crawl from there

'''


# if the table is empty, given a start page and start crawling
# if not, get the unvisited pages in the table, enqueue them into links, return links
def resume(cur):
    start_page = 'https://movie.douban.com/subject/34841067/'
    links = Queue(0)
    # TODO
    return links


def get_page(url):
    # TODO
    # if exception, return None
    page = ''
    return page


def extract_data(page):
    # exception handling - if not exist then the field = None
    # title
    # user names
    # list of recommendations
    return {}


def enqueue_new_urls(cur, queue, new_page_ids):
    # use id to check if visited, if not then enqueue
    return queue


def store_and_enqueue(cur, data, queue: Queue):
    # if any of these are None, do nothing for that particular data
    # if the page url already exist, access and update title, if not add url, & title to table, set the visited to True
    # get the id of the current page(where title belongs to)

    # add all the recommendations link to the page table if they are not already in, store the id of them in a list
    # add all recommendations with the from_page_id = current_page_id, to page_id = to_page_ids[index]

    # add all user names to table

    return queue


def iterative_crawl(cur, queue: Queue, n):
    for i in range(n):
        page_url = queue.get()
        page = get_page(page_url)
        if page is None:
            recursive_crawl(cur, queue)
            continue
        data = extract_data()
        queue = store_and_enqueue(cur, data, queue)


# a recursive way for crawling
def recursive_crawl(cur, queue: Queue):
    page_url = queue.get()
    page = get_page(page_url)
    if page is None:
        recursive_crawl(cur, queue)
        return
    data = extract_data()
    queue = store_and_enqueue(cur, data, queue)
    recursive_crawl(cur, queue)


#
def main():
    conn = pymysql.connect(host='localhost',
                           unix_socket='/tmp/mysql.sock',
                           user='root',
                           password='david2002',
                           database='mysql',
                           cursorclass=pymysql.cursors.DictCursor)
    with conn:
        with conn.cursor() as cur:
            links = resume(cur)

