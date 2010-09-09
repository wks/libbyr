import os, sys, re, urllib2, httplib

forum_host = 'bbs.byr.cn'
def make_connection():
    return httplib.HTTPConnection(forum_host)

def url_board(board_name, page_num=1):
    return 'http://bbs.byr.cn/board/%(board_name)s?p=%(page_num)s' % locals()

def url_thread(board_name, thread_id, page_num=1):
    return 'http://bbs.byr.cn/article/%(board_name)s/%(thread_id)s?p=%(page_num)s' % locals()

def load_page(url, connection=None):
    if connection == None:
        connection = make_connection()
    connection.request("GET", url)
    resp = connection.getresponse()
    return resp.read()

def board_get_thread_list(board_html):
    pat = re.compile(r'<td class="title_9"><a href="/article/\w+/(?P<thread_id>\d+)">')
    return pat.findall(board_html)

def get_max_page_num(html):
    pat = re.compile(r'<li class="page-normal"><a href="\?p=(?P<page_num>\d+)" title="[^"]+">\d+</a></li>')
    lst = pat.findall(html);

    if len(lst)==0:
        return 1
    else:
        return max(map(int,lst))

def fetch_whole_thread(board_name, thread_id):
    conn = make_connection()

    first_page = load_page(url_thread(board_name,thread_id),conn)
    last_page_num = get_max_page_num(first_page)

    yield first_page

    for page_num in xrange(2,last_page_num+1):
        page = load_page(url_thread(board_name,thread_id,page_num),conn)
        yield page

    conn.close()

