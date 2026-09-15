import six

__version__ = "0.1.0"


def to_text(value):
    """Return value as the native text type on both Python 2 and 3."""
    if isinstance(value, six.text_type):
        return value
    if isinstance(value, six.binary_type):
        return value.decode("utf-8")
    return six.text_type(value)


class Base(six.with_metaclass(type)):
    pass
