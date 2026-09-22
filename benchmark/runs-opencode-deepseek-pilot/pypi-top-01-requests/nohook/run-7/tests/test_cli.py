"""Tests for the command line interface."""

import json

import responses

from rest_fetcher.cli import main


@responses.activate
def test_cli_prints_json(capsys):
    responses.add(
        responses.GET,
        "https://api.example.com/items",
        json={"ok": True},
        status=200,
    )

    exit_code = main(["https://api.example.com/items"])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {"ok": True}


@responses.activate
def test_cli_reports_errors(capsys):
    responses.add(
        responses.GET,
        "https://api.example.com/items",
        status=404,
    )

    exit_code = main(["https://api.example.com/items"])

    assert exit_code == 1
    assert "error" in capsys.readouterr().err
