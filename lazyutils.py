def take(n, seq):
    i=0
    for item in seq:
        if i>=n:
            break
        yield item
        i+=1

def drop(n, seq):
    i=0
    for item in seq:
        if i<n:
            continue
        yield item
        i+=1

def take_while(pred, seq):
    for item in seq:
        if not pred(item):
            break
        yield item

def drop_while(pred, seq):
    dropping = True
    for item in seq:
        if dropping:
            if not pred(item):
                dropping = False
        else:
            yield item

def xfilter(pred, seq):
    for item in seq:
        if pred(item):
            yield item

def xmap(func, seq):
    for item in seq:
        yield func(item)

def xfoldl(func, init, seq):
    i = init
    for item in seq:
        i = func(i,item)
    return i

