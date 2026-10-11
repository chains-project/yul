from idna_tool.__main__ import main


def test_cli_encode(capsys):
    assert main(["encode", "例え.テスト"]) == 0
    assert capsys.readouterr().out.strip() == "xn--r8jz45g.xn--zckzah"


def test_cli_decode(capsys):
    assert main(["decode", "xn--r8jz45g.xn--zckzah"]) == 0
    assert capsys.readouterr().out.strip() == "例え.テスト"


def test_cli_invalid_domain(capsys):
    assert main(["encode", "--", "-leading-hyphen"]) == 1
    assert capsys.readouterr().err.startswith("error:")
