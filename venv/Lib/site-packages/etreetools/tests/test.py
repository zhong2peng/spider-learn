from .. import lib
import unittest
import xml.etree.ElementTree as ET
from copy import deepcopy as dup

class LibTest(unittest.TestCase):
    def assert_etree_lib_eq(self, x, y):
        self.assertTrue(lib.equal(x, y))

    def assert_etree_str_eq(self, x, y):
        x = x if isinstance(x, (str, bytes)) else ET.tostring(x)
        y = y if isinstance(y, (str, bytes)) else ET.tostring(y)
        self.assertEqual(x, y)

    def assert_etree_both_eq(self, x, y):
        self.assert_etree_lib_eq(x, y)
        self.assert_etree_str_eq(x, y)

    def test_extend(self):
        fs = ET.fromstring

        def extend_test(input, iterable, output):
            inp = fs(input)
            self.assert_etree_both_eq(fs(output), lib.extend(dup(inp), dup(iterable)))

        extend_test(b'<a>x</a>', ('y',),
                    b'<a>xy</a>')
        extend_test(b'<a/>', ('x',),
                    b'<a>x</a>')
        extend_test(b'<a>x<b>y</b></a>', ('z',),
                    b'<a>x<b>y</b>z</a>')
        extend_test(b'<a>x<b>y</b>z</a>', ('w',),
                    b'<a>x<b>y</b>zw</a>')
        extend_test(b'<a>x<b>y</b></a>', (fs('<c>C</c>'),),
                    b'<a>x<b>y</b><c>C</c></a>')
        extend_test(b'<a />', ('x', fs('<c>C</c>'), 'y'),
                    b'<a>x<c>C</c>y</a>')

    def test_extend_split(self):
        fs = ET.fromstring

        def test(input):
            tag = fs(input)

            tag1 = dup(tag)
            lib.extend(tag1, lib.split(tag1))
            self.assert_etree_both_eq(tag, tag1)

            tag2 = dup(tag)
            lib.extend(tag2, lib.split(tag2, separate_tails=False))
            self.assert_etree_both_eq(tag, tag2)

        for x in [
                '<a/>',
                '<a>x</a>',
                '<a><b></b></a>',
                '<a>x<b></b></a>',
                '<a><b></b>y</a>',
                '<a>x<b></b>y</a>',
                '<a>x<b>z</b>y</a>',
                '<a>x<b>z</b><b2>w</b2>y</a>']:
            test(x)
