# coding: utf_8

from cachingconnector import CachingConnector
from lxml import etree
import datetime

import re

class Byr(CachingConnector):

    def board(self, board_name, page=1, html=False):
        url_pattern = r"http://bbs.byr.cn/board/%s?p=%d"
        url = url_pattern % (board_name, page)
        html_content = self.load_page(url)
        if html:
            return html_content
        tree = etree.HTML(html_content)

        def parse_thread(tr):
            date_text = tr.xpath("td[@class='title_10']/text()")[0]
            date_text = re.findall(r"(\d+-\d+-\d+|\d+:\d+:\d+)", date_text)[0]
            try:
                date = datetime.datetime.strptime(date_text,"%Y-%m-%d")
            except:
                today = datetime.date.today().isoformat()
                date = datetime.datetime.strptime(today+" "+date_text,"%Y-%m-%d %H:%M:%S")

            url = tr.xpath("td[@class='title_9']/a/@href")[0]
            thread_id = re.findall(r"/article/\w+/(\d+)", url)[0]

            return {
                    "thread_id": thread_id,
                    "title": tr.xpath("td[@class='title_9']/a/text()")[0],
                    "url": url,
                    "author": tr.xpath("td[@class='title_10']/a/text()")[0],
                    "date": date,
                    "num_replies": tr.xpath("td[@class='title_11 middle']/text()")[0],
                    }

        return {
                "board_masters": tree.xpath("//div[@class='b-head corner']/div/a/text()"),
                "threads": [parse_thread(row)
                    for row in tree.xpath("//table[@class='board-list tiz']//tr")],
                "max_page_num": int(tree.xpath("(//ol[@class='page-main'])[1]/li[last()-1]//text()")[0]),
                }

    def thread(self, board_name, thread_id, page=1, html=False):
        url_pattern = r"http://bbs.byr.cn/article/%s/%d?p=%d"
        url = url_pattern % (board_name, thread_id, page)
        html_content = self.load_page(url)
        if html:
            return html_content
        tree = etree.HTML(html_content)

        def parse_post(post):
            text_or_br = post.xpath(".//td/p/br|.//td/p/text()")
            texts = [x.strip() if isinstance(x, unicode) else u"\n"
                    for x in text_or_br]
            content = u"".join(texts)
            return {
                    "author": post.xpath(".//span[@class='u-name']/a/text()")[0],
                    "post_id": int(post.xpath(".//li[@class='a-reply']/a/@href")[0].split("/")[-1]),
                    "content": content,
                    }

        return {
                "posts": [parse_post(post)
                    for post in tree.xpath("//table[@class='article']")],
                "num_topics": int(tree.xpath("//ul[@class='pagination']/li[1]/i/text()")[0]),
                "max_page_num": int(tree.xpath("(//ol[@class='page-main'])[1]/li[last()-1]//text()")[0]),
                }
