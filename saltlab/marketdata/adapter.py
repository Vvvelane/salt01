"""Streaming normalization of the three audited CSV schema families."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterator

from nacl_quant.data import DataCapabilities, MarketBar

from .catalog import CatalogEntry
from .config import AdapterConfig, FieldSemantics
from .loader import CsvLoader, CsvRow
from .validation import CsvValidator, ValidationReport


class AdapterError(ValueError):
    pass


class CsvMarketDataAdapter:
    """Adapt one configured CSV stream; it never caches or writes market data."""

    def __init__(self, loader: CsvLoader | None = None) -> None:
        self.loader = loader or CsvLoader()
        self.validator = CsvValidator(self.loader)

    def capabilities(self, config: AdapterConfig) -> DataCapabilities:
        return DataCapabilities(config.fields.capabilities)

    def adapt(
        self,
        source: str | Path | CatalogEntry,
        config: AdapterConfig,
        *,
        max_rows: int | None = None,
    ) -> Iterator[MarketBar]:
        config.require_complete()
        path = source.path if isinstance(source, CatalogEntry) else Path(source)
        if isinstance(source, CatalogEntry) and source.source_id != config.identity.source_id:
            raise AdapterError("DatasetIdentity.source_id must match CatalogEntry.source_id")
        self._validate_header(path, config.fields)
        for row in self.loader.rows(path, max_rows=max_rows):
            yield self._adapt_row(row, config)

    def validate_sample(
        self,
        source: str | Path | CatalogEntry,
        config: AdapterConfig,
        *,
        sample_rows: int = 2000,
    ) -> ValidationReport:
        config.require_complete()
        path = source.path if isinstance(source, CatalogEntry) else Path(source)
        return self.validator.validate(
            path,
            config.fields,
            timestamp_parser=config.timestamp.parse,
            sample_rows=sample_rows,
        )

    @staticmethod
    def _validate_header(path: Path, fields: FieldSemantics) -> None:
        loader = CsvLoader()
        header = loader.header(path)
        issues = CsvValidator.validate_header(header, fields)
        if issues:
            raise AdapterError("; ".join(issue.message for issue in issues))

    @staticmethod
    def _adapt_row(row: CsvRow, config: AdapterConfig) -> MarketBar:
        fields = config.fields
        try:
            raw_timestamp = config.timestamp.parse(row.values[fields.datetime_column])
            bar_start, bar_end = config.timestamp.bounds(raw_timestamp)
            available_at = config.timestamp.resolve_available_at(raw_timestamp, bar_start, bar_end)
            resolution = config.session_resolver.resolve(config.identity.instrument_id, bar_start)  # type: ignore[union-attr]
            return MarketBar(
                instrument_id=config.identity.instrument_id,
                source_symbol=fields.source_symbol_for(dict(row.values)) or config.identity.source_symbol,
                interval=config.timestamp.interval.label,  # type: ignore[union-attr]
                bar_start=bar_start,
                bar_end=bar_end,
                available_at=available_at,
                open=CsvMarketDataAdapter._decimal(row, fields.open_column),
                high=CsvMarketDataAdapter._decimal(row, fields.high_column),
                low=CsvMarketDataAdapter._decimal(row, fields.low_column),
                close=CsvMarketDataAdapter._decimal(row, fields.close_column),
                volume=CsvMarketDataAdapter._optional_decimal(row, fields.volume_column),
                notional=CsvMarketDataAdapter._optional_decimal(row, fields.notional_column),
                open_interest=CsvMarketDataAdapter._optional_decimal(row, fields.open_interest_column),
                trading_date=resolution.trading_date,
                session_id=resolution.session_id,
                source_id=config.identity.source_id,
            )
        except KeyError as exc:
            raise AdapterError(f"missing configured field at line {row.line_number}: {exc}") from exc
        except Exception as exc:
            if isinstance(exc, AdapterError):
                raise
            raise AdapterError(f"cannot adapt line {row.line_number}: {exc}") from exc

    @staticmethod
    def _decimal(row: CsvRow, column: str) -> Decimal:
        value = row.values.get(column, "").strip()
        if not value:
            raise AdapterError(f"empty required numeric field {column}")
        try:
            parsed = Decimal(value)
        except InvalidOperation as exc:
            raise AdapterError(f"invalid numeric field {column}: {value!r}") from exc
        if not parsed.is_finite():
            raise AdapterError(f"non-finite numeric field {column}")
        return parsed

    @staticmethod
    def _optional_decimal(row: CsvRow, column: str | None) -> Decimal | None:
        if column is None or not row.values.get(column, "").strip():
            return None
        return CsvMarketDataAdapter._decimal(row, column)
