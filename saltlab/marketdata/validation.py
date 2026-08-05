"""Sample-level CSV schema and value validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Callable

from .config import FieldSemantics
from .loader import CsvLoader, CsvRow


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    line_number: int | None = None


@dataclass(frozen=True)
class ValidationReport:
    path: Path
    header: tuple[str, ...]
    sampled_rows: int
    first_timestamp: datetime | None
    last_timestamp: datetime | None
    issues: tuple[ValidationIssue, ...]
    sample_limited: bool

    @property
    def valid(self) -> bool:
        return not self.issues

    def raise_if_invalid(self) -> None:
        if self.issues:
            summary = "; ".join(issue.message for issue in self.issues[:3])
            raise ValueError(f"CSV validation failed for {self.path}: {summary}")


class CsvValidator:
    def __init__(self, loader: CsvLoader | None = None) -> None:
        self.loader = loader or CsvLoader()

    def validate(
        self,
        path: str | Path,
        fields: FieldSemantics,
        *,
        timestamp_parser: Callable[[str], datetime],
        sample_rows: int = 2000,
    ) -> ValidationReport:
        if sample_rows <= 0:
            raise ValueError("sample_rows must be positive")
        path = Path(path)
        try:
            header = self.loader.header(path)
        except Exception as exc:
            return ValidationReport(
                path, (), 0, None, None,
                (ValidationIssue("header_error", str(exc)),), True,
            )

        issues = list(self.validate_header(header, fields))
        first_timestamp = None
        last_timestamp = None
        sampled = 0
        previous = None
        for row in self.loader.rows(path, max_rows=sample_rows):
            sampled += 1
            self._validate_row(row, fields, timestamp_parser, issues)
            raw_timestamp = row.values.get(fields.datetime_column, "")
            try:
                current = timestamp_parser(raw_timestamp)
                if first_timestamp is None:
                    first_timestamp = current
                if previous is not None and current <= previous:
                    issues.append(ValidationIssue("non_increasing_timestamp", "timestamps are not strictly increasing", row.line_number))
                previous = current
                last_timestamp = current
            except Exception:
                pass
        return ValidationReport(
            path=path,
            header=header,
            sampled_rows=sampled,
            first_timestamp=first_timestamp,
            last_timestamp=last_timestamp,
            issues=tuple(issues),
            sample_limited=sampled >= sample_rows,
        )

    @staticmethod
    def validate_header(header: tuple[str, ...], fields: FieldSemantics) -> tuple[ValidationIssue, ...]:
        missing = [column for column in fields.required_columns if column not in header]
        return tuple(
            ValidationIssue("missing_column", f"missing required column: {column}")
            for column in missing
        )

    @staticmethod
    def _validate_row(
        row: CsvRow,
        fields: FieldSemantics,
        timestamp_parser: Callable[[str], datetime],
        issues: list[ValidationIssue],
    ) -> None:
        for column in fields.required_columns:
            if not row.values.get(column, "").strip():
                issues.append(ValidationIssue("missing_value", f"empty value in {column}", row.line_number))
        try:
            timestamp_parser(row.values.get(fields.datetime_column, ""))
        except Exception as exc:
            issues.append(ValidationIssue("invalid_timestamp", str(exc), row.line_number))
        numeric_columns = [
            fields.open_column,
            fields.high_column,
            fields.low_column,
            fields.close_column,
            fields.volume_column,
            fields.notional_column,
            fields.open_interest_column,
        ]
        for column in numeric_columns:
            if column is None or not row.values.get(column, "").strip():
                continue
            try:
                value = Decimal(row.values[column])
                if not value.is_finite():
                    raise InvalidOperation("non-finite numeric value")
            except (InvalidOperation, ValueError) as exc:
                issues.append(ValidationIssue("invalid_numeric", f"invalid numeric {column}: {exc}", row.line_number))
