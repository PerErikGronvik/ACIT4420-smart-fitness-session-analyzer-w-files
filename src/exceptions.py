"""Domain-specific exceptions used by the Assignment II application."""


class InvalidIdentifierError(ValueError):
    """Raised when a participant or session identifier has an invalid format."""


class RejectedCsvRowError(ValueError):
    """Raised when a CSV row or field fails validation."""

    def __init__(
        self,
        source_file: str,
        row_number: int,
        field: str,
        reason: str,
    ) -> None:
        self.source_file = source_file
        self.row_number = row_number
        self.field = field
        self.reason = reason
        super().__init__(reason)