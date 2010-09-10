# coding: utf_8

import unittest
import byr3

import os.path

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')

class TestByrOnline(unittest.TestCase):
    def setUp(self):
        self.byr = byr3.Byr()

    def test_load_page(self):
        page = self.byr.load_page('http://bbs.byr.cn/default')
        self.assertTrue(u'北邮人论坛' in page)

    def test_board_page(self):
        board = self.byr.board("Linux")
        bp = board.page(1)
        self.assertTrue(u'如非特殊需要，本版不讨论关于RedHat9的相关问题' in bp.html)

    def test_board_thread_list(self):
        board = self.byr.board("Linux")
        tl = board.page(1).thread_ids()
        self.assertEqual(len(tl), 30) # 每页30个帖子

    def test_thread_page_posts_nums(self):
        thread = self.byr.thread('Linux', 100862)
        tp = thread.page(1)
        posts = list(tp.posts())
        self.assertEqual(len(posts), 10) # 第一页应该有10贴

    def test_thread_page_posts_authors(self):
        thread = self.byr.thread('Linux', 100862)
        tp = thread.page(1)
        posts = list(tp.posts())
        for username in ["sysusky", "hzmangel", "wks"]:
            their_posts = [p for p in posts if p['username'] == username]
            self.assertNotEqual(len(their_posts), 0, '%s has no posts'%username)

    def test_whole_thread_page_fetch(self):
        thread = self.byr.thread('Linux', 100862)
        max_page_num = thread.page(0).max_page_num()
        pages = thread.pages()
        self.assertEqual(len(pages), max_page_num)

    def test_whole_thread_post_fetch(self):
        thread = self.byr.thread('Linux', 100862)
        max_page_num = thread.page(0).max_page_num()
        posts = thread.posts()
        self.assertEqual(len(posts), 14) # currently (2010-09-11 00:14)
        for i,username in enumerate([
            "sysusky", "hzmangel", "sysusky", "wks", "sysusky",
            "yyg747", "kemp86", "byrmaster", "sutar", "sysusky",
            "sysusky", "byrmaster", "sysusky", "byrmaster", ]):
            self.assertEqual(posts[i]['username'], username)

if __name__ == '__main__':
    unittest.main()

