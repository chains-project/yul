==========
examplelib
==========

A library whose source code is compatible with **both Python 2 and Python 3**
from a single code base.

The project targets Python 2.7 and Python 3.5+, and uses the following rules:

* Every module starts with ``from __future__ import ...`` imports so that
  ``print``, ``unicode_literals``, ``division`` and ``absolute_import`` behave
  the same on both runtimes.
* ``six`` is used for the remaining differences (string/bytes types, integer
  types, iterators, ...).
* Test and packaging tooling runs against every supported interpreter with
  ``tox``.

Installation
------------

::

    pip install examplelib

Usage
-----

.. code-block:: python

    from examplelib import compat

    if isinstance(value, compat.string_types):
        ...

Development
-----------

Create an environment with every supported interpreter plus ``tox`` and run the
whole matrix::

    pip install -r requirements-dev.txt
    tox

Build a single universal wheel that works on Python 2 and 3::

    python setup.py bdist_wheel
    # -> dist/examplelib-0.1.0-py2.py3-none-any.whl

License
-------

MIT. See ``LICENSE``.
