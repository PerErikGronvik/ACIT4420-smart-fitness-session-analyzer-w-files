"""Tests for the reused Assignment I fitness-analysis domain code."""

import unittest

from src.calculations import (
    calculate_average,
    calculate_hr_elevation,
    calculate_max,
    calculate_min,
    detect_recovery,
)
from src.classifier import SessionClassifier
from src.observation import Observation
from src.participant import Participant
from src.report import generate_session_report
from src.session import Session
from src.validation import is_good_signal_quality, validate_observation


class DomainAnalysisTests(unittest.TestCase):
    def add_observations(self, session: Session, ld_rows: list[dict]) -> None:
        for ld_row in ld_rows:
            b_added, s_message = session.add_observation(ld_row)
            self.assertTrue(b_added, s_message)

    def test_participant_properties_and_range_validation(self) -> None:
        participant = Participant("Ola Normann", 60, 0.5)
        self.assertEqual(participant.name, "Ola Normann")
        self.assertEqual(participant.resting_heart_rate, 60)
        self.assertEqual(participant.resting_activity_level, 0.5)

        participant.resting_heart_rate = 70
        participant.resting_activity_level = 0.8
        self.assertEqual(participant.resting_heart_rate, 70)
        self.assertEqual(participant.resting_activity_level, 0.8)

        with self.assertRaisesRegex(ValueError, "between 30 and 120"):
            participant.resting_heart_rate = 121
        with self.assertRaisesRegex(ValueError, "between 0.0 and 1.0"):
            participant.resting_activity_level = 1.5

    def test_observation_attributes(self) -> None:
        observation = Observation(1, 70, 0.5, 36.6, 0.8, 0.9)
        self.assertEqual(observation.timestamp, 1)
        self.assertEqual(observation.heart_rate, 70)
        self.assertEqual(observation.skin_response, 0.5)
        self.assertEqual(observation.temperature, 36.6)
        self.assertEqual(observation.activity_level, 0.8)
        self.assertEqual(observation.signal_quality, 0.9)

    def test_observation_validation_and_signal_quality(self) -> None:
        ld_observation = {
            "timestamp": 1,
            "heart_rate": 70,
            "skin_response": 0.5,
            "temperature": 36.6,
            "activity_level": 0.8,
            "signal_quality": 0.9,
        }
        b_valid, s_message = validate_observation(ld_observation)
        self.assertTrue(b_valid)
        self.assertEqual(s_message, "")

        ld_invalid_observation = {**ld_observation, "heart_rate": 25}
        b_valid, s_message = validate_observation(ld_invalid_observation)
        self.assertFalse(b_valid)
        self.assertEqual(s_message, "Heart rate must be between 30 and 230.")
        self.assertTrue(is_good_signal_quality(0.9))
        self.assertFalse(is_good_signal_quality(0.2))

    def test_calculations_and_recovery_detection(self) -> None:
        lf_values = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.assertEqual(calculate_average(lf_values), 3.0)
        self.assertEqual(calculate_min(lf_values), 1.0)
        self.assertEqual(calculate_max(lf_values), 5.0)
        self.assertEqual(calculate_hr_elevation(80, 60), 20)

        ld_recovery_observations = [
            Observation(1, 80, 0.5, 36.6, 0.8, 0.9),
            Observation(2, 78, 0.5, 36.6, 0.7, 0.9),
            Observation(3, 76, 0.5, 36.6, 0.6, 0.9),
            Observation(4, 74, 0.5, 36.6, 0.5, 0.9),
            Observation(5, 72, 0.5, 36.6, 0.4, 0.9),
            Observation(6, 70, 0.5, 36.6, 0.3, 0.9),
            Observation(7, 68, 0.5, 36.6, 0.2, 0.9),
            Observation(8, 66, 0.5, 36.6, 0.1, 0.9),
        ]
        self.assertTrue(detect_recovery(ld_recovery_observations, 60))

        ld_steady_observations = [
            Observation(1, 61, 0.5, 36.6, 0.03, 0.9),
            Observation(2, 59, 0.5, 36.6, 0.02, 0.9),
            Observation(3, 60, 0.5, 36.6, 0.03, 0.9),
            Observation(4, 62, 0.5, 36.6, 0.02, 0.9),
            Observation(5, 59, 0.5, 36.6, 0.03, 0.9),
            Observation(6, 60, 0.5, 36.6, 0.02, 0.9),
            Observation(7, 61, 0.5, 36.6, 0.03, 0.9),
            Observation(8, 60, 0.5, 36.6, 0.02, 0.9),
        ]
        self.assertFalse(detect_recovery(ld_steady_observations, 60))

    def test_session_composes_participant_and_observations(self) -> None:
        participant = Participant("John Doe", 70, 0.5)
        session = Session(participant, session_id="FIT-2026-001")
        ld_observation = {
            "timestamp": 1,
            "heart_rate": 70,
            "skin_response": 0.5,
            "temperature": 36.6,
            "activity_level": 0.8,
            "signal_quality": 0.9,
        }

        b_added, s_message = session.add_observation(ld_observation)

        self.assertTrue(b_added)
        self.assertEqual(s_message, "Observation added successfully.")
        self.assertIs(session.participant, participant)
        self.assertEqual(session.session_id, "FIT-2026-001")
        self.assertIsInstance(session.get_observations()[0], Observation)
        self.assertEqual(len(session.get_good_quality_observations()), 1)

    def test_session_rejects_invalid_observation(self) -> None:
        session = Session(Participant("Jane Doe", 70, 0.5))
        ld_invalid_observation = {
            "timestamp": 1,
            "heart_rate": 999,
            "skin_response": 0.5,
            "temperature": 36.6,
            "activity_level": 0.8,
            "signal_quality": 0.9,
        }

        b_added, s_message = session.add_observation(ld_invalid_observation)

        self.assertFalse(b_added)
        self.assertEqual(s_message, "Heart rate must be between 30 and 230.")
        self.assertEqual(session.get_observations(), [])

    def test_classifier_normal_unusual_and_insufficient_cases(self) -> None:
        resting_session = Session(Participant("Resting Person", 60, 0.1))
        active_session = Session(Participant("Active Person", 60, 0.1))
        short_session = Session(Participant("New Person", 60, 0.1))
        ld_resting_rows = []
        ld_active_rows = []
        for i_timestamp in range(5):
            ld_resting_rows.append({
                "timestamp": i_timestamp,
                "heart_rate": 61,
                "skin_response": 0.5,
                "temperature": 36.6,
                "activity_level": 0.05,
                "signal_quality": 0.9,
            })
            ld_active_rows.append({
                "timestamp": i_timestamp,
                "heart_rate": 130,
                "skin_response": 3.0,
                "temperature": 37.8,
                "activity_level": 0.9,
                "signal_quality": 0.9,
            })
        self.add_observations(resting_session, ld_resting_rows)
        self.add_observations(active_session, ld_active_rows)
        self.add_observations(short_session, [{
            "timestamp": 1,
            "heart_rate": 65,
            "skin_response": 0.5,
            "temperature": 36.6,
            "activity_level": 0.1,
            "signal_quality": 0.9,
        }])

        self.assertEqual(
            SessionClassifier.classify_session(resting_session)["classification"],
            "resting",
        )
        self.assertEqual(
            SessionClassifier.classify_session(active_session)["classification"],
            "high activity",
        )
        self.assertEqual(
            SessionClassifier.classify_session(short_session)["classification"],
            "insufficient data",
        )
        s_rules = SessionClassifier.get_classification_rules()
        self.assertIn("resting", s_rules)
        self.assertIn("recovering", s_rules)

    def test_structured_report_contains_session_analysis(self) -> None:
        session = Session(
            Participant("Report Person", 60, 0.1), session_id="FIT-2026-009"
        )
        ld_observations = [{
            "timestamp": i_timestamp,
            "heart_rate": 61,
            "skin_response": 0.5,
            "temperature": 36.6,
            "activity_level": 0.05,
            "signal_quality": 0.9,
        } for i_timestamp in range(5)]
        self.add_observations(session, ld_observations)

        d_classification = SessionClassifier.classify_session(session)
        d_report = generate_session_report(session, d_classification)

        self.assertEqual(d_report["session_id"], "FIT-2026-009")
        self.assertEqual(d_report["participant"], "Report Person")
        self.assertEqual(d_report["classification"], "resting")
        self.assertEqual(d_report["total_observations"], 5)
        self.assertEqual(d_report["usable_observations"], 5)


if __name__ == "__main__":
    unittest.main()
