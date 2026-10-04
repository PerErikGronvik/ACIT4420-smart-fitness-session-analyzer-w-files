"""Command-line entry point for the Assignment II fitness analyzer."""

import argparse
from pathlib import Path

from src.application import run_application


DATA_DIRECTORY = Path(__file__).resolve().parent / "data"
PROFILE_FILE = DATA_DIRECTORY / "participants.csv"
OUTPUT_DIRECTORY = Path(__file__).resolve().parent / "output"


def create_argument_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for CSV input and report output paths."""
    parser = argparse.ArgumentParser(
        description=(
            "Validate fitness-session CSV rows, analyze sessions that pass "
            "validation, and write summary, explanation, and rejected-row reports. "
            "Run this command from the repository root, or provide paths to the "
            "input and output files."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples (run from the repository root):\n"
            "  python3 main.py\n"
            "  python3 main.py --sessions data/my_sessions.csv --output results\n\n"
            "Reports written to the output directory:\n"
            "  analysis_summary.csv: one row per analyzed session\n"
            "  analysis_report.txt: explanations and baseline comparisons\n"
            "  rejected_records.txt: rejected rows with source, row, field, and reason\n\n"
            "Rows from --invalid-sessions are checked and reported, but not analyzed."
        ),
    )
    parser.add_argument(
        "--profiles",
        type=Path,
        default=PROFILE_FILE,
        help="participant profile CSV (default: data/participants.csv)",
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
        "--output",
        dest="output_dir",
        type=Path,
        default=OUTPUT_DIRECTORY,
        help=(
            "directory where the three report files are written; it is created "
            "if needed (default: output/ next to main.py)"
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="print validation exception details as they are caught",
    )
    return parser


def main(args: argparse.Namespace | None = None) -> None:
    """Parse command-line options and delegate the workflow."""
    if args is None:
        args = create_argument_parser().parse_args()
    run_application(
        args.profiles,
        args.valid_sessions,
        args.invalid_sessions,
        args.output_dir,
        args.verbose,
    )


if __name__ == "__main__":
    main()

