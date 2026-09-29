# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import examplelib
from examplelib import compat


def test_version_is_set():
    assert examplelib.__version__


def test_runs_on_exactly_one_python():
    assert compat.PY2 != compat.PY3


def test_string_types_cover_native_strings():
    assert isinstance('hello', compat.string_types)
