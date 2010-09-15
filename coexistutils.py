# coding: utf_8
""" Some utilities to mine coexisting of users in a board. """

def thread_list_get_people(thread_list):
    return [(tid, [p['username'] for p in ps])
            for (tid, ps) in thread_list]


class CoexistingMiningContext(object):
    def __init__(self,thread_list):
        self.thread_list = thread_list
        self.thread_dict = dict(thread_list)
        self.thread_people = thread_list_get_people(self.thread_list)

    def mine_coexisting(self, iset):
        """ iset: a tuple of usernames """
        tids = sorted([tid for (tid,users) in self.thread_people
                      if all(u in users for u in iset)],
                     reverse=True)
        for tid in tids:
            title = self.thread_dict[tid][0]['title']
            print "http://bbs.byr.cn/article/Linux/%d  %s" % (tid, title)

