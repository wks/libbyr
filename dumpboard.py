#!/usr/bin/env python
# coding: utf_8

import byr3
import pickle
import sys
import getopt

USAGE="""dumpboard.py: Dump a board in the BYR forum.
Usage: python dumpboard.py [args]...

Parameters:
    -b, --board-name:   Name of the board to dump.  Default: Linux
    -l, --limit-pages:  Limit the total number of pages to dump.  Each page has
                        at most 60 threads.  Default: None
    -o, --output:       The output file name.  Default: threads.pickle
    -h, --help:         Show this help message.
"""

try:
    optlist, args = getopt.getopt(sys.argv[1:], "b:l:o:h", [
        "board-name", "limit-pages", "output", "help"])
except getopt.GetoptError, err:
    print str(err)
    print USAGE
    sys.exit(2)

board_name = "Linux"
limit_pages = None
output_file_name = "threads.pickle"

for o,a in optlist:
    if o in ['-b', '--board-name']:
        board_name = a
    elif o in ["-l", "--limit-pages"]:
        limit_pages = int(a)
    elif o in ["-o", "--output"]:
        output_file_name = a
    elif o in ["-h", "--help"]:
        print USAGE
        sys.exit()

byr = byr3.Byr()

board = byr.board(board_name)

print "loading threads..."
threads = board.threads(limit_pages)
print "threads loaded!  %d threads to go." % len(threads)

with open(output_file_name,"w") as f:
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

