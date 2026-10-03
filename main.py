"""Load the official Assignment II fitness CSV files."""

import re
from pathlib import Path

import perdas as pe


DATA_DIRECTORY = Path(__file__).resolve().parent / "data"

PROFILE_FIELDS = [
    "participant_id",
    "name",
    "baseline_heart_rate",
    "baseline_skin_response",
    "baseline_temperature",
]
SESSION_FIELDS = [
    "session_id",
    "participant_id",
    "timestamp",
    "heart_rate",
    "skin_response",
    "temperature",
    "activity_level",
    "signal_quality",
]

# Validation helpers for participant and session IDs.
def is_valid_participant_id(s_identifier: object) -> bool:
    """Return whether a participant ID is P followed by exactly three digits."""
    return (
        isinstance(s_identifier, str)
        and re.fullmatch(r"P[0-9]{3}", s_identifier) is not None
    )

# Validation helper for session IDs.
def is_valid_session_id(s_identifier: object) -> bool:
    """Return whether a session ID matches FIT-YYYY-NNN."""
    return (
        isinstance(s_identifier, str)
        and re.fullmatch(r"FIT-[0-9]{4}-[0-9]{3}", s_identifier) is not None
    )


def validate_csv_rows(
    s_source_name: str,
    ld_csv_rows: list[dict[str | None, str | list[str] | None]],
    ls_expected_fields: list[str],
) -> list[str]:
    """Report missing required fields and row lengths that do not match the schema."""
    ld_validation_errors = []
    i_expected_length = len(ls_expected_fields)

    for i_row_number, ld_csv_row in enumerate(ld_csv_rows, start=2):
        for s_field in ls_expected_fields:
            s_value = ld_csv_row.get(s_field)
            if s_value is None or (isinstance(s_value, str) and not s_value.strip()):
                ld_validation_errors.append(
                    f"{s_source_name} row {i_row_number}: missing required field "
                    f"{s_field}."
                )

        i_actual_length = sum(
            s_field in ld_csv_row and ld_csv_row[s_field] is not None
            for s_field in ld_csv_row
            if s_field is not None
        )
        v_extra_fields = ld_csv_row.get(None)
        if isinstance(v_extra_fields, list):
            i_actual_length += len(v_extra_fields)

        if i_actual_length != i_expected_length:
            ld_validation_errors.append(
                f"{s_source_name} row {i_row_number}: unexpected row length; "
                f"found {i_actual_length} fields, expected {i_expected_length}."
            )

        ls_unexpected_fields = [
            s_field
            for s_field in ld_csv_row
            if s_field is not None and s_field not in ls_expected_fields
        ]
        if ls_unexpected_fields:
            ld_validation_errors.append(
                f"{s_source_name} row {i_row_number}: unexpected fields "
                f"{ls_unexpected_fields}."
            )

    return ld_validation_errors


def main() -> None:
    """Read the three official inputs and report their row counts."""
    ld_identifier_errors = []

    # Read the CSV files into lists of dictionaries.
    ld_profiles_rows = pe.read_csv(DATA_DIRECTORY / "participants.csv")
    ld_valid_sessions_rows = pe.read_csv(DATA_DIRECTORY / "fitness_sessions.csv")
    ld_invalid_sessions_rows = pe.read_csv(DATA_DIRECTORY / "fitness_sessions_invalid.csv")

    ld_structure_errors = []
    ld_structure_errors.extend(
        validate_csv_rows("participants.csv", ld_profiles_rows, PROFILE_FIELDS)
    )
    ld_structure_errors.extend(
        validate_csv_rows("fitness_sessions.csv", ld_valid_sessions_rows, SESSION_FIELDS)
    )
    ld_structure_errors.extend(
        validate_csv_rows(
            "fitness_sessions_invalid.csv", ld_invalid_sessions_rows, SESSION_FIELDS
        )
    )

    print("\nDEBUG: CSV structure validation")
    if ld_structure_errors:
        for s_structure_error in ld_structure_errors:
            print(f"  {s_structure_error}")
    else:
        print("  All rows have the required fields and expected number of columns.")

    # Validate participant IDs in the profiles CSV.
    for i_row_number, ld_profile_row in enumerate(ld_profiles_rows, start=2):
        s_participant_id = ld_profile_row["participant_id"]
        if not is_valid_participant_id(s_participant_id):
            ld_identifier_errors.append(
                f"participants.csv row {i_row_number}: invalid participant_id "
                f"{s_participant_id!r}; expected P followed by three digits."
            )
    # Validate session IDs in the fitness sessions CSVs.
    for s_source_name, ld_session_rows in (
        ("fitness_sessions.csv", ld_valid_sessions_rows),
        ("fitness_sessions_invalid.csv", ld_invalid_sessions_rows),
    ):
        for i_row_number, ld_session_row in enumerate(ld_session_rows, start=2):
            s_session_id = ld_session_row["session_id"]
            s_participant_id = ld_session_row["participant_id"]
            if not is_valid_session_id(s_session_id):
                ld_identifier_errors.append(
                    f"{s_source_name} row {i_row_number}: invalid session_id "
                    f"{s_session_id!r}; expected FIT-YYYY-NNN."
                )
            if not is_valid_participant_id(s_participant_id):
                ld_identifier_errors.append(
                    f"{s_source_name} row {i_row_number}: invalid participant_id "
                    f"{s_participant_id!r}; expected P followed by three digits."
                )

    print("\nDEBUG: Identifier validation")
    if ld_identifier_errors:
        for s_identifier_error in ld_identifier_errors:
            print(f"  {s_identifier_error}")
    else:
        print("  All participant and session IDs match their required formats.")
    
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
#    for ld_session_row in ld_invalid_sessions_rows:
#        ld_session_row["timestamp"] = int(ld_session_row["timestamp"])
#        ld_session_row["heart_rate"] = int(ld_session_row["heart_rate"])
#        ld_session_row["skin_response"] = float(ld_session_row["skin_response"])
#        ld_session_row["temperature"] = float(ld_session_row["temperature"])
#        ld_session_row["activity_level"] = float(ld_session_row["activity_level"])
#        ld_session_row["signal_quality"] = float(ld_session_row["signal_quality"])

    # Organize participant profiles by participant ID.
    d_profiles_by_id = {
        ld_profile_row["participant_id"]: ld_profile_row
        for ld_profile_row in ld_profiles_rows
        if is_valid_participant_id(ld_profile_row["participant_id"])
    }
    # Organize valid sessions by session ID.
    d_sessions_by_id = {}
    for ld_session_row in ld_valid_sessions_rows:
        s_session_id = ld_session_row["session_id"]
        if not is_valid_session_id(s_session_id):
            continue
        if not is_valid_participant_id(ld_session_row["participant_id"]):
            continue
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

#    print("\nDEBUG: Participant profiles")
#    for s_participant_id, d_profile in d_profiles_by_id.items():
#        print(
#            f"{s_participant_id} - {d_profile['name']}: "
#            f"baseline heart rate={d_profile['baseline_heart_rate']}, "
#            f"skin response={d_profile['baseline_skin_response']}, "
#            f"temperature={d_profile['baseline_temperature']}"
#        )
#
#    print("\nDEBUG: Valid sessions and observations")
#    for s_session_id, d_session in d_sessions_by_id.items():
#        d_profile = d_session["participant"]
#        print(
#            f"{s_session_id} -> {d_profile['participant_id']} "
#            f"({d_profile['name']}), "
#            f"{len(d_session['observations'])} observations"
#        )
#        for d_observation in d_session["observations"]:
#            print(
#                f"  timestamp={d_observation['timestamp']}, "
#                f"participant_id={d_observation['participant_id']}, "
#                f"heart_rate={d_observation['heart_rate']}, "
#                f"skin_response={d_observation['skin_response']}, "
#                f"temperature={d_observation['temperature']}, "
#                f"activity_level={d_observation['activity_level']}, "
#                f"signal_quality={d_observation['signal_quality']}"
#            )


if __name__ == "__main__":
    main()

