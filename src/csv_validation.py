"""CSV schemas and validation helpers for the Assignment II input files."""

import math
import re
from collections.abc import Callable

from src.exceptions import InvalidIdentifierError, RejectedCsvRowError


VERBOSE = True

PROFILE_FIELDS = [
    "participant_id",
    "name",
    "baseline_heart_rate",
    "baseline_skin_response",
    "baseline_temperature",
]
SESSION_FIELDS = [
    "session_id",
    "participant_id",
    "timestamp",
    "heart_rate",
    "skin_response",
    "temperature",
    "activity_level",
    "signal_quality",
]
PROFILE_NUMERIC_RULES: dict[
    str, tuple[Callable[[str], int | float], float | None, float | None]
] = {
    "baseline_heart_rate": (int, 30, 230),
    "baseline_skin_response": (float, 0, None),
    "baseline_temperature": (float, 25, 42),
}
SESSION_NUMERIC_RULES: dict[
    str, tuple[Callable[[str], int | float], float | None, float | None]
] = {
    "timestamp": (int, 0, None),
    "heart_rate": (int, 30, 230),
    "skin_response": (float, 0, None),
    "temperature": (float, 25, 42),
    "activity_level": (float, 0, 1),
    "signal_quality": (float, 0, 1),
}
ValidationIssue = dict[str, str | int]


def create_validation_issue(
    s_source_name: str,
    i_row_number: int,
    s_field: str,
    s_reason: str,
) -> ValidationIssue:
    """Raise and handle a row rejection, returning it as a structured finding."""
    try:
        raise RejectedCsvRowError(
            s_source_name, i_row_number, s_field, s_reason
        )
    except RejectedCsvRowError as error:
        if VERBOSE:
            print(
                f"Caught RejectedCsvRowError in {error.source_file} row "
                f"{error.row_number}, field {error.field}: {error.reason}"
            )
        return {
            "source_file": error.source_file,
            "row_number": error.row_number,
            "field": error.field,
            "reason": error.reason,
        }


def is_valid_participant_id(s_identifier: object) -> bool:
    """Return whether a participant ID is P followed by exactly three digits."""
    return (
        isinstance(s_identifier, str)
        and re.fullmatch(r"P[0-9]{3}", s_identifier) is not None
    )


def is_valid_session_id(s_identifier: object) -> bool:
    """Return whether a session ID matches FIT-YYYY-NNN."""
    return (
        isinstance(s_identifier, str)
        and re.fullmatch(r"FIT-[0-9]{4}-[0-9]{3}", s_identifier) is not None
    )


def require_valid_participant_id(s_identifier: object) -> None:
    """Raise InvalidIdentifierError unless the value is a valid participant ID."""
    if not is_valid_participant_id(s_identifier):
        raise InvalidIdentifierError(
            f"Expected P followed by three digits; got {s_identifier!r}."
        )


def require_valid_session_id(s_identifier: object) -> None:
    """Raise InvalidIdentifierError unless the value is a valid session ID."""
    if not is_valid_session_id(s_identifier):
        raise InvalidIdentifierError(
            f"InvalidIdentifierError: Expected FIT-YYYY-NNN; got {s_identifier!r}."
        )


def validate_profile_ids(
    s_source_name: str,
    ld_profile_rows: list[dict[str | None, str | list[str] | None]],
) -> list[ValidationIssue]:
    """Return contextual errors for profile rows with malformed participant IDs."""
    ld_validation_errors = []
    for i_row_number, ld_profile_row in enumerate(ld_profile_rows, start=2):
        s_participant_id = ld_profile_row.get("participant_id")
        try:
            require_valid_participant_id(s_participant_id)
        except InvalidIdentifierError as error:
            if VERBOSE:
                print(
                    f"Caught InvalidIdentifierError in {s_source_name} row "
                    f"{i_row_number}, field participant_id: {error}"
                )
            ld_validation_errors.append(create_validation_issue(
                s_source_name,
                i_row_number,
                "participant_id",
                str(error),
            ))
    return ld_validation_errors


def validate_session_ids(
    s_source_name: str,
    ld_session_rows: list[dict[str | None, str | list[str] | None]],
) -> list[ValidationIssue]:
    """Return contextual errors for malformed session and participant IDs."""
    ld_validation_errors = []
    for i_row_number, ld_session_row in enumerate(ld_session_rows, start=2):
        s_session_id = ld_session_row.get("session_id")
        s_participant_id = ld_session_row.get("participant_id")
        try:
            require_valid_session_id(s_session_id)
        except InvalidIdentifierError as error:
            if VERBOSE:
                print(
                    f"Caught InvalidIdentifierError in {s_source_name} row "
                    f"{i_row_number}, field session_id: {error}"
                )
            ld_validation_errors.append(create_validation_issue(
                s_source_name,
                i_row_number,
                "session_id",
                str(error),
            ))
        try:
            require_valid_participant_id(s_participant_id)
        except InvalidIdentifierError as error:
            if VERBOSE:
                print(
                    f"Caught InvalidIdentifierError in {s_source_name} row "
                    f"{i_row_number}, field participant_id: {error}"
                )
            ld_validation_errors.append(create_validation_issue(
                s_source_name,
                i_row_number,
                "participant_id",
                str(error),
            ))
    return ld_validation_errors


def validate_session_participants(
    s_source_name: str,
    ld_session_rows: list[dict[str | None, str | list[str] | None]],
    ds_known_participant_ids: set[str],
) -> list[ValidationIssue]:
    """Return contextual errors for session rows referencing unknown participants."""
    ld_validation_errors = []
    for i_row_number, ld_session_row in enumerate(ld_session_rows, start=2):
        s_participant_id = ld_session_row.get("participant_id")
        if (
            is_valid_participant_id(s_participant_id)
            and s_participant_id not in ds_known_participant_ids
        ):
            ld_validation_errors.append(create_validation_issue(
                s_source_name,
                i_row_number,
                "participant_id",
                f"{s_participant_id!r} is not present in participants.csv.",
            ))
    return ld_validation_errors


def validate_csv_rows(
    s_source_name: str,
    ld_csv_rows: list[dict[str | None, str | list[str] | None]],
    ls_expected_fields: list[str],
) -> list[ValidationIssue]:
    """Report missing required fields and row lengths that do not match the schema."""
    ld_validation_errors = []
    i_expected_length = len(ls_expected_fields)

    for i_row_number, ld_csv_row in enumerate(ld_csv_rows, start=2):
        for s_field in ls_expected_fields:
            s_value = ld_csv_row.get(s_field)
            if s_value is None or (isinstance(s_value, str) and not s_value.strip()):
                ld_validation_errors.append(create_validation_issue(
                    s_source_name,
                    i_row_number,
                    s_field,
                    "Required field is blank or missing.",
                ))

        i_actual_length = sum(
            s_field in ld_csv_row and ld_csv_row[s_field] is not None
            for s_field in ld_csv_row
            if s_field is not None
        )
        v_extra_fields = ld_csv_row.get(None)
        if isinstance(v_extra_fields, list):
            i_actual_length += len(v_extra_fields)

        if i_actual_length != i_expected_length:
            ld_validation_errors.append(create_validation_issue(
                s_source_name,
                i_row_number,
                "row",
                f"Expected {i_expected_length} columns; found {i_actual_length}.",
            ))

        ls_unexpected_fields = [
            s_field
            for s_field in ld_csv_row
            if s_field is not None and s_field not in ls_expected_fields
        ]
        if ls_unexpected_fields:
            for s_field in ls_unexpected_fields:
                ld_validation_errors.append(create_validation_issue(
                    s_source_name,
                    i_row_number,
                    s_field,
                    "Unexpected column in row.",
                ))

    return ld_validation_errors


def has_valid_csv_shape(
    ld_csv_row: dict[str | None, str | list[str] | None],
    ls_expected_fields: list[str],
) -> bool:
    """Return whether a row has every nonblank expected field and no extra columns."""
    return all(
        isinstance(ld_csv_row.get(s_field), str)
        and bool(ld_csv_row[s_field].strip())
        for s_field in ls_expected_fields
    ) and all(
        s_field is not None and s_field in ls_expected_fields
        for s_field in ld_csv_row
    )


def convert_and_validate_numeric_fields(
    s_source_name: str,
    i_row_number: int,
    ld_csv_row: dict[str | None, str | list[str] | None],
    d_numeric_rules: dict[
        str, tuple[Callable[[str], int | float], float | None, float | None]
    ],
    ld_numeric_errors: list[ValidationIssue],
) -> bool:
    """Convert numeric fields and report conversion or range failures for a row."""
    d_converted_values: dict[str, int | float] = {}
    b_row_is_valid = True

    for s_field, (f_converter, n_minimum, n_maximum) in d_numeric_rules.items():
        s_raw_value = ld_csv_row.get(s_field)
        if not isinstance(s_raw_value, str) or not s_raw_value.strip():
            b_row_is_valid = False
            continue

        try:
            n_value = f_converter(s_raw_value)
        except (TypeError, ValueError, OverflowError):
            s_expected_type = "integer" if f_converter is int else "number"
            ld_numeric_errors.append(create_validation_issue(
                s_source_name,
                i_row_number,
                s_field,
                f"Cannot convert {s_raw_value!r} to an {s_expected_type}.",
            ))
            b_row_is_valid = False
            continue

        if isinstance(n_value, float) and not math.isfinite(n_value):
            ld_numeric_errors.append(create_validation_issue(
                s_source_name,
                i_row_number,
                s_field,
                f"Expected a finite number; got {s_raw_value!r}.",
            ))
            b_row_is_valid = False
            continue

        if (
            (n_minimum is not None and n_value < n_minimum)
            or (n_maximum is not None and n_value > n_maximum)
        ):
            if n_minimum is None:
                s_allowed_range = f"at most {n_maximum}"
            elif n_maximum is None:
                s_allowed_range = f"at least {n_minimum}"
            else:
                s_allowed_range = f"between {n_minimum} and {n_maximum}"
            ld_numeric_errors.append(create_validation_issue(
                s_source_name,
                i_row_number,
                s_field,
                f"Value {n_value} is outside the allowed range ({s_allowed_range}).",
            ))
            b_row_is_valid = False
            continue

        d_converted_values[s_field] = n_value

    if b_row_is_valid:
        ld_csv_row.update(d_converted_values)
    return b_row_is_valid