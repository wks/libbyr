# coding: UTF-8

import os, sys, re, urllib2, httplib

forum_host = 'bbs.byr.cn'

def make_connection():
    return httplib.HTTPConnection(forum_host)

def load_board_page(board_name, page_num=1, connection=None):
    url = 'http://bbs.byr.cn/board/%(board_name)s?p=%(page_num)s' % locals()
    return load_page(url, connection)

def load_thread_page(board_name, thread_id, page_num=1, connection=None):
    url = 'http://bbs.byr.cn/article/%(board_name)s/%(thread_id)s?p=%(page_num)s' % locals()
    return load_page(url, connection)

def load_page(url, connection=None):
    if connection == None:
        connection = make_connection()
    connection.request("GET", url)
    resp = connection.getresponse()
    return resp.read().decode("gb18030")

def board_get_thread_list(board_html):
    pat = re.compile(ur'<td class="title_9"><a href="/article/\w+/(?P<thread_id>\d+)">')
    return map(int, pat.findall(board_html))

def get_max_page_num(html):
    pat = re.compile(ur'<li class="page-normal"><a href="\?p=(?P<page_num>\d+)" title="[^"]+">\d+</a></li>')
    lst = pat.findall(html);

    if len(lst)==0:
        return 1
    else:
        return max(map(int,lst))

def fetch_whole_thread(board_name, thread_id):
    conn = make_connection()

    first_page = load_thread_page(board_name,thread_id,connection=conn)
    last_page_num = get_max_page_num(first_page)

    yield first_page

    for page_num in xrange(2,last_page_num+1):
        page = load_thread_page(board_name,thread_id,page_num, connection=conn)
        yield page

    conn.close()

def thread_page_get_posts(thread_html):
    pat = re.compile(
            ur'<td class="posts_content_right no_bottom no_top"><p>'
            ur'发信人: (?P<username>\w+) \((?P<nickname>.+?)\), '
            ur'信区: (?P<board>\w+) <br /> '
            ur'标&nbsp;&nbsp;题: (?P<title>.+?) '
            ur'<br /> '
            ur'发信站: 北邮人论坛 '
            ur'\((?P<date>.+?)\)'
            ur', '
            ur'站内 <br />'
            ur'&nbsp;&nbsp;<br /> '
            ur'(?P<content>.+?)'
            ur'<font class="f\d+"></font><font class="f\d+">'
            ur'※ 来源:·北邮人论坛 (<a target="_blank" href="http://bbs.byr.cn">http://)?bbs\.byr\.cn(</a>)?·'
            ur'\[FROM: (?P<source_ipaddr>[0-9.*]+)\]'
            ur'</font>'
            ur'<font class="f000"> <br /> </font></p></td>'
            )
    
    for m in pat.finditer(thread_html):
        d = m.groupdict()
        yield d


def fetch_all_posts_in_whole_thread(board_name, thread_id):
    for page in fetch_whole_thread(board_name, thread_id):
        for d in thread_page_get_posts(page):
            yield d

def test_match_all(board_name, thread_id):
    mp = get_max_page_num(board_name)
    for i,page in enumerate(fetch_whole_thread(board_name, thread_id)):
        pn = i+1
        if pn < mp:
            posts = thread_page_get_posts(page)
            sz = len(posts)
            if sz<10:
                print "wrong number: board_name=%(board_name)s thread_id=%(thread_id)s page=%(pn)s"%locals()

def escape_content(content):
    tag_pat = re.compile(ur'<.+?>')
    content = content.replace(u"<br />",u"\n").replace(u'&nbsp;',u' ')
    content = tag_pat.sub('',content)

    return content
