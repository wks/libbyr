# coding: utf_8

class FPTree(object):
    def __init__(self, trans_set, min_sup):
        """ Build a FPTree with a given transaction set.

            trans_set :: [(trans_id, [item, ...]), ...]
            That is, a list of tuples.  Each tuple has a trans_id and a list of items.

            trans_id:   Transaction id.  Must be unique to each transaction.
            item:       Item in the transaction.
                        Duplicate items are allowed, but they are only counted as one.

            min_sup:    Minimum support.  The minimum frequency of an item to be
                        considered as "frequent".
            """

        self.header_table = {}
        self.root = FPNode(None)

        freq = {}


        for tid, items in trans_set:
            for item in set(items):
                freq[item] = freq.get(item,0)+1

        freq_rev_list = sorted([(i,f) for (i,f) in freq.items() if f >= min_sup],
                key=lambda(i,f):f, reverse=True)

        freq_rev_order = dict((i,o) for (o,(i,f)) in enumerate(freq_rev_list))
        self.freq_rev_order = freq_rev_order

        for tid, items in trans_set:
            cur_freq_items = sorted([i for i in items if i in freq_rev_order],
                    key = lambda i:freq_rev_order[i])

            self.insert_tree(cur_freq_items)

    def insert_tree(self, freq_items):
        cur_node = self.root
        for item in freq_items:
            if item not in cur_node.children:
                new_node = FPNode(item)
                cur_node.children[item] = new_node
                self.header_table.setdefault(item,[]).append(new_node)
            cur_node = cur_node.children[item]
            cur_node.count += 1

class FPNode(object):
    def __init__(self, item):
        self.item = item
        self.count = 0
        self.children = {}

def print_fp_tree(fptree):
    def print_node(node, head_prefix, children_prefix):
        print u"%s%s:%d"%(head_prefix, node.item, node.count)
        children = node.children.values()
        if len(children)==0:
            return
        for child in children[:-1]:
            print_node(child, children_prefix+u"├", children_prefix+u"│")
        print_node(children[-1], children_prefix+u"└", children_prefix+u" ")
    print_node(fptree.root,u"",u"")

