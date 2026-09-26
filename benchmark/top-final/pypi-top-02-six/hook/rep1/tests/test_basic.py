from mylib import is_string, to_text


def test_is_string():
    assert is_string("hello")
    assert not is_string(123)


def test_to_text():
    assert to_text(b"hello") == "hello"
    assert to_text(123) == "123"
