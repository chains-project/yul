mylib
=====

``mylib`` is a small example library whose source code runs unchanged on
**Python 2.7** and **Python 3.5+**.

Why this template exists
------------------------

Python 2 reached end of life in 2020, but many downstream users still run
Python 2.7. A *dual-source* library keeps a single code base that works on
both major versions instead of maintaining separate ``py2``/``py3`` branches.

How compatibility is achieved
-----------------------------

* Every module starts with::

      from __future__ import absolute_import, division, print_function, unicode_literals

  This gives Python 2 the Python 3 semantics for imports, division, printing
  and string literals.

* The `six <https://six.readthedocs.io/>`_ shim is the only runtime
  dependency. It provides ``string_types``, ``text_type``, ``binary_type``
  and the renamed standard-library modules.

* All version-specific code lives in ``mylib/_compat.py`` so the rest of the
  library never inspects ``sys.version``.

* The packaging metadata uses ``python_requires`` and a *universal wheel*
  (``[bdist_wheel] universal = 1``) so a single wheel installs on both.

Installation
------------

::

    pip install -e .
    pip install -e ".[test]"

Usage
-----

.. code-block:: python

    from mylib import ensure_bytes, ensure_text

    text = ensure_text(b"caf\xc3\xa9")   # u"café" on both major versions
    data = ensure_bytes(u"café")          # b"caf\xc3\xa9" on both

Running the tests
-----------------

Run against every interpreter you have installed with `tox
<https://tox.readthedocs.io/>`_::

    tox

or just the current interpreter::

    pytest

Turning off Python 2 support later
----------------------------------

When you are ready to drop Python 2:

1. Remove ``py27`` from ``tox.ini`` and the 2.7 classifiers from ``setup.py``.
2. Relax ``python_requires`` to ``>=3.7``.
3. Remove the ``six`` dependency and inline ``_compat``.
4. Delete the ``from __future__`` imports (harmless, but no longer needed).

License
-------

MIT. See ``LICENSE``.
