"""
Report generation functions for displaying session analysis results.
"""


def generate_session_report(session, classification_result: dict) -> dict:
    """
    Build a structured report dictionary from a session and its classification.

    Args:
        session: Session object
        classification_result: Result dictionary from SessionClassifier

    Returns:
        Dictionary describing the session and its classification.
    """
    summary = session.get_session_summary()
    total = summary["total_observations"]
    usable = summary["good_quality_observations"]

    return {
        "participant": session.participant.name,
        "resting_heart_rate": session.participant.resting_heart_rate,
        "classification": classification_result["classification"],
        "confidence": classification_result["confidence"],
        "reason": classification_result["reason"],
        "total_observations": total,
        "usable_observations": usable,
        "usable_percent": (usable / total * 100) if total else 0,
        "avg_heart_rate": summary["average_heart_rate"],
        "min_heart_rate": summary["min_heart_rate"],
        "max_heart_rate": summary["max_heart_rate"],
        "avg_activity_level": summary["average_activity_level"],
    }


def print_session_report(session, classification_result: dict) -> None:
    """
    Print a formatted console report for a session.
    """
    report = generate_session_report(session, classification_result)

    print("=" * 60)
    print("FITNESS SESSION ANALYSIS REPORT")
    print("=" * 60)
    print(f"Participant: {report['participant']}")
    print(f"Resting heart rate: {report['resting_heart_rate']} bpm")
    print("-" * 60)
    print(f"Classification: {report['classification'].upper()} (confidence {report['confidence'] * 100:.0f}%)")
    print(f"Reason: {report['reason']}")
    print("-" * 60)
    print(f"Observations: {report['usable_observations']}/{report['total_observations']} usable "
          f"({report['usable_percent']:.1f}%)")
    print(f"Heart rate: avg {report['avg_heart_rate']:.1f}, min {report['min_heart_rate']}, "
          f"max {report['max_heart_rate']}")
    print(f"Average activity level: {report['avg_activity_level']:.2f}")
    print("=" * 60)


def generate_summary_table(session_results: list[dict]) -> str:
    """
    Build a compact multi-session comparison table.

    Args:
        session_results: List of report dictionaries from generate_session_report()

    Returns:
        Formatted table string.
    """
    header = f"{'Participant':<20}{'Classification':<20}{'Avg HR':<10}{'Usable %':<10}"
    lines = [header, "-" * len(header)]
    for report in session_results:
        lines.append(
            f"{report['participant']:<20}{report['classification']:<20}"
            f"{report['avg_heart_rate']:<10.1f}{report['usable_percent']:<10.1f}"
        )
    return "\n".join(lines)
