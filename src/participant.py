"""
Participant class, represents a participant and the reference measurements.
"""

class Participant:
    """
    Takes in: name(str), resting_heart_rate(int), resting_activity_level(float)
    """

    def __init__(self, name: str, resting_heart_rate: int, resting_activity_level: float):
        """
        Args:
        Takes in: name(str), resting_heart_rate(int), resting_activity_level(float)
        """
        self.name = name
        self.resting_heart_rate = resting_heart_rate
        self.resting_activity_level = resting_activity_level

    @property
    def resting_heart_rate(self) -> int:
        """Get the resting heart rate."""
        return self._resting_heart_rate

    @resting_heart_rate.setter
    def resting_heart_rate(self, value: int) -> None:
        """Set the resting heart rate."""
        if value < 30 or value > 120:
            raise ValueError("Resting heart rate must be between 30 and 120.")
        print(f"Setting resting heart rate to {value}")
        self._resting_heart_rate = value
    
    @property
    def resting_activity_level(self) -> float:
        """Get the resting activity level."""
        return self._resting_activity_level

    @resting_activity_level.setter
    def resting_activity_level(self, value: float) -> None:
        """Set the resting activity level"""
        if not(0 <= value <= 1):
            raise ValueError("Resting activity level must be between 0.0 and 1.0.")
        print(f"Setting resting activity level to {value}")
        self._resting_activity_level = value

    def __str__(self) -> str:
        """Return a string representation of the participant."""
        return f"Participant(name={self.name}, resting_heart_rate={self.resting_heart_rate}, resting_activity_level={self.resting_activity_level})"