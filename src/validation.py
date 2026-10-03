"""
Validation functions
"""

def validate_observation(observation_dict: dict) -> tuple[bool, str]:
    """
    Validate an observation dictionary.

    Args:
        Observation data (dict)
    Returns:
       Tuple of is_valid (bool) and error_message (str).
    """
    if not isinstance(observation_dict, dict):
        return False, "Observation must be a dictionary."

    required_keys = [
        "timestamp",
        "heart_rate",
        "skin_response",
        "temperature",
        "activity_level",
        "signal_quality",
    ]
    for key in required_keys:
        if key not in observation_dict:
            return False, f"Missing required key: {key}"

    timestamp = observation_dict["timestamp"]
    if isinstance(timestamp, bool) or not isinstance(timestamp, int) or timestamp < 0:
        return False, "Timestamp must be a non-negative integer."

    numeric_fields = (
        ("heart_rate", 30, 230, "Heart rate must be between 30 and 230."),
        ("skin_response", 0.0, None, "Skin response must be 0.0 or greater."),
        ("temperature", 25, 42, "Temperature must be between 25 and 42."),
        ("activity_level", 0.0, 1.0, "Activity level must be between 0.0 and 1.0."),
        ("signal_quality", 0.0, 1.0, "Signal quality must be between 0.0 and 1.0."),
    )
    for field, lower, upper, error_message in numeric_fields:
        value = observation_dict[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False, f"{field} must be numeric."
        if value < lower or (upper is not None and value > upper):
            return False, error_message

    return True, ""

def is_good_signal_quality(signal_quality: float, threshold: float = 0.5) -> bool:
    """
    Check if the signal quality in the observation is good.

    Args:
        Signal quality value (float)
    Returns:
        True if signal quality is good (>= threshold), False otherwise.
    """
    if isinstance(signal_quality, bool) or not isinstance(signal_quality, (int, float)):
        return False
    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not 0.0 <= threshold <= 1.0
    ):
        raise ValueError("Threshold must be between 0.0 and 1.0.")
    return 0.0 <= signal_quality <= 1.0 and signal_quality >= threshold