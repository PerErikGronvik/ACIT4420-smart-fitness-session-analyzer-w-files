


"""Load the official Assignment II fitness CSV files."""

from pathlib import Path

import perdas as pe


DATA_DIRECTORY = Path(__file__).resolve().parent / "data"


def main() -> None:
    """Read the three official inputs and report their row counts."""
    ld_profiles = pe.read_csv(DATA_DIRECTORY / "participants.csv")
    ld_valid_sessions = pe.read_csv(DATA_DIRECTORY / "fitness_sessions.csv")
    ld_invalid_sessions = pe.read_csv(DATA_DIRECTORY / "fitness_sessions_invalid.csv")
    print(
        "Read CSV data rows: "
        f"{len(ld_profiles)} participant profiles, "
        f"{len(ld_valid_sessions)} valid session rows, "
        f"{len(ld_invalid_sessions)} intentionally invalid session rows."
    )


if __name__ == "__main__":
    main()

