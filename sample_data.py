"""
Sample data for testing the fitness session analyzer.

Data to demonstrate the five required scenarios:
1. Resting state
2. Moderate activity
3. High activity
4. Activity followed by recovery
5. Poor quality or invalid sensor data

Generated using data_generator with sufficient observations for reliable testing.
"""

from option_a_fitness.data_generator import generate_fitness_data

def get_resting_session_data():
    profile, observations = generate_fitness_data("P001", "resting", seed=42, number_of_windows=8)
    participant = {
        "name": "Ola Normann",
        "resting_heart_rate": profile["baseline_heart_rate"],
        "resting_activity_level": 0.05
    }

    # Additional fixed observations for reliable test assertions
    base_hr = profile["baseline_heart_rate"]
    observations.extend([
        {"timestamp": 8, "heart_rate": base_hr + 1, "skin_response": 0.35, "temperature": 36.5, "activity_level": 0.03, "signal_quality": 0.94},
        {"timestamp": 9, "heart_rate": base_hr - 2, "skin_response": 0.32, "temperature": 36.4, "activity_level": 0.02, "signal_quality": 0.95},
        {"timestamp": 10, "heart_rate": base_hr, "skin_response": 0.33, "temperature": 36.5, "activity_level": 0.03, "signal_quality": 0.93},
        {"timestamp": 11, "heart_rate": base_hr + 2, "skin_response": 0.34, "temperature": 36.4, "activity_level": 0.02, "signal_quality": 0.94},
        {"timestamp": 12, "heart_rate": base_hr - 1, "skin_response": 0.31, "temperature": 36.5, "activity_level": 0.03, "signal_quality": 0.96},
        {"timestamp": 13, "heart_rate": base_hr + 1, "skin_response": 0.33, "temperature": 36.4, "activity_level": 0.02, "signal_quality": 0.95},
        {"timestamp": 14, "heart_rate": base_hr, "skin_response": 0.32, "temperature": 36.5, "activity_level": 0.03, "signal_quality": 0.94},
        {"timestamp": 15, "heart_rate": base_hr + 2, "skin_response": 0.34, "temperature": 36.4, "activity_level": 0.02, "signal_quality": 0.93},
        {"timestamp": 16, "heart_rate": base_hr - 2, "skin_response": 0.30, "temperature": 36.5, "activity_level": 0.03, "signal_quality": 0.95},
        {"timestamp": 17, "heart_rate": base_hr + 1, "skin_response": 0.33, "temperature": 36.4, "activity_level": 0.02, "signal_quality": 0.94},
    ])

    return participant, observations

def get_moderate_activity_session_data():
    profile, observations = generate_fitness_data("P002", "moderate_activity", seed=43, number_of_windows=8)
    participant = {
        "name": "Kari Normann",
        "resting_heart_rate": profile["baseline_heart_rate"],
        "resting_activity_level": 0.1
    }

    # Additional fixed observations for reliable test assertions
    base_hr = profile["baseline_heart_rate"]
    observations.extend([
        {"timestamp": 8, "heart_rate": base_hr + 18, "skin_response": 1.35, "temperature": 36.9, "activity_level": 0.36, "signal_quality": 0.92},
        {"timestamp": 9, "heart_rate": base_hr + 20, "skin_response": 1.45, "temperature": 37.0, "activity_level": 0.38, "signal_quality": 0.93},
        {"timestamp": 10, "heart_rate": base_hr + 16, "skin_response": 1.25, "temperature": 36.85, "activity_level": 0.33, "signal_quality": 0.91},
        {"timestamp": 11, "heart_rate": base_hr + 15, "skin_response": 1.2, "temperature": 36.8, "activity_level": 0.31, "signal_quality": 0.92},
        {"timestamp": 12, "heart_rate": base_hr + 19, "skin_response": 1.4, "temperature": 36.95, "activity_level": 0.37, "signal_quality": 0.93},
        {"timestamp": 13, "heart_rate": base_hr + 17, "skin_response": 1.3, "temperature": 36.9, "activity_level": 0.34, "signal_quality": 0.92},
        {"timestamp": 14, "heart_rate": base_hr + 21, "skin_response": 1.5, "temperature": 37.05, "activity_level": 0.4, "signal_quality": 0.94},
        {"timestamp": 15, "heart_rate": base_hr + 16, "skin_response": 1.25, "temperature": 36.85, "activity_level": 0.33, "signal_quality": 0.91},
        {"timestamp": 16, "heart_rate": base_hr + 18, "skin_response": 1.35, "temperature": 36.9, "activity_level": 0.36, "signal_quality": 0.92},
        {"timestamp": 17, "heart_rate": base_hr + 15, "skin_response": 1.2, "temperature": 36.8, "activity_level": 0.31, "signal_quality": 0.93},
    ])

    return participant, observations

def get_high_activity_session_data():
    profile, observations = generate_fitness_data("P003", "high_activity", seed=44, number_of_windows=7)
    
    participant = {
        "name": "Per Normann",
        "resting_heart_rate": profile["baseline_heart_rate"],
        "resting_activity_level": 0.08
    }
    
    # Additional fixed observations for reliable test assertions
    base_hr = profile["baseline_heart_rate"]
    observations.extend([
        {"timestamp": 7, "heart_rate": base_hr + 85, "skin_response": 3.5, "temperature": 37.8, "activity_level": 0.89, "signal_quality": 0.95},
        {"timestamp": 8, "heart_rate": base_hr + 88, "skin_response": 3.7, "temperature": 37.9, "activity_level": 0.91, "signal_quality": 0.96},
        {"timestamp": 9, "heart_rate": base_hr + 82, "skin_response": 3.4, "temperature": 37.6, "activity_level": 0.87, "signal_quality": 0.94},
        {"timestamp": 10, "heart_rate": base_hr + 80, "skin_response": 3.2, "temperature": 37.5, "activity_level": 0.84, "signal_quality": 0.93},
        {"timestamp": 11, "heart_rate": base_hr + 90, "skin_response": 3.9, "temperature": 38.0, "activity_level": 0.93, "signal_quality": 0.95},
        {"timestamp": 12, "heart_rate": base_hr + 86, "skin_response": 3.6, "temperature": 37.8, "activity_level": 0.90, "signal_quality": 0.94},
        {"timestamp": 13, "heart_rate": base_hr + 83, "skin_response": 3.5, "temperature": 37.7, "activity_level": 0.88, "signal_quality": 0.96},
        {"timestamp": 14, "heart_rate": base_hr + 87, "skin_response": 3.6, "temperature": 37.85, "activity_level": 0.90, "signal_quality": 0.93},
        {"timestamp": 15, "heart_rate": base_hr + 81, "skin_response": 3.3, "temperature": 37.6, "activity_level": 0.86, "signal_quality": 0.95},
        {"timestamp": 16, "heart_rate": base_hr + 84, "skin_response": 3.4, "temperature": 37.7, "activity_level": 0.88, "signal_quality": 0.94},
    ])

    return participant, observations

def get_poor_quality_session_data():
    profile, observations = generate_fitness_data("P004", "poor_quality", seed=45, number_of_windows=7)
    
    participant = {
        "name": "Nils Normann",
        "resting_heart_rate": profile["baseline_heart_rate"],
        "resting_activity_level": 0.1
    }
    
    # Known-invalid entries the validator must reject, plus known-good entries
    # so the session still has enough usable data to classify.
    observations.extend([
        {"timestamp": 7, "heart_rate": 75, "skin_response": 2.0, "temperature": 36.7, "activity_level": 0.5, "signal_quality": 0.65},   # below quality threshold
        {"timestamp": 8, "heart_rate": 250, "skin_response": 1.8, "temperature": 36.8, "activity_level": 0.4, "signal_quality": 0.55},  # invalid heart rate (too high)
        {"timestamp": 9, "heart_rate": 95, "skin_response": 1.5, "temperature": 50.0, "activity_level": 0.6, "signal_quality": 0.48},   # invalid temperature (too high)
        {"timestamp": 10, "heart_rate": 92, "skin_response": 1.6, "temperature": 36.9, "activity_level": 1.5, "signal_quality": 0.40}, # invalid activity level
        {"timestamp": 11, "heart_rate": -50, "skin_response": 2.2, "temperature": 36.8, "activity_level": 0.5, "signal_quality": 0.60}, # invalid heart rate (negative)
        {"timestamp": 12, "heart_rate": 89, "skin_response": 2.1, "temperature": 15.0, "activity_level": 0.46, "signal_quality": 0.61}, # invalid temperature (too low)
        {"timestamp": 13, "heart_rate": 91, "skin_response": 2.0, "temperature": 36.8, "activity_level": 0.5, "signal_quality": 0.72},  # good quality
        {"timestamp": 14, "heart_rate": 87, "skin_response": 2.1, "temperature": 36.7, "activity_level": 0.49, "signal_quality": 0.75}, # good quality
        {"timestamp": 15, "heart_rate": 92, "skin_response": 2.0, "temperature": 36.8, "activity_level": 0.51, "signal_quality": 0.73}, # good quality
        {"timestamp": 16, "heart_rate": 90, "skin_response": 2.0, "temperature": 36.7, "activity_level": 0.5, "signal_quality": 0.76},  # good quality
    ])

    return participant, observations

def get_activity_followed_by_recovery_session_data():
    profile, observations = generate_fitness_data("P005", "recovery", seed=46, number_of_windows=7)
    
    participant = {
        "name": "Eva Normann",
        "resting_heart_rate": profile["baseline_heart_rate"],
        "resting_activity_level": 0.06
    }
    
    # Fixed observations showing a monotonic decline back toward baseline
    base_hr = profile["baseline_heart_rate"]
    observations.extend([
        {"timestamp": 7, "heart_rate": base_hr + 55, "skin_response": 3.0, "temperature": 37.6, "activity_level": 0.80, "signal_quality": 0.95},
        {"timestamp": 8, "heart_rate": base_hr + 45, "skin_response": 2.6, "temperature": 37.4, "activity_level": 0.70, "signal_quality": 0.94},
        {"timestamp": 9, "heart_rate": base_hr + 35, "skin_response": 2.2, "temperature": 37.3, "activity_level": 0.60, "signal_quality": 0.94},
        {"timestamp": 10, "heart_rate": base_hr + 27, "skin_response": 2.0, "temperature": 37.2, "activity_level": 0.54, "signal_quality": 0.93},
        {"timestamp": 11, "heart_rate": base_hr + 20, "skin_response": 1.8, "temperature": 37.1, "activity_level": 0.48, "signal_quality": 0.92},
        {"timestamp": 12, "heart_rate": base_hr + 14, "skin_response": 1.5, "temperature": 37.0, "activity_level": 0.36, "signal_quality": 0.92},
        {"timestamp": 13, "heart_rate": base_hr + 10, "skin_response": 1.2, "temperature": 36.9, "activity_level": 0.25, "signal_quality": 0.91},
        {"timestamp": 14, "heart_rate": base_hr + 6, "skin_response": 1.0, "temperature": 36.85, "activity_level": 0.16, "signal_quality": 0.92},
        {"timestamp": 15, "heart_rate": base_hr + 3, "skin_response": 0.8, "temperature": 36.8, "activity_level": 0.08, "signal_quality": 0.93},
        {"timestamp": 16, "heart_rate": base_hr + 1, "skin_response": 0.6, "temperature": 36.7, "activity_level": 0.05, "signal_quality": 0.94},
    ])

    return participant, observations