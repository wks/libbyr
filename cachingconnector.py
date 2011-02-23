#coding: utf_8

import os, urlparse, httplib


class CachingConnector(object):
    PROXY_ADDR = os.environ.get('http_proxy',None)
    FORUM_HOST = 'bbs.byr.cn'
    FORUM_ENCODING = 'gb18030'

    if PROXY_ADDR is not None:
        CONN_ADDR = urlparse.urlparse(PROXY_ADDR).netloc
    else:
        CONN_ADDR = FORUM_HOST

    def __init__(self):
        self._conn = None
        self._cache = {}

    def connect(self):
        self._conn = httplib.HTTPConnection(self.CONN_ADDR)

    @property
    def conn(self):
        if self._conn is None:
            self.connect()
        return self._conn 

    def load_page(self, url, nocache=False):
        if nocache==False:
            if url in self._cache:
                return self._cache[url]
        while True:
            try:
                self.conn.request("GET", url)
                resp = self.conn.getresponse()
                # BYR forum does not always find the borders of multi-byte
                # chars correctly.  So "replace" is needed.
                # "ignore" also works.
                text = resp.read().decode(self.FORUM_ENCODING, "replace") 
                self._cache[url] = text
                return text
            except httplib.HTTPException:
                self.connect()

