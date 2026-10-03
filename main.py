


"""Load the official Assignment II fitness CSV files."""

from pathlib import Path

import perdas as pe


DATA_DIRECTORY = Path(__file__).resolve().parent / "data"


def main() -> None:
    """Read the three official inputs and report their row counts."""
    ld_profiles_rows = pe.read_csv(DATA_DIRECTORY / "participants.csv")
    ld_valid_sessions_rows = pe.read_csv(DATA_DIRECTORY / "fitness_sessions.csv")
    ld_invalid_sessions_rows = pe.read_csv(DATA_DIRECTORY / "fitness_sessions_invalid.csv")

    for ld_profile_row in ld_profiles_rows:
        ld_profile_row["baseline_heart_rate"] = int(
            ld_profile_row["baseline_heart_rate"]
        )
        ld_profile_row["baseline_skin_response"] = float(
            ld_profile_row["baseline_skin_response"]
        )
        ld_profile_row["baseline_temperature"] = float(
            ld_profile_row["baseline_temperature"]
        )

    for ld_session_row in ld_valid_sessions_rows:
        ld_session_row["timestamp"] = int(ld_session_row["timestamp"])
        ld_session_row["heart_rate"] = int(ld_session_row["heart_rate"])
        ld_session_row["skin_response"] = float(ld_session_row["skin_response"])
        ld_session_row["temperature"] = float(ld_session_row["temperature"])
        ld_session_row["activity_level"] = float(ld_session_row["activity_level"])
        ld_session_row["signal_quality"] = float(ld_session_row["signal_quality"])

    print(
        "Read CSV data rows: "
        f"{len(ld_profiles_rows)} participant profiles, "
        f"{len(ld_valid_sessions_rows)} valid session rows, "
        f"{len(ld_invalid_sessions_rows)} intentionally invalid session rows."
    )


if __name__ == "__main__":
    main()

