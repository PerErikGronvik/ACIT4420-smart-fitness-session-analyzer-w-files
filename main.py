"""
Main entry point for the Smart Fitness Session Analyzer.
"""

from option_a_fitness.data_generator import generate_fitness_data, available_scenarios
from src.participant import Participant
from src.session import Session
from src.classifier import SessionClassifier
from src.report import print_session_report, generate_session_report


def ask_participant_name() -> str:
    """Prompt for a non-empty participant name."""
    while True:
        name = input("Participant name: ").strip()
        if name:
            return name
        print("Name cannot be empty.")


def ask_scenario() -> str:
    """Prompt for a simulated condition, or 'random' to let the generator decide."""
    choices = list(available_scenarios()) + ["random"]
    while True:
        scenario = input(f"Scenario ({', '.join(choices)}): ").strip()
        if scenario in choices:
            return scenario
        print(f"Unknown scenario '{scenario}'. Choose one of: {', '.join(choices)}")


def main() -> dict:
    """Analyze one incoming wearable session and print its report."""
    participant_name = ask_participant_name()
    scenario = ask_scenario()

    profile, observations = generate_fitness_data(participant_name, scenario, number_of_windows=12)

    participant = Participant(participant_name, profile["baseline_heart_rate"], 0.1)
    session = Session(participant)

    for observation in observations:
        ok, message = session.add_observation(observation)
        if not ok:
            print(f"Rejected: {message}")

    result = SessionClassifier.classify_session(session)
    print_session_report(session, result)
    print(SessionClassifier.get_classification_rules())

    return generate_session_report(session, result)


if __name__ == "__main__":
    main()

