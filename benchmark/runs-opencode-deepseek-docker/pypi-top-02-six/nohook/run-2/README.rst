======
mylib
======

A sample Python library whose source is compatible with both Python 2.7 and
Python 3.4+.

Installation
============

::

    pip install mylib

Usage
=====

.. code-block:: python

    from mylib import greet, merge, normalize

    greet("world")                      # 'Hello, world!'
    merge({"a": 1}, {"b": 2})           # {'a': 1, 'b': 2}
    normalize("  hello\tworld  ")       # 'hello world'

Compatibility
=============

Source files start with::

    from __future__ import absolute_import, division, print_function, unicode_literals

Version-specific behavior lives in ``mylib/_compat.py``. Import compatibility
helpers from there instead of relying on interpreter-specific modules.

Testing
=======

Run the test suite across every supported interpreter::

    tox

Development dependencies::

    pip install -r requirements-dev.txt

A universal wheel (``py2.py3-none-any``) is produced by the
``[bdist_wheel] universal = 1`` setting in ``setup.cfg``.
