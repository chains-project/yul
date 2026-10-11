import json

import httpx
import pytest
import respx

from api_fetcher.__main__ import main


@respx.mock
def test_cli_prints_json(capsys: pytest.CaptureFixture[str]) -> None:
    respx.get("https://api.example.com/ping").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    exit_code = main(["https://api.example.com/ping"])
    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == {"ok": True}


@respx.mock
def test_cli_reports_errors(capsys: pytest.CaptureFixture[str]) -> None:
    respx.get("https://api.example.com/bad").mock(
        return_value=httpx.Response(500)
    )
    exit_code = main(["https://api.example.com/bad"])
    assert exit_code == 1
    assert "error:" in capsys.readouterr().err


def test_cli_rejects_malformed_param() -> None:
    with pytest.raises(SystemExit):
        main(["--param", "no-equals", "https://api.example.com"])
