import pytest

from mytool import __version__
from mytool.cli import build_parser, main


def test_parser_requires_a_command():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_greet_defaults(capsys):
    assert main(["greet"]) == 0
    assert capsys.readouterr().out == "Hello, world!\n"


def test_greet_options(capsys):
    assert main(["greet", "-n", "Ada", "-c", "2", "--shout"]) == 0
    assert capsys.readouterr().out == "HELLO, ADA!\nHELLO, ADA!\n"


def test_greet_quiet_suppresses_output(capsys):
    assert main(["greet", "--quiet"]) == 0
    assert capsys.readouterr().out == ""


def test_greet_verbose_before_subcommand(capsys):
    assert main(["-v", "greet", "-n", "Ada"]) == 0
    captured = capsys.readouterr()
    assert "greeting 'Ada'" in captured.err
    assert captured.out == "Hello, Ada!\n"


def test_greet_verbose_after_subcommand(capsys):
    assert main(["greet", "-v", "-n", "Ada"]) == 0
    captured = capsys.readouterr()
    assert "greeting 'Ada'" in captured.err


def test_greet_rejects_non_positive_count():
    with pytest.raises(SystemExit) as excinfo:
        main(["greet", "--count", "0"])
    assert excinfo.value.code == 2
