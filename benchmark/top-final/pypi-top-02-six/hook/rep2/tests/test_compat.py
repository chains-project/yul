from mylib import to_text, iteritems, string_types


def test_to_text_from_bytes():
    assert to_text(b"hello") == "hello"


def test_to_text_from_str():
    assert to_text("hello") == "hello"


def test_iteritems():
    d = {"a": 1, "b": 2}
    assert dict(iteritems(d)) == d


def test_string_types():
    assert isinstance("hello", string_types)
