#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import io
import os
import re

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with io.open(os.path.join(here, *parts), encoding='utf-8') as handle:
        return handle.read()


def find_version(*parts):
    match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", read(*parts))
    if not match:
        raise RuntimeError('Unable to find __version__ in %s' % os.path.join(*parts))
    return match.group(1)


setup(
    name='examplelib',
    version=find_version('src', 'examplelib', '__init__.py'),
    description='A library source-compatible with Python 2 and Python 3.',
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    author='examplelib contributors',
    license='MIT',
    url='https://github.com/example/examplelib',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'six>=1.10',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries',
    ],
)
