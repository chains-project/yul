from __future__ import print_function

import sys
from os.path import join, dirname, abspath

PROJECT_DIR = dirname(abspath(__file__))

try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    from distutils.core import setup
    find_packages = None


setup(
    name='pycompat',
    version='1.0.0',
    description='A library for writing source code compatible with both Python 2 and Python 3',
    author='Benchmark User',
    author_email='user@example.com',
    url='https://github.com/example/pycompat',
    license='MIT',
    packages=['pycompat'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=[],
    extras_require={
        'test': [
            'pytest>=3.0',
            'pytest-cov',
        ],
    },
)