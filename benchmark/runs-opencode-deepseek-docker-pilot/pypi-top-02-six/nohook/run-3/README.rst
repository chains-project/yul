======
mylib
======

``mylib`` is a small library that runs unmodified on **Python 2.7** and
**Python 3.4+**. It exists to demonstrate the layout and conventions needed to
ship a single codebase across both runtimes.

Compatibility approach
======================

* Every module starts with ``from __future__ import ...`` so that literals,
  division, and imports behave the same on both runtimes.
* ``six`` provides the compatibility shims (``text_type``, ``binary_type``,
  ``iteritems``, ...). These are re-exported from ``mylib.compat`` so the rest
  of the code has a single import surface.
* ``bdist_wheel`` is configured as ``universal``, producing a wheel that can be
  installed on either runtime.
* ``tox`` tests against the whole supported interpreter matrix.

Installation
============

::

    pip install mylib

Usage
=====

.. code-block:: python

    >>> from mylib import greet, to_text
    >>> greet("World")
    'Hello, World!'
    >>> greet(b"World")
    'Hello, World!'
    >>> to_text(42)
    '42'

Development
===========

::

    pip install -e ".[tests]"
    pytest
    tox

License
=======

MIT. See ``LICENSE``.
