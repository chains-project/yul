mylib
======

A small example library that is source compatible with both Python 2.7 and
Python 3.

Install
-------

::

    pip install mylib

Usage
-----

::

    from mylib._compat import to_bytes, to_unicode

    blob = to_bytes("h\u00e9llo")
    text = to_unicode(blob)

Supported interpreters
----------------------

* Python 2.7
* Python 3.5 and newer

Development
-----------

Run the full matrix locally with `tox <https://tox.readthedocs.io/>`_::

    pip install tox
    tox
