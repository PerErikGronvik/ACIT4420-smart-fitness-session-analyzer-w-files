"""Load the official Assignment II fitness CSV files."""

from pathlib import Path

import perdas as pe


DATA_DIRECTORY = Path(__file__).resolve().parent / "data"


def main() -> None:
    """Read the three official inputs and report their row counts."""

    # Read the CSV files into lists of dictionaries.
    ld_profiles_rows = pe.read_csv(DATA_DIRECTORY / "participants.csv")
    ld_valid_sessions_rows = pe.read_csv(DATA_DIRECTORY / "fitness_sessions.csv")
    ld_invalid_sessions_rows = pe.read_csv(DATA_DIRECTORY / "fitness_sessions_invalid.csv")
    
    # Convert baseline values to appropriate types.
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

    # Convert valid session values to appropriate types.
    for ld_session_row in ld_valid_sessions_rows:
        ld_session_row["timestamp"] = int(ld_session_row["timestamp"])
        ld_session_row["heart_rate"] = int(ld_session_row["heart_rate"])
        ld_session_row["skin_response"] = float(ld_session_row["skin_response"])
        ld_session_row["temperature"] = float(ld_session_row["temperature"])
        ld_session_row["activity_level"] = float(ld_session_row["activity_level"])
        ld_session_row["signal_quality"] = float(ld_session_row["signal_quality"])

    # Convert invalid session values to appropriate types.

    # Organize participant profiles by participant ID.
    d_profiles_by_id = {
        ld_profile_row["participant_id"]: ld_profile_row
        for ld_profile_row in ld_profiles_rows
    }
    # Organize valid sessions by session ID.
    d_sessions_by_id = {}
    for ld_session_row in ld_valid_sessions_rows:
        s_session_id = ld_session_row["session_id"]
        if s_session_id not in d_sessions_by_id:
            d_sessions_by_id[s_session_id] = {
                "participant": d_profiles_by_id[ld_session_row["participant_id"]],
                "observations": [],
            }
        d_sessions_by_id[s_session_id]["observations"].append(ld_session_row)

    # Report the number of rows read from each CSV file.
    print(
        "Read CSV data rows: "
        f"{len(ld_profiles_rows)} participant profiles, "
        f"{len(ld_valid_sessions_rows)} valid session rows, "
        f"{len(d_sessions_by_id)} valid sessions, "
        f"{len(ld_invalid_sessions_rows)} intentionally invalid session rows."
    )


if __name__ == "__main__":
    main()

