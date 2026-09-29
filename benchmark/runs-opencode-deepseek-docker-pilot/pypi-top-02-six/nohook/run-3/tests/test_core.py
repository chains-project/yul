# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import unittest

from mylib import greet, merged, to_bytes, to_text
from mylib.compat import text_type


class ToTextTests(unittest.TestCase):
    def test_passthrough_unicode(self):
        self.assertEqual(to_text("caf\u00e9"), "caf\u00e9")

    def test_decodes_utf8_bytes(self):
        self.assertEqual(to_text("caf\u00e9".encode("utf-8")), "caf\u00e9")

    def test_coerces_non_string(self):
        self.assertEqual(to_text(42), "42")


class ToBytesTests(unittest.TestCase):
    def test_encodes_unicode(self):
        self.assertEqual(to_bytes("caf\u00e9"), "caf\u00e9".encode("utf-8"))

    def test_passthrough_bytes(self):
        value = b"raw"
        self.assertIs(to_bytes(value), value)


class GreetTests(unittest.TestCase):
    def test_greets_text(self):
        result = greet("World")
        self.assertIsInstance(result, text_type)
        self.assertEqual(result, "Hello, World!")

    def test_greets_utf8_bytes(self):
        self.assertEqual(greet(b"Jos\xc3\xa9"), "Hello, Jos\u00e9!")

    def test_rejects_non_string(self):
        with self.assertRaises(TypeError):
            greet(123)


class MergedTests(unittest.TestCase):
    def test_later_mappings_win(self):
        self.assertEqual(merged({"a": 1}, {"a": 2, "b": 3}), {"a": 2, "b": 3})


if __name__ == "__main__":
    unittest.main()
