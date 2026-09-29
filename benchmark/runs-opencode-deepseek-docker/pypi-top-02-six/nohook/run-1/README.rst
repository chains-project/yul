mylib
=====

``mylib`` is an example library whose source code runs unchanged on both
Python 2 and Python 3. It demonstrates a layout and a handful of patterns
that keep a single code base importable from either interpreter.

Features
--------

* One source tree, no ``2to3`` step at install time.
* ``from __future__`` imports and ``six`` used only in a small compatibility
  module, so version specific logic stays in one place.
* A universal wheel (``bdist_wheel universal = 1``) that installs on both
  major Python versions.
* ``tox`` and GitHub Actions matrices covering Python 2.7 through 3.11.

Installation
------------

::

    pip install mylib

The only runtime dependency is ``six``. The package declares
``python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*"``.

Usage
-----

.. code-block:: python

    from __future__ import unicode_literals

    import mylib

    mylib.greet(b"World")          # -> 'Hello, World!'
    mylib.encode("payload")        # -> 'cGF5bG9hZA=='
    mylib.decode(b"cGF5bG9hZA==")  # -> 'payload'
    list(mylib.iter_dict({"a": 1}))  # -> [('a', 1)]

``mylib.compat`` exposes the primitives that make the rest of the code
version agnostic:

.. code-block:: python

    from mylib.compat import PY2, binary_type, text_type, to_bytes, to_text

Compatibility rules used in this project
----------------------------------------

#. Start every module with
   ``from __future__ import absolute_import, division, print_function, unicode_literals``.
#. Never compare against ``str`` directly; use ``mylib.compat.string_types``.
#. Convert between ``bytes`` and text explicitly with ``to_bytes``/``to_text``.
#. Iterate mappings with ``iteritems``/``iterkeys``/``itervalues`` instead of
   ``.items()``/``.keys()``/``.values()``.
#. Declare classes with ``@add_metaclass`` rather than Python 3 metaclass
   syntax.
#. Guard version specific imports behind ``PY2``/``PY3``.

Testing
-------

::

    pip install -e ".[test]"
    pytest

To run the full interpreter matrix (requires the interpreters to be
installed)::

    pip install tox
    tox

Layout
------

::

    mylib/
        __init__.py      package metadata and public API
        compat.py        Python 2/3 compatibility helpers
        core.py          example, version-agnostic implementation
    tests/
        test_compat.py
        test_core.py
    setup.py
    setup.cfg
    pyproject.toml
    tox.ini
    .github/workflows/ci.yml

License
-------

MIT. See ``LICENSE``.
