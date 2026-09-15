from mylib.compat import to_text, iter_items


def test_to_text_decodes_bytes():
    assert to_text(b"hello") == "hello"


def test_to_text_passes_through_str():
    assert to_text("hello") == "hello"


def test_iter_items():
    assert dict(iter_items({"a": 1})) == {"a": 1}
