import six

__version__ = "0.1.0"


def is_string(value):
    return isinstance(value, six.string_types)


def to_text(value):
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return six.text_type(value)


class Base(six.with_metaclass(type)):
    pass
