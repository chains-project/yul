"""Tests for the compatibility helpers and the example API.

Deliberately uses only the standard library ``unittest`` package so the very
same suite runs on Python 2.7 and on modern Python 3.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import shutil
import sys
import tempfile
import unittest

from compatlib import PY2, greet, read_text, write_text
from compatlib._compat import binary_type, text_type, to_bytes, to_text


class CompatHelpersTests(unittest.TestCase):
    def test_python_major_is_detected(self):
        self.assertEqual(PY2, sys.version_info[0] == 2)

    def test_to_bytes_encodes_text(self):
        result = to_bytes("caf\u00e9")
        self.assertIsInstance(result, binary_type)
        self.assertEqual(result, "caf\u00e9".encode("utf-8"))

    def test_to_bytes_is_idempotent(self):
        raw = "caf\u00e9".encode("utf-8")
        self.assertEqual(to_bytes(raw), raw)

    def test_to_text_decodes_bytes(self):
        result = to_text("caf\u00e9".encode("utf-8"))
        self.assertIsInstance(result, text_type)
        self.assertEqual(result, "caf\u00e9")

    def test_to_text_is_idempotent(self):
        self.assertEqual(to_text("caf\u00e9"), "caf\u00e9")

    def test_to_bytes_rejects_other_types(self):
        with self.assertRaises(TypeError):
            to_bytes(42)

    def test_to_text_rejects_other_types(self):
        with self.assertRaises(TypeError):
            to_text(42)


class CoreTests(unittest.TestCase):
    def test_greet_returns_text(self):
        result = greet("World")
        self.assertIsInstance(result, text_type)
        self.assertEqual(result, "Hello, World!")

    def test_greet_accepts_bytes(self):
        self.assertEqual(greet(b"World"), "Hello, World!")

    def test_greet_accepts_utf8_text(self):
        self.assertEqual(greet("caf\u00e9"), "Hello, caf\u00e9!")


class RoundTripTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_read_write_round_trip(self):
        path = os.path.join(self.tmpdir, "notes.txt")
        write_text(path, "caf\u00e9\n")
        self.assertEqual(read_text(path), "caf\u00e9\n")

    def test_read_uses_declared_encoding(self):
        path = os.path.join(self.tmpdir, "latin1.txt")
        with open(path, "wb") as handle:
            handle.write("caf\u00e9\n".encode("latin-1"))
        self.assertEqual(read_text(path, encoding="latin-1"), "caf\u00e9\n")


if __name__ == "__main__":
    unittest.main()
