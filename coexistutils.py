# coding: utf_8
""" Some utilities to mine coexisting of users in a board. """

class CoexistingMiningContext(object):
    def __init__(thread_list):
        self.thread_list = thread_list
        self.thread_dict = thread_dict
        self.thread_people = [(tid, [p['username'] for p in ps])
                for (tid, ps) in self.thread_list]

    def mine_coexisting(self, iset):
        """ iset: a tuple of usernames """
        tids = sorted([tid for (tid,users) in self.thread_people
                      if all(u in users for u in iset)],
                     reverse=True)
        for tid in tids:
            title = self.thread_dict[tid][0]['title']
            print "http://bbs.byr.cn/article/Linux/%d  %s" % (tid, title)

