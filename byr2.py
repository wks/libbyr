# coding: utf_8

import os, sys, re, urllib2, httplib

class Byr(object):
    FORUM_HOST = 'bbs.byr.cn'
    FORUM_ENCODING = 'gb18030'

    def __init__(self):
        self._conn = None

    def make_connection(self):
        return httplib.HTTPConnection(self.FORUM_HOST)

    def reconnect(self):
        self._conn = self.make_connection()

    def get_connection(self):
        if self._conn is None:
            self._conn = self.make_connection()
        return self._conn

    conn = property(get_connection)

    def load_board_page(self, board_name, page_num=1):
        url = 'http://bbs.byr.cn/board/%(board_name)s?p=%(page_num)s' % locals()
        return self.load_page(url)

    def load_thread_page(self, board_name, thread_id, page_num=1):
        url = 'http://bbs.byr.cn/article/%(board_name)s/%(thread_id)s?p=%(page_num)s' % locals()
        return self.load_page(url)

    def load_page(self, url):
        while True:
            try:
                self.conn.request("GET", url)
                resp = self.conn.getresponse()
                return resp.read().decode(self.FORUM_ENCODING)
            except httplib.HTTPException:
                self.reconnect()

    @staticmethod
    def board_page_get_thread_list(board_html):
        pat = re.compile(ur'<td class="title_9"><a href="/article/\w+/(?P<thread_id>\d+)">')
        return map(int, pat.findall(board_html))

    @staticmethod
    def page_get_max_page_num(html):
        pat = re.compile(ur'<li class="page-normal"><a href="\?p=(?P<page_num>\d+)" title="[^"]+">\d+</a></li>')
        lst = pat.findall(html);

        if len(lst)==0:
            return 1
        else:
            return max(map(int,lst))

    def fetch_whole_thread(self, board_name, thread_id):
        first_page = self.load_thread_page(board_name,thread_id)
        last_page_num = self.get_max_page_num(first_page)

        yield first_page

        for page_num in xrange(2,last_page_num+1):
            page = self.load_thread_page(board_name,thread_id,page_num)
            yield page

    @staticmethod
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


    def fetch_all_posts_in_whole_thread(self, board_name, thread_id):
        for page in self.fetch_whole_thread(board_name, thread_id):
            for d in self.thread_page_get_posts(page):
                yield d

    def test_match_all(self, board_name, thread_id):
        mp = self.get_max_page_num(board_name)
        for i,page in enumerate(self.fetch_whole_thread(board_name, thread_id)):
            pn = i+1
            if pn < mp:
                posts = self.thread_page_get_posts(page)
                sz = len(posts)
                if sz<10:
                    print "wrong number: board_name=%(board_name)s thread_id=%(thread_id)s page=%(pn)s"%locals()

    @staticmethod
    def escape_content(content):
        tag_pat = re.compile(ur'<.+?>')
        content = content.replace(u"<br />",u"\n").replace(u'&nbsp;',u' ')
        content = tag_pat.sub('',content)

        return content

