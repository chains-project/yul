from api_client.cli import main


def test_main_prints_json(httpx_mock, monkeypatch, capsys):
    monkeypatch.setenv("API_BASE_URL", "https://api.example.com")
    httpx_mock.add_response(url="https://api.example.com/users", json={"count": 2})

    exit_code = main(["users"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"count": 2' in captured.out


def test_main_accepts_base_url_flag(httpx_mock, monkeypatch, capsys):
    monkeypatch.delenv("API_BASE_URL", raising=False)
    httpx_mock.add_response(url="https://other.example.com/ping", json={"ok": True})

    exit_code = main(["--base-url", "https://other.example.com", "/ping"])

    assert exit_code == 0


def test_main_reports_api_error(httpx_mock, monkeypatch, capsys):
    monkeypatch.setenv("API_BASE_URL", "https://api.example.com")
    httpx_mock.add_response(status_code=500)

    exit_code = main(["/boom"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "error:" in captured.err


def test_main_requires_base_url(capsys):
    exit_code = main(["/users"])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "API_BASE_URL" in captured.err


def test_main_rejects_bad_param(capsys):
    exit_code = main(["path", "-p", "oops"])

    assert exit_code == 2
