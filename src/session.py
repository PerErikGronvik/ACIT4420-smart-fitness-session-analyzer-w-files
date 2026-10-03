"""
Grouping observations into fitness session.
"""

from src.observation import Observation
from src.validation import validate_observation, is_good_signal_quality
from src.calculations import calculate_average, calculate_min, calculate_max, calculate_hr_elevation

class Session:
    """
    Represents a fitness session consisting of multiple observations.
    
    Demonstrates composition: A session contains multiple observation objects.

    Attributes:
        observations (list of Observation): The list of observations in the session.
        participant (Participant): The participant associated with the session.

    """
    def __init__(self, participant):

        self.observations = []
        self.participant = participant

    def add_observation(self, observation_dict: dict) -> tuple[bool, str]:
        """
        Adds an observation to the session after validation.

        Args:
            observation_dict (dict): The observation data to be added.

        Returns:
            tuple[bool, str]: A tuple containing a boolean indicating success,
                               and a message describing the result.
        """
        is_valid, message = validate_observation(observation_dict)
        if not is_valid:
            return False, message
        obs = Observation(
            timestamp=observation_dict["timestamp"],
            heart_rate=observation_dict["heart_rate"],
            skin_response=observation_dict["skin_response"],
            temperature=observation_dict["temperature"],
            activity_level=observation_dict["activity_level"],
            signal_quality=observation_dict["signal_quality"]
        )
        self.observations.append(obs)
        return True, "Observation added successfully."

    def get_observations(self) -> list[Observation]:
        """
        Get all observations in the session.
        """
        return self.observations

    def get_good_quality_observations(self, quality_threshold: float=0.7) -> list:
        """
        Get all observations with good signal quality above the specified threshold.

        Args:
            quality_threshold (float): The minimum signal quality required for an observation to be considered good.

        Returns:
            list[Observation]: The list of good quality observations.
        """
        return [obs for obs in self.observations if is_good_signal_quality(obs.signal_quality, quality_threshold)]

    def get_session_summary(self, quality_threshold: float = 0.7) -> dict:
        """
        Get a summary of the session, including the number of good quality observations.

        Args:
            quality_threshold (float): The minimum signal quality required for an observation to be considered good.

        Returns:
            dict: A dictionary containing the session summary.
        """
        good_quality_observations = self.get_good_quality_observations(quality_threshold)

        if not good_quality_observations:
            return {
                "total_observations": len(self.observations),
                "good_quality_observations": 0,
                "average_heart_rate": 0,
                "min_heart_rate": 0,
                "max_heart_rate": 0,
                "average_skin_response": 0,
                "average_activity_level": 0,
                "average_temperature": 0
            }
        heart_rates = [obs.heart_rate for obs in good_quality_observations]
        activity_levels = [obs.activity_level for obs in good_quality_observations]
        temperatures = [obs.temperature for obs in good_quality_observations]

        return {
            "total_observations": len(self.observations),
            "good_quality_observations": len(good_quality_observations),
            "average_heart_rate": sum(heart_rates) / len(heart_rates),
            "min_heart_rate": min(heart_rates),
            "max_heart_rate": max(heart_rates),
            "average_skin_response": sum(obs.skin_response for obs in good_quality_observations) / len(good_quality_observations),
            "average_activity_level": sum(activity_levels) / len(activity_levels),
            "average_temperature": sum(temperatures) / len(temperatures)
        }

    def __str__(self) -> str:
        return f"Session with {len(self.observations)} observations" 