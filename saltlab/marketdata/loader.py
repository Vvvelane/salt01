"""Streaming, read-only CSV access."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Iterator, Mapping


class CsvLoadError(ValueError):
    pass


@dataclass(frozen=True)
class CsvRow:
    line_number: int
    values: Mapping[str, str]


class CsvLoader:
    """Open one CSV at a time and yield rows without materializing the file."""

    def __init__(self, *, encoding: str = "utf-8-sig") -> None:
        self.encoding = encoding

    def header(self, path: str | Path) -> tuple[str, ...]:
        with Path(path).open("r", encoding=self.encoding, newline="") as handle:
            reader = csv.reader(handle)
            try:
                fields = next(reader)
            except StopIteration as exc:
                raise CsvLoadError(f"empty CSV: {path}") from exc
        self._validate_header(fields, path)
        return tuple(fields)

    def rows(self, path: str | Path, *, max_rows: int | None = None) -> Iterator[CsvRow]:
        if max_rows is not None and max_rows < 0:
            raise ValueError("max_rows must be non-negative or None")

        def generate() -> Iterator[CsvRow]:
            with Path(path).open("r", encoding=self.encoding, newline="") as handle:
                reader = csv.DictReader(handle)
                fields = reader.fieldnames
                if fields is None:
                    raise CsvLoadError(f"empty CSV: {path}")
                self._validate_header(fields, path)
                for row_number, row in enumerate(reader, start=2):
                    if max_rows is not None and row_number - 2 >= max_rows:
                        break
                    if None in row:
                        raise CsvLoadError(f"extra CSV fields at line {row_number}: {path}")
                    if any(value is None for value in row.values()):
                        raise CsvLoadError(f"missing CSV field at line {row_number}: {path}")
                    yield CsvRow(row_number, MappingProxyType(dict(row)))

        return generate()

    @staticmethod
    def _validate_header(fields: list[str], path: str | Path) -> None:
        if not fields or any(not field.strip() for field in fields):
            raise CsvLoadError(f"blank CSV header field: {path}")
        if len(fields) != len(set(fields)):
            raise CsvLoadError(f"duplicate CSV header field: {path}")
