mylib
=====

A small library that keeps a single source tree compatible with both
Python 2 and Python 3.

The examples, metadata and tooling in this repository show one way to do
that without maintaining forked ``py2``/``py3`` branches.

Installation
------------

::

    pip install mylib

Usage
-----

.. code-block:: python

    >>> from mylib import slugify
    >>> slugify("Hello, World!")
    'hello-world'

Compatibility approach
----------------------

* Every module starts with ``from __future__ import ...`` so the same code
  runs on Python 2.7 and 3.x.
* ``mylib/_compat.py`` wraps `six <https://pypi.org/project/six/>`_ and the
  moved standard-library modules. All version differences live there.
* Packaging stays on ``setup.py``/``setup.cfg`` instead of ``pyproject.toml``
  because Python 2.7's pip cannot install PEP 517/518 builds.
* The wheel is marked ``universal`` so a single wheel installs on both.
* ``tox.ini`` runs the test suite against every supported interpreter.

Development
-----------

::

    pip install -e ".[test]"
    pytest

    # Run the full interpreter matrix (requires each Python available):
    tox

Supported versions
------------------

Python 2.7, 3.5, 3.6, 3.7, 3.8 and 3.9.

License
-------

MIT. See ``LICENSE``.
