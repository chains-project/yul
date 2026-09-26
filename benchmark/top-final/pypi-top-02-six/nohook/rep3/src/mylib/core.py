from __future__ import absolute_import, division, print_function

import six


def greet(name):
    if not isinstance(name, six.string_types):
        raise TypeError("name must be a string")
    return "Hello, {0}!".format(name)
