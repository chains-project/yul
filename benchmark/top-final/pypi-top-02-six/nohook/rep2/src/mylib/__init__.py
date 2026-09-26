import six

__version__ = "0.1.0"


def to_text(value):
    """Coerce value to the native text type on both Python 2 and 3."""
    if isinstance(value, six.text_type):
        return value
    return six.text_type(value)


def iteritems(d):
    return six.iteritems(d)
