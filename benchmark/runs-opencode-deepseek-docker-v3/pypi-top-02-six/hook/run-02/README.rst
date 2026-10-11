======
mylib
======

A small example library whose source code runs unchanged on **Python 2.7** and
**Python 3.5+**.

This project demonstrates the conventions you need to follow for dual
compatibility:

* ``from __future__ import absolute_import, division, print_function, unicode_literals``
  at the top of every module.
* A single ``mylib._compat`` module that centralises every version-specific
  name (backed by `six <https://six.readthedocs.io/>`_).
* ``setup.cfg`` marks the wheel as ``universal = 1`` so a single ``py2.py3``
  wheel is produced.
* ``tox`` and the GitHub Actions workflow run the test suite against every
  supported interpreter.

Installation
============

::

    pip install mylib

Usage
=====

.. code-block:: python

    >>> from mylib import slugify, chunked
    >>> slugify("Hello, World!")
    'hello-world'
    >>> list(chunked(range(5), 2))
    [[0, 1], [2, 3], [4]]

Command line
------------

::

    $ mylib "Hello, World!"
    hello-world

Development
===========

::

    pip install -e ".[testing]"
    pytest
    tox

License
=======

MIT.  See ``LICENSE``.
