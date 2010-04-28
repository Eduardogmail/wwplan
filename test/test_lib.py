#!/usr/bin/python
import unittest
from wwplan import lib

class TestLibrary(unittest.TestCase):
    def test_first(self):
        it = (x for x in range(10))
        self.assertEqual(lib.first(it), 0)
        self.assertEqual(list(it), range(1, 10))
        self.assertRaises(StopIteration, lib.first, it)       

    def test_partition(self):
        lst = range(10)
        lst_true, lst_false = lib.partition(lst, lambda x: x % 2 == 0)
        self.assertEqual(lst_true, [0, 2, 4, 6, 8])
        self.assertEqual(lst_false, [1, 3, 5, 7, 9])

    def test_grouper(self):
        s = "abcd1234"
        groups = list(lib.grouper(3, s, 'x'))
        self.assertEqual(groups[0], tuple("abc"))
        self.assertEqual(groups[1], tuple("d12"))
        
    def test_flatten(self):
        self.assertEqual(lib.flatten([[1, 2], [3, 4, 5], []]), [1, 2, 3, 4, 5])
        
    def test_split_iter_of_consecutive(self):
        lst = [1, 0, 0, 2, 3, 4, 0, 5, 0, 0, 6, 7]
        self.assertEqual(list(lib.split_iter_of_consecutive(lst, lambda x: x == 0, 2)),
            [[1], [2, 3, 4, 0, 5], [6, 7]])
            
    def test_split_iter(self):
        lst = [1, 0, 0, 0, 2, 3, 4, 0, 5, 0, 0, 6, 7]
        self.assertEqual(list(lib.split_iter(lst, lambda x: x == 0, skip_sep=True)),
            [[1], [2, 3, 4], [5], [6, 7]])
        self.assertEqual(list(lib.split_iter(lst, lambda x: x == 0, skip_sep=False)),
            [[1], [0, 0, 0], [2, 3, 4], [0], [5], [0, 0], [6, 7]])
            
    def test_strip_iter_items(self):
        lst = [1, 0, 0, 2, 3, 4, 0, 5, 0, 0, 6, 7]
        self.assertEqual(list(lib.strip_iter_items(lst, lambda x: x != 0)),
            [1, 2, 3, 4, 5, 6, 7])
    
    def test_strip_list(self):
        lst = [0, 0, 1, 2, 3, 0]
        self.assertEqual(list(lib.strip_list(lst, lambda x: x != 0)),
            [1, 2, 3])
            
    def test_pairwise(self):
        lst = [0, 1, 2, 3, 4]
        self.assertEqual(list(lib.pairwise(lst)), [(0, 1), (1, 2), (2, 3), (3, 4)])
        
    def test_iter_block(self):
        lines = map(str, [1, 0, 2, 3, 4, 9, 5, 0, 0, 6, 7])
        res = list(lib.iter_block(lines, r"^0$", r"^9$"))
        self.assertEqual(res, ['0', '2', '3', '4', '9'])

    def test_keyify(self):
        k = lib.keyify
        self.assertEqual(k("some key"), "some_key") 
        self.assertEqual(k("some key.key2:key3"), "some_keykey2key3")
                
    def test_parse_table(self):
        table = """header1    header2  header3
                   val1a      val2a    val3a
                   val1b      val2b    val3b"""
        table2 = [s.strip() for s in table.splitlines()]
        res = list(lib.parse_table(table2, ["header1", "header2", "header3"]))
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0], {"header1": "val1a", "header2": "val2a", "header3": "val3a"})
        self.assertEqual(res[1], {"header1": "val1b", "header2": "val2b", "header3": "val3b"})

            
if __name__ == '__main__':
    unittest.main()
