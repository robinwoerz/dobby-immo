"""Tests for the apartment profile store."""

from __future__ import annotations

from typing import TYPE_CHECKING

from dobby_immo.profile import _DEFAULT_TEMPLATE, ProfileStore

if TYPE_CHECKING:
    from pathlib import Path


def test_read_returns_template_when_missing(tmp_path: Path) -> None:
    store = ProfileStore(tmp_path / "missing" / "profile.md")
    assert store.read() == _DEFAULT_TEMPLATE


def test_write_creates_dirs_and_file(tmp_path: Path) -> None:
    path = tmp_path / "sub" / "dir" / "profile.md"
    store = ProfileStore(path)
    result = store.write("# Test")
    assert path.exists()
    assert path.read_text(encoding="utf-8") == "# Test"
    assert "updated" in result.lower()


def test_read_after_write(tmp_path: Path) -> None:
    store = ProfileStore(tmp_path / "profile.md")
    store.write("# My Profile\n- Zimmer: 3")
    assert store.read() == "# My Profile\n- Zimmer: 3"


def test_write_overwrites_existing(tmp_path: Path) -> None:
    store = ProfileStore(tmp_path / "profile.md")
    store.write("v1")
    store.write("v2")
    assert store.read() == "v2"
