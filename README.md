# Smart Fitness Session Analyzer

**Course:** ACIT 4420 - Python Programming Assignment (Option A)
**Student:** Per-Erik Glærum Gronvik
**Student Number:** pegro6469 385710

## Prerquisites
Python.
For report.py:
Install python and jupyter extension in vs code.

## Description

A application that analyzes simulated wearable-device measurements from a
fitness session. It validates incoming observations, compares them against a
participant's personal resting baseline, and classifies the session as resting,
moderate activity, high activity, recovering, or insufficient data.

Run `main.py`, enter a participant name and a scenario, and the program generates
simulated sensor data for that scenario (using the instructor-supplied
`option_a_fitness/data_generator.py`), validates it, and produces a console report.
The classification is always computed by the program from the data — the chosen
scenario only configures what the simulated device measures, it is not the answer.

## Repository structure

```text
README.md
main.py               entry point, prompts for a name/scenario and prints a report
tests.py               unit tests
sample_data.py         curated datasets for the 5 required scenarios (used by tests.py)
requirements.txt       dependency notes (standard library only)
report.py              interactive walkthrough (# %% cells) that demonstrates each
                        assignment requirement in order and runs tests.py; not
                        required, kept for review
option_a_fitness/      instructor-supplied data generator, unmodified
src/
    participant.py     Participant class
    observation.py     Observation class
    session.py          Session class
    classifier.py       SessionClassifier class
    validation.py       validation functions
    calculations.py      calculation functions
    report.py           report-generation functions
```

## Class design and responsibilities

- **Participant** (`src/participant.py`) — stores a participant's name and resting
  baseline (heart rate, activity level). `_resting_heart_rate` and
  `_resting_activity_level` are protected attributes, only settable through
  properties that validate their range (heart rate 30-120 bpm, activity 0.0-1.0).
- **Observation** (`src/observation.py`) — a single sensor reading (heart rate,
  skin response, temperature, activity level, signal quality) with `to_dict()`
  and `__str__()`.
- **Session** (`src/session.py`) — groups a `Participant` and a list of
  `Observation` objects. This is the composition relationship: a session *has a*
  participant and *has many* observations, rather than being a subtype of either.
  Observations are only added through `add_observation()`, which validates them
  first and rejects invalid data.
- **SessionClassifier** (`src/classifier.py`) — a stateless analyzer with:
  - a class variable `ACTIVITY_THRESHOLDS` defining the classification boundaries
  - a `@staticmethod classify_session(session)` that computes the classification
    from a session's data (no instance needed)
  - a `@classmethod get_classification_rules()` that documents the thresholds

No inheritance hierarchy is used between these classes. Composition was chosen
over inheritance because a `Session` is not a specialization of `Participant` or
`Observation` — it aggregates them. Inheritance would force an artificial
is-a relationship where none exists.

Standalone functions (not tied to any class) live in `src/validation.py`
(`validate_observation`, `is_good_signal_quality`), `src/calculations.py`
(`calculate_average`, `calculate_min`, `calculate_max`, `calculate_hr_elevation`,
`detect_recovery`), and `src/report.py` (`generate_session_report`,
`print_session_report`, `generate_summary_table`).

## Assumptions and classification rules

- An observation is rejected if any required field is missing, non-numeric, or
  outside its valid range: heart rate 30-230 bpm, temperature 25-42 °C, activity
  level 0.0-1.0, signal quality 0.0-1.0, timestamp a non-negative integer.
- Only observations with `signal_quality >= 0.7` are "usable" for classification.
- A session needs at least 3 usable observations, otherwise it is classified as
  `insufficient data`.
- Classification compares the average heart rate of usable observations against
  the participant's resting heart rate:
  - `resting`: less than 10% above baseline
  - `moderate activity`: 10% to 55% above baseline
  - `high activity`: more than 55% above baseline
  - `recovering`: overrides the above when the last 8 usable observations show
    heart rate declining by more than 20% relative to how elevated it was, and
    activity level is also decreasing, and the session was elevated at least
    5 bpm above baseline to begin with (`detect_recovery` in `calculations.py`)

## Installation and running instructions

This project only uses the Python standard library; no installation is required
beyond Python 3.10+.


```bash
python3 tests.py
```

## Example output

```text
Participant name: Kari Normann
Scenario (resting, moderate_activity, high_activity, recovery, poor_quality, random): high_activity
============================================================
FITNESS SESSION ANALYSIS REPORT
============================================================
Participant: Kari Normann
Resting heart rate: 65 bpm
------------------------------------------------------------
Classification: HIGH ACTIVITY (confidence 100%)
Reason: Average heart rate is significantly elevated above baseline.
------------------------------------------------------------
Observations: 12/12 usable (100.0%)
Heart rate: avg 126.7, min 113, max 141
Average activity level: 0.83
============================================================
```

## Known limitations

- The classification thresholds are tuned against the value ranges
  produced by `option_a_fitness/data_generator.py`; very different data
  distributions may need different thresholds.
- `detect_recovery` requires at least 8 usable observations; shorter sessions
  can never be classified as `recovering`.
- `main.py` analyzes one session per run. The 5 required scenarios (resting,
  moderate activity, high activity, recovery, poor-quality data) are
  demonstrated together in `sample_data.py` / `tests.py`, and interactively in
  `report.py`.