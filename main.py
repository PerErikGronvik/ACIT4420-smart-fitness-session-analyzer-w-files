"""Load and organize the official Assignment II fitness CSV files."""

from pathlib import Path

from src import csv_validation as cv
from src import perdas as pe
from src.validation import SIGNAL_QUALITY_THRESHOLD, is_good_signal_quality


DATA_DIRECTORY = Path(__file__).resolve().parent / "data"


def main() -> None:
    """Load the CSV data, validate it, group observations, and summarize."""
    ld_profiles_rows = pe.read_csv(DATA_DIRECTORY / "participants.csv")
    ld_valid_sessions_rows = pe.read_csv(DATA_DIRECTORY / "fitness_sessions.csv")
    ld_invalid_sessions_rows = pe.read_csv(DATA_DIRECTORY / "fitness_sessions_invalid.csv")

    ld_rejected_records = []
    ld_rejected_records.extend(
        cv.validate_csv_rows("participants.csv", ld_profiles_rows, cv.PROFILE_FIELDS)
    )
    ld_rejected_records.extend(
        cv.validate_profile_ids("participants.csv", ld_profiles_rows)
    )
    ld_rejected_records.extend(
        cv.validate_csv_rows(
            "fitness_sessions.csv", ld_valid_sessions_rows, cv.SESSION_FIELDS
        )
    )
    ld_rejected_records.extend(
        cv.validate_csv_rows(
            "fitness_sessions_invalid.csv",
            ld_invalid_sessions_rows,
            cv.SESSION_FIELDS,
        )
    )

    ld_accepted_profile_rows = []
    for i_row_number, ld_profile_row in enumerate(ld_profiles_rows, start=2):
        b_shape_is_valid = cv.has_valid_csv_shape(
            ld_profile_row, cv.PROFILE_FIELDS
        )
        b_id_is_valid = cv.is_valid_participant_id(
            ld_profile_row.get("participant_id")
        )
        b_values_are_valid = cv.convert_and_validate_numeric_fields(
            "participants.csv",
            i_row_number,
            ld_profile_row,
            cv.PROFILE_NUMERIC_RULES,
            ld_rejected_records,
        )
        if b_shape_is_valid and b_id_is_valid and b_values_are_valid:
            ld_accepted_profile_rows.append(ld_profile_row)

    d_profiles_by_id = {
        ld_profile_row["participant_id"]: ld_profile_row
        for ld_profile_row in ld_accepted_profile_rows
    }
    ds_known_participant_ids = set(d_profiles_by_id)

    ld_accepted_valid_session_rows = []
    for s_source_name, ld_session_rows in (
        ("fitness_sessions.csv", ld_valid_sessions_rows),
        ("fitness_sessions_invalid.csv", ld_invalid_sessions_rows),
    ):
        ld_rejected_records.extend(
            cv.validate_session_ids(s_source_name, ld_session_rows)
        )
        ld_rejected_records.extend(
            cv.validate_session_participants(
                s_source_name, ld_session_rows, ds_known_participant_ids
            )
        )
        for i_row_number, ld_session_row in enumerate(ld_session_rows, start=2):
            b_shape_is_valid = cv.has_valid_csv_shape(
                ld_session_row, cv.SESSION_FIELDS
            )
            b_ids_are_valid = (
                cv.is_valid_session_id(ld_session_row.get("session_id"))
                and cv.is_valid_participant_id(
                    ld_session_row.get("participant_id")
                )
            )
            b_participant_is_known = (
                ld_session_row.get("participant_id") in ds_known_participant_ids
            )
            b_values_are_valid = cv.convert_and_validate_numeric_fields(
                s_source_name,
                i_row_number,
                ld_session_row,
                cv.SESSION_NUMERIC_RULES,
                ld_rejected_records,
            )
            if (
                s_source_name == "fitness_sessions.csv"
                and b_shape_is_valid
                and b_ids_are_valid
                and b_participant_is_known
                and b_values_are_valid
            ):
                ld_accepted_valid_session_rows.append(ld_session_row)

    d_sessions_by_id = {}
    for ld_session_row in ld_accepted_valid_session_rows:
        s_session_id = ld_session_row["session_id"]
        if s_session_id not in d_sessions_by_id:
            d_sessions_by_id[s_session_id] = {
                "participant": d_profiles_by_id[ld_session_row["participant_id"]],
                "observations": [],
                "usable_observations": [],
                "low_quality_observations": [],
            }
        d_session = d_sessions_by_id[s_session_id]
        d_session["observations"].append(ld_session_row)
        s_quality_bucket = (
            "usable_observations"
            if is_good_signal_quality(
                ld_session_row["signal_quality"], SIGNAL_QUALITY_THRESHOLD
            )
            else "low_quality_observations"
        )
        d_session[s_quality_bucket].append(ld_session_row)

    i_low_quality_observations = sum(
        len(d_session["low_quality_observations"])
        for d_session in d_sessions_by_id.values()
    )

    if ld_rejected_records:
        print("Rejected records:")
        for d_rejected_record in ld_rejected_records:
            print(
                f"  {d_rejected_record['source_file']} row "
                f"{d_rejected_record['row_number']}, "
                f"field {d_rejected_record['field']}: "
                f"{d_rejected_record['reason']}"
            )

    print(
        f"Read {len(ld_profiles_rows)} participant profiles, "
        f"accepted {len(ld_accepted_valid_session_rows)} valid observations "
        f"across {len(d_sessions_by_id)} sessions; "
        f"{i_low_quality_observations} observations below the "
        f"{SIGNAL_QUALITY_THRESHOLD} signal-quality threshold are excluded "
        "from analysis. Read "
        f"{len(ld_invalid_sessions_rows)} intentionally invalid session rows "
        f"({len(ld_rejected_records)} rejection records)."
    )


if __name__ == "__main__":
    main()

