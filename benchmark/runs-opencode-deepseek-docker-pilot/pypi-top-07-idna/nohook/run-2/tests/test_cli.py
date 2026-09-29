import io

from idna_toolkit.cli import main


def test_encode_arguments(capsys):
    assert main(["encode", "例え.テスト", "münchen.de"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "xn--r8jz45g.xn--zckzah",
        "xn--mnchen-3ya.de",
    ]


def test_decode_arguments(capsys):
    assert main(["decode", "xn--r8jz45g.xn--zckzah"]) == 0
    assert capsys.readouterr().out.strip() == "例え.テスト"


def test_reads_from_stdin(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("例え.テスト\n\nmünchen.de\n"))
    assert main(["encode"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "xn--r8jz45g.xn--zckzah",
        "xn--mnchen-3ya.de",
    ]


def test_encode_uts46(capsys):
    assert main(["encode", "--uts46", "BÜCHER.example"]) == 0
    assert capsys.readouterr().out.strip() == "xn--bcher-kva.example"


def test_errors_go_to_stderr(capsys):
    assert main(["encode", "example.com", "例え..テスト"]) == 1
    captured = capsys.readouterr()
    assert captured.out.strip() == "example.com"
    assert "error" in captured.err
