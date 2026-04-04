"""Persistent apartment search profile stored as a Markdown file."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

_DEFAULT_TEMPLATE = """\
# Apartment-Suchprofil

## Grunddaten
- Zimmer: -
- Flaeche (qm): -
- Budget (EUR): -
- Kaltmiete/Warmmiete: -

## Lage
- Stadt/Region: -
- Stadtteil: -
- Naehe zu: -

## Ausstattung
- Balkon/Terrasse: -
- Parkplatz/Garage: -
- Einbaukueche: -
- Aufzug: -
- Keller: -
- Waschmaschinenanschluss: -

## Stil & Zustand
- Typ (Altbau/Neubau): -
- Renoviert: -
- Etage: -

## Sonstiges
- Haustiere erlaubt: -
- Besondere Wuensche: -

## Notizen
"""


class ProfileStore:
    """Read and write the apartment search profile on disk."""

    def __init__(self, path: Path) -> None:
        """Initialise the store with the file *path*."""
        self._path = path

    def read(self) -> str:
        """Return the current profile or the starter template if none exists."""
        if self._path.exists():
            return self._path.read_text(encoding="utf-8")
        return _DEFAULT_TEMPLATE

    def write(self, content: str) -> str:
        """Overwrite the profile with *content* and return a confirmation."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(content, encoding="utf-8")
        return "Profile updated successfully."
