# %% [markdown]
# Smart Fitness Session Analyzer Report
# To run the file Install the VS Code Python and Jupyter extensions and open this file in VS Code. and the ipykernel package must be installed beforehand.
#
# Each section below demonstrates one bullet point from the assignment's
# "Common requirements" list, in the same order they are listed there.

# %% [markdown]
# ## 1. At least four meaningful classes, including one clear example of composition

# %%
from src.observation import Observation
from src.participant import Participant
from src.session import Session
from src.classifier import SessionClassifier

participant = Participant("John Doe", 70, 0.5)
session = Session(participant)  # composition: a Session has a Participant and has Observations

observation_data = {
    "timestamp": 1,
    "heart_rate": 70,
    "skin_response": 0.5,
    "temperature": 36.6,
    "activity_level": 0.8,
    "signal_quality": 0.9,
}
success, message = session.add_observation(observation_data)
assert success

print("Classes:", Participant.__name__, Observation.__name__, Session.__name__, SessionClassifier.__name__)
print("Composition check:", session.participant is participant, isinstance(session.get_observations()[0], Observation))

# %% [markdown]
# ## 2. At least one private or protected-style attribute controlled through a property

# %%
print("Protected attribute:", participant._resting_heart_rate)

try:
    participant.resting_heart_rate = 999
except ValueError as error:
    print("Invalid assignment correctly rejected:", error)

# %% [markdown]
# ## 3. Composition preferred over inheritance
#
# `Session` is not a type of `Participant` or `Observation` - it aggregates them.
# No inheritance hierarchy is used between the domain classes for this reason


# %% [markdown]
# ## 4. At least one class method or static method with a justified purpose

# %%
result = SessionClassifier.classify_session(session)  # static method, needs no instance state
print("classify_session (static method):", result["classification"])
print(SessionClassifier.get_classification_rules())  # class method, documents ACTIVITY_THRESHOLDS

# %% [markdown]
# ## 5. At least four standalone functions for calculations, validation, or presentation

# %%
from src.calculations import calculate_average, calculate_min, calculate_max, calculate_hr_elevation, detect_recovery
from src.validation import validate_observation, is_good_signal_quality
from src.report import generate_session_report, print_session_report

heart_rates = [70, 75, 80, 65, 90]
print("calculate_average:", calculate_average(heart_rates))
print("calculate_min:", calculate_min(heart_rates))
print("calculate_max:", calculate_max(heart_rates))
print("calculate_hr_elevation:", calculate_hr_elevation(90, 70))
print("validate_observation:", validate_observation(observation_data))
print("is_good_signal_quality:", is_good_signal_quality(0.9))

# %% [markdown]
# ## 6. Lists and dictionaries as part of the application data

# %%
summary = session.get_session_summary()
print("Session summary (dict):", summary)
print("Observations (list):", session.get_observations())

# %% [markdown]
# ## 7. Validation of missing, impossible, or poor-quality values

# %%
missing_field = {k: v for k, v in observation_data.items() if k != "heart_rate"}
impossible_value = {**observation_data, "heart_rate": 999}
poor_quality = {**observation_data, "signal_quality": 0.2}

print("Missing field:", validate_observation(missing_field))
print("Impossible value:", validate_observation(impossible_value))
print("Poor signal quality accepted by validation, but excluded from analysis:", is_good_signal_quality(poor_quality["signal_quality"]))

# %% [markdown]
# ## 8. A structured result returned as a dictionary

# %%
report_dict = generate_session_report(session, result)
print(report_dict)

# %% [markdown]
# ## 9. A readable console report

# %%
print_session_report(session, result)

# %% [markdown]
# ## 10. At least five scenarios, including normal, unusual, and invalid-data cases

# %%
from sample_data import (
    get_resting_session_data,
    get_moderate_activity_session_data,
    get_high_activity_session_data,
    get_activity_followed_by_recovery_session_data,
    get_poor_quality_session_data,
)


def build_session(participant_data, observations_data):
    """Create a Session and add all observations, printing any that get rejected."""
    p = Participant(
        participant_data["name"],
        participant_data["resting_heart_rate"],
        participant_data["resting_activity_level"],
    )
    s = Session(p)
    for observation in observations_data:
        ok, msg = s.add_observation(observation)
        if not ok:
            print(f"  Rejected: {msg}")
    return s


scenarios = [
    ("Resting session", get_resting_session_data),
    ("Moderate activity", get_moderate_activity_session_data),
    ("High activity", get_high_activity_session_data),
    ("Activity followed by recovery", get_activity_followed_by_recovery_session_data),
    ("Poor quality / invalid sensor data", get_poor_quality_session_data),
]

for label, data_fn in scenarios:
    print(f"\n--- {label} ---")
    p_data, o_data = data_fn()
    s = build_session(p_data, o_data)
    print_session_report(s, SessionClassifier.classify_session(s))

# %% [markdown]
# ## Test coverage
#
# Runs the actual test suite in `tests.py`.

# %%
import runpy

_ = runpy.run_path("tests.py", run_name="__main__")

