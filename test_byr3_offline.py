# coding: utf_8

import unittest
import byr3

import os.path

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')

class TestByrBase(unittest.TestCase):
    def setUp(self):
        self.byr = byr3.Byr()

    def test_board_page_url(self):
        board = self.byr.board("Linux")
        board_page = board.page(123)
        self.assertTrue(isinstance(board_page, byr3.BoardPage))
        self.assertEqual(board_page.url, 'http://bbs.byr.cn/board/Linux?p=123')

    def test_thread_page_url(self):
        thread = self.byr.thread("Linux", 12345)
        thread_page = thread.page(678)
        self.assertTrue(isinstance(thread_page, byr3.ThreadPage))
        self.assertEqual(thread_page.url, 'http://bbs.byr.cn/article/Linux/12345?p=678')

class TestByrThreadPage(unittest.TestCase):
    def setUp(self):
        self.linux_100862 = open(os.path.join(TEST_DATA_DIR, "Linux-100862.html")).read().decode('gb18030')

    def test_header_footer_matching(self):
        blocks = byr3.ThreadPage.html_extract_blocks(self.linux_100862)

        for block in blocks:
            lines = byr3.ThreadPage.block_unhtml(block)

            self.assertTrue(byr3.ThreadPage.PAT_HEADER_LINES[0].match(lines[0]) is not None)
            self.assertTrue(byr3.ThreadPage.PAT_HEADER_LINES[1].match(lines[1]) is not None)
            self.assertTrue(byr3.ThreadPage.PAT_HEADER_LINES[2].match(lines[2]) is not None)
            self.assertTrue(byr3.ThreadPage.PAT_FOOTER_LINE.match(lines[-1]) is not None)

    def test_footer_modify_matching(self):
        blocks = byr3.ThreadPage.html_extract_blocks(self.linux_100862)

        for block in [blocks[7]]:
            lines = byr3.ThreadPage.block_unhtml(block)

            self.assertTrue(byr3.ThreadPage.PAT_MODIFY_LINE.match(lines[-2]) is not None)

    def test_extract_posts(self):
        posts = byr3.ThreadPage.html_extract_posts(self.linux_100862)
        self.assertEqual(len(posts), 10)

        for username in ["sysusky", "hzmangel", "wks"]:
            their_posts = [p for p in posts if p['username'] == username]
            self.assertNotEqual(len(their_posts), 0, '%s has no posts'%username)

    def test_page_max_num(self):
        byr = byr3.Byr()
        thread = byr.thread('Linux', 100862)
        page = thread.page(1)
        page._html = self.linux_100862 # This is a white-box test

        self.assertEqual(page.max_page_num(), 2)


if __name__ == '__main__':
    unittest.main()

