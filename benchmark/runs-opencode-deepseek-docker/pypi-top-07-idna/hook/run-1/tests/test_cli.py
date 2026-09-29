from idnatool.cli import main


def test_cli_encode(capsys):
    assert main(["encode", "bücher.example"]) == 0
    assert capsys.readouterr().out.strip() == "xn--bcher-kva.example"


def test_cli_decode(capsys):
    assert main(["decode", "xn--bcher-kva.example"]) == 0
    assert capsys.readouterr().out.strip() == "bücher.example"


def test_cli_multiple_domains(capsys):
    assert main(["encode", "a.example", "bücher.example"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "a.example",
        "xn--bcher-kva.example",
    ]


def test_cli_profile_flag(capsys):
    assert main(["encode", "--profile", "uts46", "Bücher.example"]) == 0
    assert capsys.readouterr().out.strip() == "xn--bcher-kva.example"


def test_cli_error_returns_nonzero(capsys):
    assert main(["encode", "foo..bar"]) == 1
    assert "idnatool:" in capsys.readouterr().err
