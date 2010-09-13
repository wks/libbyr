import byr3
import pickle
import sys

byr = byr3.Byr()

board = byr.board("Linux")

try:
    pickle_file = sys.argv[1]
except IndexError:
    pickle_file = "threads.pickle"

print "loading threads..."
threads = board.threads()
print "threads loaded!  %d threads to go." % len(threads)

with open(pickle_file,"w") as f:
    for i,thread in enumerate(threads):
        try:
            print "Loading thread num:%d, id=%s...." % (i,thread.thread_id)
            posts = thread.posts()
            print "thread id=%s loaded!" % thread.thread_id
            print "pickling..."
            item = (thread.thread_id,posts)
            pickle.dump(item, f, 2)
            print "pickled..."
        except byr3.RegexpMismatchError, e:
            print "Error loading thread id=%s"%thread.thread_id

