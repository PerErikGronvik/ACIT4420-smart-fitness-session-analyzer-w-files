"""Load and organize the official Assignment II fitness CSV files."""

import argparse
import csv
from pathlib import Path

from src import csv_validation as cv
from src import perdas as pe
from src.classifier import SessionClassifier
from src.participant import Participant
from src.report import (generate_session_report, generate_summary_table, print_session_report, write_analysis_report_txt, write_analysis_summary_csv, write_rejected_records_txt,)
from src.session import Session
from src.validation import MINIMUM_USABLE_OBSERVATIONS, SIGNAL_QUALITY_THRESHOLD, is_good_signal_quality


DATA_DIRECTORY = Path(__file__).resolve().parent / "data"
PROFILE_FILE = DATA_DIRECTORY / "participants.csv"
OUTPUT_DIRECTORY = Path(__file__).resolve().parent / "output"


def create_argument_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for CSV input and report output paths."""
    parser = argparse.ArgumentParser(
        description=(
            "Validate fitness-session CSV rows, analyze sessions that pass "
            "validation, and write summary, explanation, and rejected-row reports. "
            "The participant profile file is always read from "
            "data/participants.csv relative to this program."
        ),
        epilog=(
            "Examples:\n"
            "  python main.py\n"
            "  python main.py --sessions data/my_sessions.csv\n"
            "  python main.py --sessions data/my_sessions.csv "
            "--invalid-sessions data/bad_rows.csv --output-dir results\n\n"
            "Reports created in the output directory: analysis_summary.csv "
            "(one data row per analyzed session), analysis_report.txt "
            "(readable explanations of the results), and rejected_records.txt "
            "(invalid CSV rows and reasons). Rows from --invalid-sessions are "
            "checked and reported, but are not included in session analysis."
        ),
    )
    parser.add_argument(
        "--sessions",
        "--valid-sessions",
        dest="valid_sessions",
        nargs="?",
        type=Path,
        const=DATA_DIRECTORY / "fitness_sessions.csv",
        default=DATA_DIRECTORY / "fitness_sessions.csv",
        help=(
            "CSV file containing session observations to analyze. Use this to "
            "replace data/fitness_sessions.csv; if the option is written without "
            "a path, the default file is used."
        ),
    )
    parser.add_argument(
        "--invalid-sessions",
        nargs="?",
        type=Path,
        const=DATA_DIRECTORY / "fitness_sessions_invalid.csv",
        default=DATA_DIRECTORY / "fitness_sessions_invalid.csv",
        help=(
            "CSV file of deliberately invalid or test rows to validate and list "
            "in rejected_records.txt. These rows are not analyzed. If omitted, "
            "data/fitness_sessions_invalid.csv is checked."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIRECTORY,
        help=(
            "directory where the three report files are written; it is created "
            "if needed (default: output/ next to main.py)"
        ),
    )
    return parser


def main(args: argparse.Namespace | None = None) -> None:
    """Load the CSV data, validate it, group observations, and summarize."""
    if args is None:
        args = create_argument_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        ld_profiles_rows = pe.read_csv(PROFILE_FILE)
    except (FileNotFoundError, PermissionError, csv.Error) as error:
        print(f"Could not load required participant profiles: {error}")
        return

    try:
        ld_valid_sessions_rows = pe.read_csv(args.valid_sessions)
    except (FileNotFoundError, PermissionError, csv.Error) as error:
        print(f"Could not load {args.valid_sessions.name}; continuing without it: {error}")
        ld_valid_sessions_rows = []

    try:
        ld_invalid_sessions_rows = pe.read_csv(args.invalid_sessions)
    except (FileNotFoundError, PermissionError, csv.Error) as error:
        print(
            f"Could not load {args.invalid_sessions.name}; "
            f"continuing without it: {error}"
        )
        ld_invalid_sessions_rows = []

    ld_rejected_records = []
    ld_rejected_records.extend(
        cv.validate_csv_rows(PROFILE_FILE.name, ld_profiles_rows, cv.PROFILE_FIELDS)
    )
    ld_rejected_records.extend(
        cv.validate_profile_ids(PROFILE_FILE.name, ld_profiles_rows)
    )
    ld_rejected_records.extend(
        cv.validate_csv_rows(
            args.valid_sessions.name, ld_valid_sessions_rows, cv.SESSION_FIELDS
        )
    )
    ld_rejected_records.extend(
        cv.validate_csv_rows(
            args.invalid_sessions.name,
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
            PROFILE_FILE.name,
            i_row_number,
            ld_profile_row,
            cv.PROFILE_NUMERIC_RULES,
            ld_rejected_records,
        )
        if b_shape_is_valid and b_id_is_valid and b_values_are_valid:
            ld_accepted_profile_rows.append(ld_profile_row)

    d_profile_row_numbers = {
        id(ld_profile_row): i_row_number
        for i_row_number, ld_profile_row in enumerate(ld_profiles_rows, start=2)
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
            ld_rejected_records.append(cv.create_validation_issue(
                PROFILE_FILE.name,
                d_profile_row_numbers[id(ld_profile_row)],
                "baseline_heart_rate",
                str(error),
            ))
            continue
        d_participants_by_id[ld_profile_row["participant_id"]] = d_participant

    ds_known_participant_ids = set(d_participants_by_id)

    ld_accepted_valid_session_rows = []
    for s_source_name, ld_session_rows, b_is_valid_input in (
        (args.valid_sessions.name, ld_valid_sessions_rows, True),
        (args.invalid_sessions.name, ld_invalid_sessions_rows, False),
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
                b_is_valid_input
                and b_shape_is_valid
                and b_ids_are_valid
                and b_participant_is_known
                and b_values_are_valid
            ):
                ld_accepted_valid_session_rows.append(ld_session_row)

    d_session_row_numbers = {
        id(ld_session_row): i_row_number
        for i_row_number, ld_session_row in enumerate(
            ld_valid_sessions_rows, start=2
        )
    }
    d_sessions_by_id: dict[str, Session] = {}
    for ld_session_row in ld_accepted_valid_session_rows:
        s_session_id = ld_session_row["session_id"]
        if s_session_id not in d_sessions_by_id:
            d_sessions_by_id[s_session_id] = Session(
                d_participants_by_id[ld_session_row["participant_id"]],
                session_id=s_session_id,
            )
        b_observation_added, s_add_message = d_sessions_by_id[
            s_session_id
        ].add_observation(ld_session_row)
        if not b_observation_added:
            ld_rejected_records.append(cv.create_validation_issue(
                args.valid_sessions.name,
                d_session_row_numbers[id(ld_session_row)],
                "observation",
                s_add_message,
            ))

    ld_analysis_results = []
    for d_session in d_sessions_by_id.values():
        d_classification_result = SessionClassifier.classify_session(d_session)
        d_analysis_result = generate_session_report(
            d_session, d_classification_result
        )
        ld_analysis_results.append(d_analysis_result)
        print_session_report(d_session, d_classification_result)

    print("Session comparison summary:")
    print(generate_summary_table(ld_analysis_results))
    summary_path = write_analysis_summary_csv(
        ld_analysis_results, args.output_dir
    )

    print(f"Wrote analysis summary: {summary_path}")
    report_path = write_analysis_report_txt(
        ld_analysis_results, args.output_dir
    )
    
    print(f"Wrote readable analysis report: {report_path}")
    rejected_path = write_rejected_records_txt(
        ld_rejected_records, args.output_dir
    )
    
    print(f"Wrote rejected-record details: {rejected_path}")

    i_low_quality_observations = sum(
        len(d_session.observations)
        - len(d_session.get_good_quality_observations(SIGNAL_QUALITY_THRESHOLD))
        for d_session in d_sessions_by_id.values()
    )
    i_insufficient_sessions = sum(
        len(d_session.get_good_quality_observations(SIGNAL_QUALITY_THRESHOLD))
        < MINIMUM_USABLE_OBSERVATIONS
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

    i_accepted_rows = sum(
        len(d_session.observations) for d_session in d_sessions_by_id.values()
    )
    i_rejected_rows = len({
        (d_record["source_file"], d_record["row_number"])
        for d_record in ld_rejected_records
    })
    print(
        f"Completed: {i_accepted_rows} accepted session rows, "
        f"{i_rejected_rows} rejected CSV rows, {len(d_sessions_by_id)} sessions. "
        f"{i_low_quality_observations} low-quality observations were excluded "
        f"from analysis; {i_insufficient_sessions} sessions had fewer than "
        f"{MINIMUM_USABLE_OBSERVATIONS} usable observations."
    )
    print(
        "Created reports: "
        f"{summary_path}, {report_path}, {rejected_path}"
    )


if __name__ == "__main__":
    main()

