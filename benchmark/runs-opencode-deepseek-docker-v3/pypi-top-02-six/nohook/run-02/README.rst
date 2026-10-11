mylib
=====

A small library whose source is compatible with both Python 2.7 and
Python 3.5+.

Installation
------------

::

    pip install -e .

Usage
-----

::

    from mylib import greet, merge

    greet("World")            # u'Hello, World!'
    merge({"a": 1}, {"b": 2}) # {'a': 1, 'b': 2}

Writing version-agnostic code
-----------------------------

All differences between Python 2 and Python 3 are isolated in
``mylib/_compat.py``. Import the helpers from there rather than using
version-specific builtins directly:

.. code-block:: python

    from mylib._compat import (
        PY2,
        text_type,
        binary_type,
        string_types,
        integer_types,
        range,
        map,
        zip,
        filter,
        iteritems,
        iterkeys,
        itervalues,
        iterbytes,
    )

Guidelines used throughout this project:

* Start every module with
  ``from __future__ import absolute_import, division, print_function, unicode_literals``.
* Use ``io.open(..., encoding="utf-8")`` instead of the built-in ``open``.
* Use ``text_type`` / ``binary_type`` / ``string_types`` for type checks.
* Use ``iteritems`` and friends instead of calling ``.iteritems()``.
* Keep ``setup.py`` valid Python 2.7 syntax (no f-strings, no keyword-only
  arguments) and produce a universal wheel via ``universal = 1``.

Testing
-------

Run the suite against every interpreter with tox::

    tox

Or against the current interpreter only::

    pip install -r requirements-dev.txt
    pytest
