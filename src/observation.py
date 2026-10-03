"""
A single measurement
"""

class Observation:
    """
    Represents a single observation.
    timestamp, heart_rate, skin_response(level), temperature(C), activity_level(0-1), signal quality(0-1)
    """
    def __init__(self, timestamp: int, heart_rate: float, skin_response: float, temperature: float, activity_level: float, signal_quality: float):
        self.timestamp = timestamp
        self.heart_rate = heart_rate
        self.skin_response = skin_response
        self.temperature = temperature
        self.activity_level = activity_level
        self.signal_quality = signal_quality
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "heart_rate": self.heart_rate,
            "skin_response": self.skin_response,
            "temperature": self.temperature,
            "activity_level": self.activity_level,
            "signal_quality": self.signal_quality
        }
    def __str__(self) -> str:
        return f"Observation(timestamp={self.timestamp}, heart_rate={self.heart_rate}, skin_response={self.skin_response}, temperature={self.temperature}, activity_level={self.activity_level}, signal_quality={self.signal_quality})"