"""Small CSV-reading helpers for the Perdas assignment project."""

import csv
from pathlib import Path


def read_csv(
    csv_path: Path,
) -> list[dict[str | None, str | list[str] | None]]:
    """Read CSV rows as dictionaries without converting or validating values."""
    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))
