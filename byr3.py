# coding: utf_8

import os, sys, re, urllib2, httplib, string, urlparse

PROXY_ADDR = os.environ.get('http_proxy',None)

class Byr(object):
    FORUM_HOST = 'bbs.byr.cn'
    FORUM_ENCODING = 'gb18030'
    if PROXY_ADDR is not None:
        CONN_ADDR = urlparse.urlparse(PROXY_ADDR).netloc
    else:
        CONN_ADDR = FORUM_HOST

    def __init__(self):
        self._conn = None

    def connect(self):
        self._conn = httplib.HTTPConnection(self.CONN_ADDR)

    @property
    def conn(self):
        if self._conn is None:
            self.connect()
        return self._conn 
    def load_page(self, url):
        while True:
            try:
                self.conn.request("GET", url)
                resp = self.conn.getresponse()
                # BYR forum does not always find the borders of multi-byte
                # chars correctly.  So "replace" is needed.
                # "ignore" also works.
                return resp.read().decode(self.FORUM_ENCODING, "replace") 
            except httplib.HTTPException:
                self.connect()

    def board(self, board_name):
        return Board(self, board_name)

    def thread(self, board_name, thread_id):
        return Thread(self, board_name, thread_id)

class PagedMixin(object):
    def page(self, page_num):
        return self._page_class()(self, page_num)

    def xpages(self):
        first_page = self.page(1)
        last_page_num = first_page.max_page_num()

        yield first_page

        for page_num in xrange(2,last_page_num+1):
            page = self.page(page_num)
            yield page

    def pages(self):
        return list(self.xpages())

class Board(PagedMixin, object):
    def __init__(self, byr, board_name):
        self.byr = byr
        self.board_name = board_name

    @staticmethod
    def _page_class():
        return BoardPage

    def xthreads(self, limit_page = None):
        cur_page = 0
        for page in self.xpages():
            for thread in page.threads():
                yield thread
            cur_page += 1
            if limit_page != None and cur_page >= limit_page:
                break

    def threads(self, limit_page = None):
        return list(self.xthreads(limit_page))

class Thread(PagedMixin, object):
    def __init__(self, byr, board_name, thread_id):
        self.byr = byr
        self.board_name = board_name
        self.thread_id = thread_id

    @staticmethod
    def _page_class():
        return ThreadPage

    def xposts(self):
        for page in self.xpages():
            for post in page.posts():
                yield post

    def posts(self):
        return list(self.xposts())

class Page(object):
    def __init__(self, byr):
        self._html = None
        self.byr = byr

    @property
    def html(self):
        if self._html is None:
            self.load()
        return self._html

    def load(self):
        self._html = self.byr.load_page(self.url)

    PAT_PAGE_NUM = re.compile(ur'<li class="page-normal"><a href="\?p=(?P<page_num>\d+)" title="[^"]+">\d+</a></li>')
    def max_page_num(self):
        lst = Page.PAT_PAGE_NUM.findall(self.html);

        if len(lst)==0:
            return 1
        else:
            return max(map(int,lst))

class BoardPage(Page):
    def __init__(self, board, page_num):
        Page.__init__(self, board.byr)
        self.board_name = board.board_name
        self.page_num = page_num

    @property
    def url(self):
        return 'http://bbs.byr.cn/board/%(board_name)s?p=%(page_num)s' % self.__dict__

    PAT_THREAD_LINK = re.compile(ur'<td class="title_9"><a href="/article/\w+/(?P<thread_id>\d+)">')
    def thread_ids(self):
        return map(int, BoardPage.PAT_THREAD_LINK.findall(self.html))

    def threads(self):
        return [Thread(self.byr, self.board_name, tid)
                for tid in self.thread_ids()]

class ThreadPage(Page):
    def __init__(self, thread, page_num):
        Page.__init__(self, thread.byr)
        self.board_name = thread.board_name
        self.thread_id = thread.thread_id
        self.page_num = page_num

    @property
    def url(self):
        return 'http://bbs.byr.cn/article/%(board_name)s/%(thread_id)s?p=%(page_num)s' % self.__dict__

    PAT_BLOCK = re.compile(
            ur'<td class="posts_content_right no_bottom no_top"><p>'
            ur'(.+?)'
            ur'<font class="f000"> <br /> </font></p></td>'
            )

    @staticmethod
    def html_extract_blocks(html):
        return ThreadPage.PAT_BLOCK.findall(html)

    #PAT_DATE = re.compile(ur'\w+ \w+&nbsp;&nbsp;\d+ \d+:\d+:\d+ \d+')

    @staticmethod
    def parse_date(date_string):
        pass
        # TODO: Not implemented

    PAT_TAG = re.compile(ur'<.+?>')

    @staticmethod
    def strip_html(html):
        html = ThreadPage.PAT_TAG.sub(u'', html)
        html = html.replace('&nbsp;', ' ')
        html = html.replace('&lt;', '<')
        html = html.replace('&gt;', '>')
        html = html.replace('&amp;', '&')
        html = html.replace('&quot;', '"')
        return html

    PAT_BR = re.compile(ur' ?<br /> ?')
    @staticmethod
    def split_br(html):
        return ThreadPage.PAT_BR.split(html)

    PAT_HEADER_LINES = map(re.compile, [
        ur'发信人: (?P<username>\w+) \((?P<nickname>.*?)\), 信区: (?P<board>\w+)' ,
        ur'标  题: (?P<title>.+)',
        ur'发信站: (?P<send_site_name>.+?) \((?P<date>.+?)\), 站内',
        ])
    
    PAT_FOOTER_LINE = re.compile(ur'※ 来源:·(?P<source_site_name>.+?) (?P<source_site_addr>.+?)·\[FROM: (?P<source_ipaddr>.+?)\]')
    PAT_MODIFY_LINE = re.compile(ur'※ 修改:·byrmaster 于 (?P<modify_date>.+?) 修改本文·\[FROM: (?P<modify_ipaddr>.+?)\]')

    @staticmethod
    def block_unhtml(block):
        lines = map(ThreadPage.strip_html, ThreadPage.split_br(block))
        return lines

    @staticmethod
    def block_extract_post(block):
        lines = ThreadPage.block_unhtml(block)

        result_dict = {}
        result_dict[u'content'] = u'\n'.join(lines[4:-1])

        for pat, line in zip(ThreadPage.PAT_HEADER_LINES,lines):
            try:
                result_dict.update(pat.match(line).groupdict())
            except AttributeError, e:
                raise RegexpMismatchError(line, pat)

        # Both footers may fail to exist.
        for pat, line in [
                (ThreadPage.PAT_FOOTER_LINE, lines[-1]),
                (ThreadPage.PAT_MODIFY_LINE, lines[-2]),
                (ThreadPage.PAT_MODIFY_LINE, lines[-1]),
                ]:
            m = pat.match(line)
            if m is not None:
                result_dict.update(m.groupdict())

        return result_dict

    @staticmethod
    def html_extract_posts(html):
        return map(ThreadPage.block_extract_post, ThreadPage.html_extract_blocks(html))

    def posts(self):
        return ThreadPage.html_extract_posts(self.html)

class RegexpMismatchError(Exception):
    def __init__(self, line, regex):
        self.line = line
        self.regex = regex

