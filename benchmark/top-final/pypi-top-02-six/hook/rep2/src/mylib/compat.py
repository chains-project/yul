import six
from six import PY2, iteritems, string_types


def to_text(value):
    if isinstance(value, six.binary_type):
        return value.decode("utf-8")
    return six.text_type(value)
