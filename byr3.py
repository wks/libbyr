# coding: utf_8

import os, sys, re, urllib2, httplib, string

class Byr(object):
    FORUM_HOST = 'bbs.byr.cn'
    FORUM_ENCODING = 'gb18030'

    def __init__(self):
        self._conn = None

    def connect(self):
        self._conn = httplib.HTTPConnection(self.FORUM_HOST)

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
                return resp.read().decode(self.FORUM_ENCODING)
            except httplib.HTTPException:
                self.reconnect()

    def board(self, board_name):
        return Board(self, board_name)

    def thread(self, board_name, thread_id):
        return Thread(self, board_name, thread_id)

class PagedMixin(object):
    def page(self, page_num):
        return self._page_class()(self, page_num)

class Board(PagedMixin, object):
    def __init__(self, byr, board_name):
        self.byr = byr
        self.board_name = board_name

    @staticmethod
    def _page_class():
        return BoardPage

class Thread(PagedMixin, object):
    def __init__(self, byr, board_name, thread_id):
        self.byr = byr
        self.board_name = board_name
        self.thread_id = thread_id

    @staticmethod
    def _page_class():
        return ThreadPage

    def xpages(self):
        first_page = self.page(1)
        last_page_num = first_page.max_page_num()

        yield first_page

        for page_num in xrange(2,last_page_num+1):
            page = self.page(page_num)
            yield page

    def pages(self):
        return list(self.xpages())

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

    PAT_PAGE_NUM = re.compile(ur'<li class="page-normal"><a href="\?p=(?P<page_num>\d+)" title="[^"]+">\d+</a></li>')
    def max_page_num(self):
        lst = Page.PAT_PAGE_NUM.findall(self.html);

        if len(lst)==0:
            return 1
        else:
            return max(map(int,lst))

    def load(self):
        self._html = self.byr.load_page(self.url)

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

    PAT_DATE = re.compile(ur'\w+ \w+&nbsp;&nbsp;\d+ \d+:\d+:\d+ \d+')

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
        ur'发信人: (?P<username>\w+) \((?P<nickname>.+?)\), 信区: (?P<board>\w+)' ,
        ur'标  题: (?P<title>.+)',
        ur'发信站: 北邮人论坛 \((?P<date>[A-Za-z0-9 :]+)\), 站内',
        ])
    
    PAT_FOOTER_LINE = re.compile(ur'※ 来源:·北邮人论坛 (http://)?bbs\.byr\.cn·\[FROM: (?P<source_ipaddr>[0-9.*]+)\]')
    PAT_MODIFY_LINE = re.compile(ur'※ 修改:·byrmaster 于 (?P<modify_date>[A-Za-z0-9 :]+) 修改本文·\[FROM: (?P<modify_ipaddr>[0-9.*]+)\]')

    @staticmethod
    def block_unhtml(block):
        lines = map(ThreadPage.strip_html, ThreadPage.split_br(block))
        return lines

    @staticmethod
    def block_extract_post(block):
        lines = ThreadPage.block_unhtml(block)

        result_dict = {}
        result_dict[u'content'] = u'\n'.join(lines[4:-1])

        for pat, line in zip(ThreadPage.PAT_HEADER_LINES,lines) + [(ThreadPage.PAT_FOOTER_LINE, lines[-1])]:
            result_dict.update(pat.match(line).groupdict())

        m_lb1 = ThreadPage.PAT_MODIFY_LINE.match(lines[-2])
        if m_lb1 is not None:
            result_dict.update(m_lb1.groupdict())

        return result_dict

    @staticmethod
    def html_extract_posts(html):
        return map(ThreadPage.block_extract_post, ThreadPage.html_extract_blocks(html))

    def posts(self):
        return ThreadPage.html_extract_posts(self.html)
    

class Blah(Page):
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

