"""Small CSV-reading helpers for the Perdas assignment project."""

import csv
from pathlib import Path


def read_csv(
    csv_path: Path,
) -> list[dict[str | None, str | list[str] | None]]:
    """Read CSV rows as dictionaries without converting or validating values."""
    try:
        with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
            return list(csv.DictReader(csv_file))
    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"CSV input file was not found: {csv_path}"
        ) from error
    except PermissionError as error:
        raise PermissionError(
            f"Permission denied while reading CSV input file: {csv_path}"
        ) from error
    except csv.Error as error:
        raise csv.Error(
            f"Could not parse CSV input file {csv_path}: {error}"
        ) from error