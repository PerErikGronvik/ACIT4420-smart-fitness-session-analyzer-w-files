"""Focused tests for Assignment II CSV validation behavior."""

import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import csv_validation as cv
from src import perdas as pe
from src.participant import Participant
from src.report import write_analysis_report_txt, write_analysis_summary_csv, write_rejected_records_txt


class CsvValidationTests(unittest.TestCase):
    def make_session_row(self, **overrides: str | None) -> dict[str, str | None]:
        d_session_row: dict[str, str | None] = {
            "session_id": "FIT-2026-001",
            "participant_id": "P001",
            "timestamp": "0",
            "heart_rate": "68",
            "skin_response": "1.18",
            "temperature": "32.4",
            "activity_level": "0.08",
            "signal_quality": "0.98",
        }
        d_session_row.update(overrides)
        return d_session_row

    def test_valid_session_row_passes_schema_id_and_numeric_validation(self) -> None:
        d_session_row = self.make_session_row()
        ld_issues = []

        self.assertEqual(
            cv.validate_csv_rows("fitness_sessions.csv", [d_session_row], cv.SESSION_FIELDS),
            [],
        )
        with patch.object(cv, "VERBOSE", False):
            self.assertEqual(
                cv.validate_session_ids("fitness_sessions.csv", [d_session_row]),
                [],
            )
        self.assertTrue(
            cv.convert_and_validate_numeric_fields(
                "fitness_sessions.csv",
                2,
                d_session_row,
                cv.SESSION_NUMERIC_RULES,
                ld_issues,
            )
        )
        self.assertEqual(d_session_row["timestamp"], 0)
        self.assertEqual(d_session_row["heart_rate"], 68)
        self.assertEqual(ld_issues, [])

    def test_malformed_session_and_participant_ids_are_reported(self) -> None:
        d_session_row = self.make_session_row(
            session_id="FIT-26-001", participant_id="001"
        )

        with patch.object(cv, "VERBOSE", False):
            ld_issues = cv.validate_session_ids(
                "fitness_sessions_invalid.csv", [d_session_row]
            )

        self.assertEqual(
            [(d_issue["field"], d_issue["row_number"]) for d_issue in ld_issues],
            [("session_id", 2), ("participant_id", 2)],
        )
        self.assertTrue(all(
            d_issue["source_file"] == "fitness_sessions_invalid.csv"
            for d_issue in ld_issues
        ))

    def test_blank_required_field_is_reported(self) -> None:
        d_session_row = self.make_session_row(activity_level="")

        ld_issues = cv.validate_csv_rows(
            "fitness_sessions_invalid.csv", [d_session_row], cv.SESSION_FIELDS
        )

        self.assertTrue(any(
            d_issue["field"] == "activity_level" for d_issue in ld_issues
        ))

    def test_missing_header_column_is_reported(self) -> None:
        d_session_row = self.make_session_row()
        del d_session_row["signal_quality"]

        ld_issues = cv.validate_csv_rows(
            "fitness_sessions.csv", [d_session_row], cv.SESSION_FIELDS
        )

        self.assertTrue(any(
            d_issue["field"] == "signal_quality"
            and "missing from the CSV header" in d_issue["reason"]
            for d_issue in ld_issues
        ))

    def test_short_row_reports_missing_field_and_column_count(self) -> None:
        d_session_row = self.make_session_row(signal_quality=None)

        ld_issues = cv.validate_csv_rows(
            "fitness_sessions_invalid.csv", [d_session_row], cv.SESSION_FIELDS
        )

        self.assertTrue(any(
            d_issue["field"] == "signal_quality" for d_issue in ld_issues
        ))
        self.assertTrue(any(
            d_issue["field"] == "row" and "found 7" in d_issue["reason"]
            for d_issue in ld_issues
        ))

    def test_bad_numeric_conversion_is_reported(self) -> None:
        d_session_row = self.make_session_row(heart_rate="fast")
        ld_issues = []

        b_is_valid = cv.convert_and_validate_numeric_fields(
            "fitness_sessions_invalid.csv",
            3,
            d_session_row,
            cv.SESSION_NUMERIC_RULES,
            ld_issues,
        )

        self.assertFalse(b_is_valid)
        self.assertEqual(ld_issues[0]["field"], "heart_rate")
        self.assertIn("Cannot convert 'fast'", ld_issues[0]["reason"])

    def test_out_of_range_numeric_value_is_reported(self) -> None:
        d_session_row = self.make_session_row(signal_quality="1.4")
        ld_issues = []

        b_is_valid = cv.convert_and_validate_numeric_fields(
            "fitness_sessions_invalid.csv",
            6,
            d_session_row,
            cv.SESSION_NUMERIC_RULES,
            ld_issues,
        )

        self.assertFalse(b_is_valid)
        self.assertEqual(ld_issues[0]["field"], "signal_quality")
        self.assertIn("outside the allowed range", ld_issues[0]["reason"])

    def test_numeric_range_boundaries_are_accepted(self) -> None:
        ld_boundary_rows = [
            self.make_session_row(
                timestamp="0",
                heart_rate="30",
                skin_response="0",
                temperature="25",
                activity_level="0",
                signal_quality="0",
            ),
            self.make_session_row(
                timestamp="1",
                heart_rate="230",
                skin_response="100",
                temperature="42",
                activity_level="1",
                signal_quality="1",
            ),
        ]

        for i_row_number, d_session_row in enumerate(ld_boundary_rows, start=2):
            with self.subTest(row=i_row_number):
                self.assertTrue(
                    cv.convert_and_validate_numeric_fields(
                        "fitness_sessions.csv",
                        i_row_number,
                        d_session_row,
                        cv.SESSION_NUMERIC_RULES,
                        [],
                    )
                )

    def test_profile_baseline_limit_matches_participant_model(self) -> None:
        d_profile_row = {
            "baseline_heart_rate": "120",
            "baseline_skin_response": "1.2",
            "baseline_temperature": "32.4",
        }
        self.assertTrue(
            cv.convert_and_validate_numeric_fields(
                "participants.csv",
                2,
                d_profile_row,
                cv.PROFILE_NUMERIC_RULES,
                [],
            )
        )
        self.assertEqual(Participant("Test", 120).resting_heart_rate, 120)

        d_profile_row = {
            "baseline_heart_rate": "121",
            "baseline_skin_response": "1.2",
            "baseline_temperature": "32.4",
        }
        ld_issues = []
        self.assertFalse(
            cv.convert_and_validate_numeric_fields(
                "participants.csv",
                2,
                d_profile_row,
                cv.PROFILE_NUMERIC_RULES,
                ld_issues,
            )
        )
        with self.assertRaises(ValueError):
            Participant("Test", 121)

    def test_missing_input_file_raises_contextual_error(self) -> None:
        with tempfile.TemporaryDirectory() as s_temp_directory:
            missing_path = Path(s_temp_directory) / "missing.csv"

            with self.assertRaisesRegex(
                FileNotFoundError, "CSV input file was not found"
            ):
                pe.read_csv(missing_path)

    def test_unknown_participant_is_reported(self) -> None:
        d_session_row = self.make_session_row(participant_id="P999")

        ld_issues = cv.validate_session_participants(
            "fitness_sessions_invalid.csv", [d_session_row], {"P001", "P002"}
        )

        self.assertEqual(len(ld_issues), 1)
        self.assertEqual(ld_issues[0]["field"], "participant_id")
        self.assertIn("P999", ld_issues[0]["reason"])

    def test_report_files_are_created_and_overwritten_on_repeat_run(self) -> None:
        d_first_result = {
            "session_id": "FIT-2026-001",
            "participant_id": "P001",
            "participant": "Amina Noor",
            "resting_heart_rate": 68,
            "baseline_skin_response": 1.2,
            "baseline_temperature": 32.4,
            "classification": "resting",
            "confidence": 1.0,
            "reason": "Average heart rate stays close to baseline.",
            "total_observations": 4,
            "usable_observations": 4,
            "usable_percent": 100.0,
            "avg_heart_rate": 68.5,
            "min_heart_rate": 68,
            "max_heart_rate": 69,
            "avg_activity_level": 0.1,
            "avg_skin_response": 1.2,
            "avg_temperature": 32.4,
            "heart_rate_change": 0.5,
            "skin_response_change": 0.0,
            "temperature_change": 0.0,
        }
        d_second_result = {**d_first_result, "session_id": "FIT-2026-002"}
        d_first_rejection = {
            "source_file": "first.csv",
            "row_number": 2,
            "field": "heart_rate",
            "reason": "First rejection.",
        }
        d_second_rejection = {
            "source_file": "second.csv",
            "row_number": 3,
            "field": "timestamp",
            "reason": "Second rejection.",
        }

        with tempfile.TemporaryDirectory() as s_temp_directory:
            output_directory = Path(s_temp_directory) / "new-output"
            self.assertFalse(output_directory.exists())

            write_analysis_summary_csv([d_first_result], output_directory)
            write_analysis_report_txt([d_first_result], output_directory)
            write_rejected_records_txt([d_first_rejection], output_directory)
            self.assertTrue(output_directory.is_dir())

            write_analysis_summary_csv([d_second_result], output_directory)
            write_analysis_report_txt([d_second_result], output_directory)
            write_rejected_records_txt([d_second_rejection], output_directory)

            with (output_directory / "analysis_summary.csv").open(
                "r", encoding="utf-8", newline=""
            ) as csv_file:
                ld_summary_rows = list(csv.DictReader(csv_file))
            self.assertEqual(len(ld_summary_rows), 1)
            self.assertEqual(ld_summary_rows[0]["session_id"], "FIT-2026-002")

            s_analysis_report = (
                output_directory / "analysis_report.txt"
            ).read_text(encoding="utf-8")
            self.assertIn("FIT-2026-002", s_analysis_report)
            self.assertNotIn("FIT-2026-001", s_analysis_report)

            s_rejected_report = (
                output_directory / "rejected_records.txt"
            ).read_text(encoding="utf-8")
            self.assertIn("second.csv row 3, field timestamp: Second rejection.", s_rejected_report)
            self.assertNotIn("First rejection.", s_rejected_report)


if __name__ == "__main__":
    unittest.main()