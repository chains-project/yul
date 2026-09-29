from worldclock.cli import DEFAULT_ZONES, main


def test_now_lists_default_zones(capsys):
    assert main([]) == 0
    out = capsys.readouterr().out
    for zone in DEFAULT_ZONES:
        assert zone in out


def test_now_lists_explicit_zones(capsys):
    assert main(["now", "-z", "UTC", "-z", "Asia/Tokyo"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 2
    assert lines[0].startswith("UTC")
    assert lines[1].startswith("Asia/Tokyo")


def test_convert_subcommand(capsys):
    assert main(["convert", "2024-03-10T07:00:00Z", "-z", "America/New_York"]) == 0
    assert capsys.readouterr().out.strip() == "2024-03-10T03:00:00-04:00"


def test_list_subcommand_filters(capsys):
    assert main(["list", "Asia"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines
    assert all(line.startswith("Asia/") for line in lines)
