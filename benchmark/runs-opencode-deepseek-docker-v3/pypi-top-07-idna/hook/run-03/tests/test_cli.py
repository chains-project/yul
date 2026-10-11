from idn_toolkit.cli import main


def test_cli_encode(capsys):
    assert main(["encode", "münchen.de"]) == 0
    assert capsys.readouterr().out.strip() == "xn--mnchen-3ya.de"


def test_cli_decode(capsys):
    assert main(["decode", "xn--mnchen-3ya.de"]) == 0
    assert capsys.readouterr().out.strip() == "münchen.de"


def test_cli_reads_stdin(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", type("F", (), {"read": lambda self: "例え.テスト\n"})())
    assert main(["encode"]) == 0
    assert capsys.readouterr().out.strip() == "xn--r8jz45g.xn--zckzah"


def test_cli_invalid_domain(capsys):
    assert main(["encode", "bad..name"]) == 1
    assert "error:" in capsys.readouterr().err
