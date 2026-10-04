"""
Report generation functions for displaying session analysis results.
"""


import csv
from pathlib import Path


ANALYSIS_SUMMARY_FIELDS = [
    "session_id",
    "participant_id",
    "participant",
    "resting_heart_rate",
    "baseline_skin_response",
    "baseline_temperature",
    "classification",
    "confidence",
    "reason",
    "total_observations",
    "usable_observations",
    "usable_percent",
    "avg_heart_rate",
    "min_heart_rate",
    "max_heart_rate",
    "avg_activity_level",
    "avg_skin_response",
    "avg_temperature",
    "heart_rate_change",
    "skin_response_change",
    "temperature_change",
]


def write_analysis_summary_csv(
    session_results: list[dict], output_directory: Path
) -> Path:
    """Create the output directory and write one summary row per session."""
    output_directory.mkdir(parents=True, exist_ok=True)
    summary_path = output_directory / "analysis_summary.csv"

    with summary_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=ANALYSIS_SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(session_results)

    return summary_path


def write_analysis_report_txt(
    session_results: list[dict], output_directory: Path
) -> Path:
    """Write a readable explanation of each session's analysis results."""
    output_directory.mkdir(parents=True, exist_ok=True)
    report_path = output_directory / "analysis_report.txt"
    lines = [
        "FITNESS SESSION ANALYSIS REPORT",
        "=" * 32,
        "Only observations meeting the signal-quality threshold are used for these statistics.",
        "A positive baseline difference means the session average was above the participant's reference value.",
        "Confidence is the proportion of recorded observations that were usable; insufficient-data classifications have zero confidence.",
        "",
    ]

    for index, report in enumerate(session_results, start=1):
        lines.extend([
            f"Result {index}: Session {report['session_id']}",
            "-" * 32,
            f"Participant: {report['participant']} ({report['participant_id']})",
            f"Classification: {report['classification']} ({report['confidence'] * 100:.0f}% confidence)",
            f"Why: {report['reason']}",
            f"Usable observations: {report['usable_observations']} of {report['total_observations']} ({report['usable_percent']:.1f}%).",
        ])

        if report["usable_observations"]:
            lines.extend([
                f"Heart rate: average {report['avg_heart_rate']:.1f} bpm, ranging from {report['min_heart_rate']} to {report['max_heart_rate']} bpm.",
                f"Compared with the resting baseline of {report['resting_heart_rate']} bpm, average heart rate changed by {report['heart_rate_change']:+.1f} bpm.",
                f"Average activity level: {report['avg_activity_level']:.2f} on a 0-to-1 scale.",
            ])
            if report["skin_response_change"] is not None:
                lines.append(
                    f"Skin response: average {report['avg_skin_response']:.2f}, "
                    f"compared with baseline {report['baseline_skin_response']:.2f} "
                    f"(change {report['skin_response_change']:+.2f})."
                )
            else:
                lines.append("Skin response: baseline comparison is unavailable.")
            if report["temperature_change"] is not None:
                lines.append(
                    f"Temperature: average {report['avg_temperature']:.2f} C, "
                    f"compared with baseline {report['baseline_temperature']:.2f} C "
                    f"(change {report['temperature_change']:+.2f} C)."
                )
            else:
                lines.append("Temperature: baseline comparison is unavailable.")
        else:
            lines.append(
                "No usable observations were available, so session averages and baseline comparisons could not be calculated."
            )
        lines.append("")

    if not session_results:
        lines.append("No sessions were available to analyze.")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def write_rejected_records_txt(
    rejected_records: list[dict], output_directory: Path
) -> Path:
    """Write each rejected row's source, row number, field, and reason."""
    output_directory.mkdir(parents=True, exist_ok=True)
    rejected_path = output_directory / "rejected_records.txt"
    lines = ["REJECTED CSV RECORDS", "=" * 20, ""]

    if rejected_records:
        for rejected_record in rejected_records:
            lines.append(
                f"{rejected_record['source_file']} row "
                f"{rejected_record['row_number']}, "
                f"field {rejected_record['field']}: "
                f"{rejected_record['reason']}"
            )
    else:
        lines.append("No rejected records.")

    rejected_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rejected_path


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
    participant = session.participant
    baseline_heart_rate = participant.resting_heart_rate
    baseline_skin_response = participant.baseline_skin_response
    baseline_temperature = participant.baseline_temperature
    average_heart_rate = summary["average_heart_rate"]
    average_skin_response = summary["average_skin_response"]
    average_temperature = summary["average_temperature"]

    return {
        "session_id": session.session_id,
        "participant_id": participant.participant_id,
        "participant": participant.name,
        "resting_heart_rate": baseline_heart_rate,
        "baseline_skin_response": baseline_skin_response,
        "baseline_temperature": baseline_temperature,
        "classification": classification_result["classification"],
        "confidence": classification_result["confidence"],
        "reason": classification_result["reason"],
        "total_observations": total,
        "usable_observations": usable,
        "usable_percent": (usable / total * 100) if total else 0,
        "avg_heart_rate": average_heart_rate,
        "min_heart_rate": summary["min_heart_rate"],
        "max_heart_rate": summary["max_heart_rate"],
        "avg_activity_level": summary["average_activity_level"],
        "avg_skin_response": average_skin_response,
        "avg_temperature": average_temperature,
        "heart_rate_change": (
            average_heart_rate - baseline_heart_rate if usable else None
        ),
        "skin_response_change": (
            average_skin_response - baseline_skin_response
            if usable and baseline_skin_response is not None
            else None
        ),
        "temperature_change": (
            average_temperature - baseline_temperature
            if usable and baseline_temperature is not None
            else None
        ),
    }


def print_session_report(session, classification_result: dict) -> None:
    """
    Print a formatted console report for a session.
    """
    report = generate_session_report(session, classification_result)

    print("=" * 60)
    print("FITNESS SESSION ANALYSIS REPORT")
    print("=" * 60)
    print(f"Session: {report['session_id']}")
    print(f"Participant: {report['participant']}")
    print(f"Participant ID: {report['participant_id']}")
    print(
        f"Reference values: heart rate {report['resting_heart_rate']} bpm, "
        f"skin response {report['baseline_skin_response']}, "
        f"temperature {report['baseline_temperature']} C"
    )
    print("-" * 60)
    print(f"Classification: {report['classification'].upper()} (confidence {report['confidence'] * 100:.0f}%)")
    print(f"Reason: {report['reason']}")
    print("-" * 60)
    print(f"Observations: {report['usable_observations']}/{report['total_observations']} usable "
          f"({report['usable_percent']:.1f}%)")
    if report["usable_observations"]:
        print(f"Heart rate: avg {report['avg_heart_rate']:.1f}, min {report['min_heart_rate']}, "
              f"max {report['max_heart_rate']}")
        print(f"Average activity level: {report['avg_activity_level']:.2f}")
        print(
            f"Average heart rate vs baseline: "
            f"{report['heart_rate_change']:+.1f} bpm"
        )
        if report["skin_response_change"] is not None:
            print(
                f"Average skin response: {report['avg_skin_response']:.2f} "
                f"vs baseline {report['baseline_skin_response']:.2f} "
                f"({report['skin_response_change']:+.2f})"
            )
        if report["temperature_change"] is not None:
            print(
                f"Average temperature: {report['avg_temperature']:.2f} C "
                f"vs baseline {report['baseline_temperature']:.2f} C "
                f"({report['temperature_change']:+.2f} C)"
            )
    else:
        print("No usable heart-rate or activity measurements are available.")
        print("No usable observations are available for baseline comparisons.")
    print("=" * 60)


def generate_summary_table(session_results: list[dict]) -> str:
    """
    Build a compact multi-session comparison table.

    Args:
        session_results: List of report dictionaries from generate_session_report()

    Returns:
        Formatted table string.
    """
    header = (
        f"{'Session':<16}{'Participant':<20}{'Classification':<22}"
        f"{'Avg HR':<10}{'Usable %':<10}"
    )
    lines = [header, "-" * len(header)]
    for report in session_results:
        s_average_heart_rate = (
            f"{report['avg_heart_rate']:.1f}"
            if report["usable_observations"]
            else "n/a"
        )
        lines.append(
            f"{report['session_id']:<16}{report['participant']:<20}"
            f"{report['classification']:<22}{s_average_heart_rate:<10}"
            f"{report['usable_percent']:<10.1f}"
        )
    return "\n".join(lines)
