from mylib import to_text, iteritems


def test_to_text():
    assert to_text(123) == "123"
    assert to_text(u"already") == u"already"


def test_iteritems():
    d = {"a": 1, "b": 2}
    assert dict(iteritems(d)) == d
