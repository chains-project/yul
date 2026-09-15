import six


def to_text(value):
    """Coerce bytes/str to a native text type on both Python 2 and 3."""
    if isinstance(value, six.binary_type):
        return value.decode("utf-8")
    return value


def iter_items(mapping):
    """dict.items() that returns an iterator on both Python 2 and 3."""
    return six.iteritems(mapping)
