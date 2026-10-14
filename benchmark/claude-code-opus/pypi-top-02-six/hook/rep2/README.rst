mylib
=====

A library supporting both **Python 2.7** and **Python 3.6+** from one
codebase.

Development
-----------

.. code-block:: sh

    python -m venv .venv && . .venv/bin/activate
    pip install -r requirements-dev.txt
    pytest          # current interpreter
    tox             # every installed interpreter, plus flake8

Compatibility conventions
-------------------------

* Start every module with::

      from __future__ import absolute_import, division, print_function

* Mark text literals explicitly: ``u"text"`` for text and ``b"data"`` for
  bytes. Leave unprefixed ``"str"`` only where the native string type is
  needed, such as ``__all__``, attribute names, or ``%`` formats for
  exceptions.
* Use ``six`` (``six.text_type``, ``six.moves``, ``six.add_metaclass``, ...)
  rather than checking ``sys.version_info`` inline. Keep project-specific
  shims in ``mylib/_compat.py``.
* Use only syntax that is valid on both versions. That rules out f-strings,
  type annotations (use type comments), ``nonlocal``, keyword-only
  arguments, ``async``/``await``, ``yield from``, and the walrus operator.
* Put ``# -*- coding: utf-8 -*-`` at the top of any file with non-ASCII
  source.

Releasing
---------

.. code-block:: sh

    pip install build twine
    python -m build      # produces a universal py2.py3 wheel + sdist
    twine upload dist/*
