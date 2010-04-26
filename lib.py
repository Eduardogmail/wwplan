"""Generic functions."""
import itertools
import re

class Struct:
    """Struct/record-like class."""
    def __init__(self, _name, **entries):
        self._name = _name
        self.__dict__.update(entries)

    def __repr__(self):
        args = [(k, v) for (k, v) in 
            vars(self).iteritems() if not k.startswith("_")]
        return "<%s> %s" % (self._name, args)

def first(it):
    """Return first item in iterable."""
    return it.next()
  
def partition(it, pred):
    """Partition element in iterator in 2 lists (true_predicate, false_predicate)."""
    true_list, false_list = [], []
    for x in it:
        (true_list if pred(x) else false_list).append(x)
    return true_list, false_list

def grouper(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    chain = itertools.chain(iterable, itertools.repeat(padvalue, n-1))
    return itertools.izip(*[chain]*n)

def flatten(lst):
    """Flat one level of lst."""
    return [y for x in lst for y in x]

def split_iter_of_consecutive(it, pred, n):
    """Yield groups in iterable delimited by n consecutive items that match predicate."""
    lst = list(it)
    indexes = [idx for (idx, x) in enumerate(lst) if pred(x)]
    indexeslst = [[x[1] for x in group] for (match, group) 
        in itertools.groupby(enumerate(indexes), lambda (i, x): i - x)]
    split_indexes = [(idxs[0], idxs[-1]+1) for idxs in indexeslst if len(idxs) >= n]
    for start, end in grouper(2, [0] + flatten(split_indexes) + [None]):
        yield lst[start:end]   

def split_iter(it, condition, skip_sep=False):
    """Split iterable yield elements grouped by condition."""
    for match, group in itertools.groupby(it, condition):
        if skip_sep and match:
            continue
        yield list(group)

def strip_iter_items(it, condition=bool):
    """Remove items in iterable that do not match condition."""
    return list(itertools.ifilter(condition, it))

def strip_list(lst, condition=bool):
    """Strip elements (from head and tail) of iterable that do not match condition."""
    start = first(idx for (idx, x) in enumerate(lst) if condition(x)) 
    end = first((len(lst)-idx) for (idx, x) in enumerate(reversed(lst)) if condition(x))
    return lst[start:end]
    
def pairwise(iterable):
    "s -> (s0, s1), (s1, s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    return itertools.izip(a, itertools.islice(b, 1, None))

def iter_block(lines, startre, endre):
    """Yield lines whose bounds are defined by a start/end regular expressions."""
    from_startre = itertools.dropwhile(lambda s: not re.match(startre, s), lines)
    for line in from_startre:
        yield line
        if re.match(endre, line):
            break

def keyify(s):
    """Replaces spaces in string for underscores and remove chars '.:'"""
    return re.sub("\s+", "_", s).replace(".", "").replace(":", "").lower() 

def parse_table(lines, fields, keyify_cb=None):
    """Parse table and yield dictionaries containing the row info."""
    def _find_columns(line, fields):
        return [(field, line.index(field)) for field in fields]
    header, units = lines[0], lines[1:]
    columns = _find_columns(header, fields)
    fields, indexes = zip(*columns)
    for line in strip_iter_items(units):
        def _pairs():
            for field, (start, end) in zip(fields, pairwise(indexes+(None,))):
                key = (keyify(field) if (not keyify_cb or keyify_cb(field)) else field)
                value = line[start:end].strip()
                yield (key, value)
        yield dict(_pairs())
