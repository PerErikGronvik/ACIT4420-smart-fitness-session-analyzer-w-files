"""
SessionClassifier for analyzing and classifying fitness sessions.
"""

from src.calculations import calculate_average, calculate_hr_elevation, detect_recovery
from src.validation import MINIMUM_USABLE_OBSERVATIONS


class SessionClassifier:
    """
    Analyzes a session and classifies its intensity level.

    Classification levels:
    - resting: minimal change from baseline
    - moderate activity: some elevation in heart rate
    - high activity: significant elevation in heart rate
    - recovering: heart rate and activity decline near the end of the session
    - insufficient data: fewer than 3 usable observations
    """

    # Class variable defining the heart-rate-increase boundaries between levels
    ACTIVITY_THRESHOLDS = {
        "resting": 0.10,   # below 10% above resting HR
        "moderate": 0.55,  # 10-55% above resting HR
    }

    @staticmethod
    def classify_session(session) -> dict:
        """
        Classify a session and return detailed results.

        Args:
            session: Session object to classify

        Returns:
            Dictionary with classification results
        """
        usable = session.get_good_quality_observations()

        if len(usable) < MINIMUM_USABLE_OBSERVATIONS:
            return {
                "classification": "insufficient data",
                "reason": (
                    f"Only {len(usable)} usable observations; at least "
                    f"{MINIMUM_USABLE_OBSERVATIONS} are required."
                ),
                "confidence": 0.0,
                "avg_heart_rate": 0,
                "hr_increase_percent": 0,
                "recovering": False,
            }

        resting_hr = session.participant.resting_heart_rate
        avg_hr = calculate_average([obs.heart_rate for obs in usable])
        elevation = calculate_hr_elevation(avg_hr, resting_hr)
        increase_percent = elevation / resting_hr if resting_hr else 0
        recovering = detect_recovery(usable, resting_hr)

        if recovering:
            classification = "recovering"
            reason = "Heart rate and activity decline toward the end of the session."
        elif increase_percent < SessionClassifier.ACTIVITY_THRESHOLDS["resting"]:
            classification = "resting"
            reason = "Average heart rate stays close to the resting baseline."
        elif increase_percent < SessionClassifier.ACTIVITY_THRESHOLDS["moderate"]:
            classification = "moderate activity"
            reason = "Average heart rate is moderately elevated above baseline."
        else:
            classification = "high activity"
            reason = "Average heart rate is significantly elevated above baseline."

        confidence = min(1.0, len(usable) / len(session.observations)) if session.observations else 0.0

        return {
            "classification": classification,
            "reason": reason,
            "confidence": confidence,
            "avg_heart_rate": avg_hr,
            "hr_increase_percent": increase_percent,
            "recovering": recovering,
        }

    @classmethod
    def get_classification_rules(cls) -> str:
        """
        Return a human-readable description of the classification rules.
        """
        return (
            "Classification rules:\n"
            f"  resting: heart rate increase below {cls.ACTIVITY_THRESHOLDS['resting'] * 100:.0f}%\n"
            f"  moderate activity: heart rate increase below {cls.ACTIVITY_THRESHOLDS['moderate'] * 100:.0f}%\n"
            "  high activity: heart rate increase above the moderate threshold\n"
            "  recovering: heart rate and activity decline near the end of the session\n"
            "  insufficient data: fewer than 3 usable observations"
        )
