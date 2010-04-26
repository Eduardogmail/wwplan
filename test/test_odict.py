#!/usr/bin/python
import unittest
import odict

class TestLibrary(unittest.TestCase):
    def setUp(self):
        self.odict = odict.odict([("key1", "value1"), ("key2", "value2")])
                          
    def test_setitem(self):
        self.odict["key3"] = "value3"
        self.assertEqual(self.odict["key3"], "value3")

    def test_getitem(self):
        self.assertEqual(self.odict["key1"], "value1")
        self.assertEqual(self.odict["key2"], "value2")
        
    def test_delitem(self):
        del self.odict["key2"]
        self.assertEqual(self.odict["key1"], "value1")
        self.assertTrue("key2" not in self.odict)
        self.assertEqual(len(self.odict), 1)
        
    def test_repr(self):
        s = repr(self.odict)
        self.assertTrue("key1" in s)
        self.assertTrue("value1" in s)
        
    def test_keys(self):
        self.assertEqual(self.odict.keys(), ["key1", "key2"])
        
    def test_copy(self):
        odict2 = self.odict.copy()
        self.odict["key1"] = "value11"
        self.assertEqual(odict2["key1"], "value1")
    
if __name__ == '__main__':
    unittest.main()#
