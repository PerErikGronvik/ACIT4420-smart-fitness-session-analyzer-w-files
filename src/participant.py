"""
Participant class, represents a participant and the reference measurements.
"""

from src.validation import PROFILE_BASELINE_HEART_RATE_RANGE


class Participant:
    """
    Takes in: name(str), resting_heart_rate(int), resting_activity_level(float)
    """

    def __init__(
        self,
        name: str,
        resting_heart_rate: int,
        resting_activity_level: float | None = None,
        *,
        participant_id: str | None = None,
        baseline_skin_response: float | None = None,
        baseline_temperature: float | None = None,
    ):
        """
        Args:
        Takes in: name(str), resting_heart_rate(int), resting_activity_level(float)
        """
        self.name = name
        self._participant_id = participant_id
        self._baseline_skin_response = baseline_skin_response
        self._baseline_temperature = baseline_temperature
        self.resting_heart_rate = resting_heart_rate
        self.resting_activity_level = resting_activity_level

    @property
    def participant_id(self) -> str | None:
        """Get the participant ID when it was supplied by the profile CSV."""
        return self._participant_id

    @property
    def baseline_skin_response(self) -> float | None:
        """Get the participant's skin-response baseline when available."""
        return self._baseline_skin_response

    @property
    def baseline_temperature(self) -> float | None:
        """Get the participant's temperature baseline when available."""
        return self._baseline_temperature

    @property
    def resting_heart_rate(self) -> int:
        """Get the resting heart rate."""
        return self._resting_heart_rate

    @resting_heart_rate.setter
    def resting_heart_rate(self, value: int) -> None:
        """Set the resting heart rate."""
        minimum, maximum = PROFILE_BASELINE_HEART_RATE_RANGE
        if value < minimum or value > maximum:
            raise ValueError(
                f"Resting heart rate must be between {minimum} and {maximum}."
            )
        self._resting_heart_rate = value
    
    @property
    def resting_activity_level(self) -> float | None:
        """Get the resting activity level."""
        return self._resting_activity_level

    @resting_activity_level.setter
    def resting_activity_level(self, value: float | None) -> None:
        """Set the resting activity level"""
        if value is None:
            self._resting_activity_level = None
            return
        if not(0 <= value <= 1):
            raise ValueError("Resting activity level must be between 0.0 and 1.0.")
        self._resting_activity_level = value

    def __str__(self) -> str:
        """Return a string representation of the participant."""
        return f"Participant(name={self.name}, resting_heart_rate={self.resting_heart_rate}, resting_activity_level={self.resting_activity_level})"