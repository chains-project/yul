from worldtime.cli import main


def test_now_prints_aware_iso(capsys):
    assert main(["now", "japan"]) == 0
    out = capsys.readouterr().out.strip()
    assert "+09:00" in out


def test_convert_command(capsys):
    assert main(["convert", "2024-03-10T07:00:00Z", "--to", "us-east"]) == 0
    assert "03:00:00" in capsys.readouterr().out


def test_regions_lists_expected(capsys):
    assert main(["regions"]) == 0
    out = capsys.readouterr().out
    assert "japan" in out and "Asia/Tokyo" in out
