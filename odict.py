"""
Simple Ordered Dictionary.

See http://code.activestate.com/recipes/496761/
"""
from UserDict import DictMixin
from pprint import pformat

class odict(DictMixin):    
    def __init__(self, items=None):
        self._keys = []
        self._data = {}
        for key, value in (items or []):
            self[key] = value
        
    def __setitem__(self, key, value):
        if key not in self._data:
            self._keys.append(key)
        self._data[key] = value
                
    def __getitem__(self, key):
        return self._data[key]    
    
    def __delitem__(self, key):
        del self._data[key]
        self._keys.remove(key)
        
    def __repr__(self):
        result = []
        for key in self._keys:
            result.append('(%s, %s)' % (repr(key), repr(self._data[key])))
        return ''.join(['OrderedDict', '([', ', '.join(result), '])'])
  
    def pprint(self):
        info = pformat(self.items())
        template = ("OrderedDict(\n%s\n)" if "\n" in info else "OrderedDict(%s)")
        print template % info
                  
    def keys(self):
        return list(self._keys)
        
    def copy(self):
        copyDict = odict()
        copyDict._data = self._data.copy()
        copyDict._keys = self._keys[:]
        return copyDict
