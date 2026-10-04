"""Application workflow for loading, validating, analyzing, and reporting CSV data."""

import csv
from pathlib import Path

from src import csv_validation as cv
from src import perdas as pe
from src.classifier import SessionClassifier
from src.participant import Participant
from src.report import generate_session_report, generate_summary_table, print_session_report, write_analysis_report_txt, write_analysis_summary_csv, write_rejected_records_txt
from src.session import Session
from src.validation import MINIMUM_USABLE_OBSERVATIONS, SIGNAL_QUALITY_THRESHOLD, is_good_signal_quality


def load_input_rows(profile_file: Path, valid_sessions_file: Path, invalid_sessions_file: Path):
    """Load required profiles and each session file, continuing if a session file is unavailable."""
    try:
        ld_profiles_rows = pe.read_csv(profile_file)
    except (FileNotFoundError, PermissionError, csv.Error) as error:
        print(f"Could not load required participant profiles: {error}")
        return None

    try:
        ld_valid_sessions_rows = pe.read_csv(valid_sessions_file)
    except (FileNotFoundError, PermissionError, csv.Error) as error:
        print(f"Could not load {valid_sessions_file.name}; continuing without it: {error}")
        ld_valid_sessions_rows = []

    try:
        ld_invalid_sessions_rows = pe.read_csv(invalid_sessions_file)
    except (FileNotFoundError, PermissionError, csv.Error) as error:
        print(f"Could not load {invalid_sessions_file.name}; continuing without it: {error}")
        ld_invalid_sessions_rows = []

    return ld_profiles_rows, ld_valid_sessions_rows, ld_invalid_sessions_rows


def build_participants(profile_rows: list, profile_file: Path, rejected_records: list) -> dict[str, Participant]:
    """Validate profile rows and create participant objects from accepted rows."""
    rejected_records.extend(
        cv.validate_csv_rows(profile_file.name, profile_rows, cv.PROFILE_FIELDS)
    )
    rejected_records.extend(cv.validate_profile_ids(profile_file.name, profile_rows))

    ld_accepted_profile_rows = []
    for i_row_number, ld_profile_row in enumerate(profile_rows, start=2):
        b_shape_is_valid = cv.has_valid_csv_shape(ld_profile_row, cv.PROFILE_FIELDS)
        b_id_is_valid = cv.is_valid_participant_id(ld_profile_row.get("participant_id"))
        b_values_are_valid = cv.convert_and_validate_numeric_fields(
            profile_file.name,
            i_row_number,
            ld_profile_row,
            cv.PROFILE_NUMERIC_RULES,
            rejected_records,
        )
        if b_shape_is_valid and b_id_is_valid and b_values_are_valid:
            ld_accepted_profile_rows.append(ld_profile_row)

    d_profile_row_numbers = {
        id(ld_profile_row): i_row_number
        for i_row_number, ld_profile_row in enumerate(profile_rows, start=2)
    }
    d_participants_by_id = {}
    for ld_profile_row in ld_accepted_profile_rows:
        try:
            d_participant = Participant(
                name=ld_profile_row["name"],
                resting_heart_rate=ld_profile_row["baseline_heart_rate"],
                participant_id=ld_profile_row["participant_id"],
                baseline_skin_response=ld_profile_row["baseline_skin_response"],
                baseline_temperature=ld_profile_row["baseline_temperature"],
            )
        except ValueError as error:
            rejected_records.append(cv.create_validation_issue(
                profile_file.name,
                d_profile_row_numbers[id(ld_profile_row)],
                "baseline_heart_rate",
                str(error),
            ))
            continue
        d_participants_by_id[ld_profile_row["participant_id"]] = d_participant

    return d_participants_by_id


def validate_session_rows(valid_rows: list, invalid_rows: list, valid_file: Path, invalid_file: Path, known_participant_ids: set[str], rejected_records: list) -> list:
    """Validate both session inputs and return only acceptable analysis rows."""
    ld_accepted_rows = []
    for s_source_name, ld_session_rows, b_is_valid_input in (
        (valid_file.name, valid_rows, True),
        (invalid_file.name, invalid_rows, False),
    ):
        rejected_records.extend(cv.validate_csv_rows(s_source_name, ld_session_rows, cv.SESSION_FIELDS))
        rejected_records.extend(
            cv.validate_session_ids(s_source_name, ld_session_rows)
        )
        rejected_records.extend(
            cv.validate_session_participants(
                s_source_name, ld_session_rows, known_participant_ids, valid_file.name
            )
        )
        for i_row_number, ld_session_row in enumerate(ld_session_rows, start=2):
            b_shape_is_valid = cv.has_valid_csv_shape(ld_session_row, cv.SESSION_FIELDS)
            b_ids_are_valid = (
                cv.is_valid_session_id(ld_session_row.get("session_id"))
                and cv.is_valid_participant_id(ld_session_row.get("participant_id"))
            )
            b_participant_is_known = ld_session_row.get("participant_id") in known_participant_ids
            b_values_are_valid = cv.convert_and_validate_numeric_fields(
                s_source_name,
                i_row_number,
                ld_session_row,
                cv.SESSION_NUMERIC_RULES,
                rejected_records,
            )
            if b_is_valid_input and b_shape_is_valid and b_ids_are_valid and b_participant_is_known and b_values_are_valid:
                ld_accepted_rows.append(ld_session_row)

    return ld_accepted_rows


def build_sessions(session_rows: list, source_session_rows: list, valid_sessions_file: Path, participants_by_id: dict[str, Participant], rejected_records: list) -> dict[str, Session]:
    """Group validated observations into Session objects with linked participants."""
    d_session_row_numbers = {
        id(ld_session_row): i_row_number
        for i_row_number, ld_session_row in enumerate(source_session_rows, start=2)
    }
    d_sessions_by_id: dict[str, Session] = {}

    for ld_session_row in session_rows:
        s_session_id = ld_session_row["session_id"]
        if s_session_id not in d_sessions_by_id:
            d_sessions_by_id[s_session_id] = Session(
                participants_by_id[ld_session_row["participant_id"]],
                session_id=s_session_id,
            )
        b_observation_added, s_add_message = d_sessions_by_id[s_session_id].add_observation(ld_session_row)
        if not b_observation_added:
            rejected_records.append(cv.create_validation_issue(
                valid_sessions_file.name,
                d_session_row_numbers[id(ld_session_row)],
                "observation",
                s_add_message,
            ))

    return d_sessions_by_id


def analyze_and_write_reports(sessions_by_id: dict[str, Session], rejected_records: list, output_directory: Path, profiles_count: int, invalid_rows_count: int) -> None:
    """Classify sessions, write reports, and print the completion summary."""
    ld_analysis_results = []
    for d_session in sessions_by_id.values():
        d_classification_result = SessionClassifier.classify_session(d_session)
        ld_analysis_results.append(generate_session_report(d_session, d_classification_result))
        print_session_report(d_session, d_classification_result)

    print("Session comparison summary:")
    print(generate_summary_table(ld_analysis_results))
    summary_path = write_analysis_summary_csv(ld_analysis_results, output_directory)
    report_path = write_analysis_report_txt(ld_analysis_results, output_directory)
    rejected_path = write_rejected_records_txt(rejected_records, output_directory)

    i_low_quality_observations = sum(
        len(d_session.observations)
        - len(d_session.get_good_quality_observations(SIGNAL_QUALITY_THRESHOLD))
        for d_session in sessions_by_id.values()
    )
    i_insufficient_sessions = sum(
        len(d_session.get_good_quality_observations(SIGNAL_QUALITY_THRESHOLD))
        < MINIMUM_USABLE_OBSERVATIONS
        for d_session in sessions_by_id.values()
    )
    if rejected_records:
        print("Rejected records:")
        for d_rejected_record in rejected_records:
            print(
                f"  {d_rejected_record['source_file']} row "
                f"{d_rejected_record['row_number']}, "
                f"field {d_rejected_record['field']}: "
                f"{d_rejected_record['reason']}"
            )

    i_accepted_session_rows = sum(
        len(d_session.observations) for d_session in sessions_by_id.values()
    )
    i_rejected_rows = len({
        (d_record["source_file"], d_record["row_number"])
        for d_record in rejected_records
    })
    print(
        f"Completed: {profiles_count + i_accepted_session_rows} accepted rows "
        f"({profiles_count} profiles, {i_accepted_session_rows} session observations), "
        f"{i_rejected_rows} rejected CSV rows, {len(sessions_by_id)} sessions. "
        f"{i_low_quality_observations} low-quality observations were excluded "
        f"from analysis; {i_insufficient_sessions} sessions had fewer than "
        f"{MINIMUM_USABLE_OBSERVATIONS} usable observations."
    )
    print(f"Created reports: {summary_path}, {report_path}, {rejected_path}")


def run_application(profile_file: Path, valid_sessions_file: Path, invalid_sessions_file: Path, output_directory: Path, verbose: bool = False) -> None:
    """Coordinate the CSV-to-analysis workflow and its focused processing steps."""
    cv.VERBOSE = verbose
    output_directory.mkdir(parents=True, exist_ok=True)
    d_input_rows = load_input_rows(profile_file, valid_sessions_file, invalid_sessions_file)
    if d_input_rows is None:
        return

    ld_profiles_rows, ld_valid_sessions_rows, ld_invalid_sessions_rows = d_input_rows
    ld_rejected_records = []
    d_participants_by_id = build_participants(ld_profiles_rows, profile_file, ld_rejected_records)
    ld_accepted_session_rows = validate_session_rows(
        ld_valid_sessions_rows,
        ld_invalid_sessions_rows,
        valid_sessions_file,
        invalid_sessions_file,
        set(d_participants_by_id),
        ld_rejected_records,
    )
    d_sessions_by_id = build_sessions(
        ld_accepted_session_rows,
        ld_valid_sessions_rows,
        valid_sessions_file,
        d_participants_by_id,
        ld_rejected_records,
    )
    analyze_and_write_reports(
        d_sessions_by_id,
        ld_rejected_records,
        output_directory,
        len(d_participants_by_id),
        len(ld_invalid_sessions_rows),
    )
