"""Tests for dobby_immo.main."""

from dobby_immo.main import main


def test_main(capsys):
    main()
    captured = capsys.readouterr()
    assert "Dobby Immo" in captured.out
