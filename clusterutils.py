"""
    Some utilities for data clustering.

    A vector is represented by a dict.  The keys are dimensions.  Values of all
    dimensions areassumed to be floats.  For example:
    {'x':6, 'y':8} and {'ACM_ICPC'10, 'CPP':20, 'Linux':100} are vectors.
"""
def vlength(d):
    """
    Euclidian length of a vector.
    vlength({'x':3, 'y':4}) == 5.
    """
    return math.sqrt(sum(x*x for x in d.itervalues()))

def vproduct(d1,d2):
    """
    Inner (dot) product of two vectors.
    vproduct({'x':3, 'y':4}, {'x':5, 'y':6}) == 3*5 + 4*6 = 39
    """
    return sum(v1*d2[k1] for (k1,v1) in d1.iteritems() if k1 in d2)

def vcosine(d1,d2):
    """
    The cosine similarity of two vectors.
    """
    return vproduct(d1,d2)/(vlength(d1)*vlength(d2))


