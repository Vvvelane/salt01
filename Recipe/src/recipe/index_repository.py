from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import duckdb

from .settings import Settings, settings

REQUIRED_VIEWS = (
    "v_catalog_revision",
    "v_exchanges",
    "v_products",
    "v_dataset_availability",
    "v_market_series",
    "v_dataset_fields",
    "v_instrument_master",
    "v_trading_calendar",
    "v_session_rules",
    "v_contract_lifecycle",
)

# Quality views remain readable for backwards-compatible API clients, but are
# not part of the current Recipe product scope or index readiness contract.


class IndexErrorBase(Exception):
    code = "index_error"


class IndexUnavailable(IndexErrorBase):
    code = "index_unavailable"


class IndexContractError(IndexErrorBase):
    code = "index_contract_error"


class QueryValidationError(IndexErrorBase):
    code = "invalid_query"


@dataclass(frozen=True)
class IndexState:
    dsn: str | None
    available: bool
    contract_ready: bool
    catalog_revision: str | None
    schema_version: str | None
    missing_views: tuple[str, ...]
    message: str | None = None


def _json(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _records(cursor: duckdb.DuckDBPyConnection) -> list[dict[str, Any]]:
    columns = [item[0] for item in cursor.description]
    return [{column: _json(value) for column, value in zip(columns, row)} for row in cursor.fetchall()]


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        iso_value = value[:-1] + "+00:00" if value.endswith("Z") else value
        parsed = datetime.fromisoformat(iso_value)
        return parsed.astimezone(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None) if parsed.tzinfo else parsed
    except ValueError as exc:
        raise QueryValidationError(f"invalid datetime: {value}") from exc


def _default_window(start: str | None, end: str | None, days: int = 90) -> tuple[datetime, datetime]:
    now = datetime.now(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None, hour=23, minute=59, second=59, microsecond=0)
    end_dt = _parse_iso(end) or now
    start_dt = _parse_iso(start) or end_dt - timedelta(days=days)
    if start_dt > end_dt:
        raise QueryValidationError("start must not be after end")
    if end_dt - start_dt > timedelta(days=366):
        raise QueryValidationError("first-phase query range is limited to 366 days")
    return start_dt, end_dt


def _row_datetime(value: Any) -> datetime | None:
    """Parse a timestamp returned from a source Parquet file."""

    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    if isinstance(value, date):
        return datetime.combine(value, time.min)
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace('Z', '+00:00'))
    except ValueError:
        return None
    return parsed.replace(tzinfo=None)


def _contract_base(value: str) -> str:
    return str(value).strip().upper().split('.', 1)[0]


class IndexRepository:
    """Read-only access to the published DuckDB index contract.

    This class deliberately has no data-root argument and no directory scan.
    Physical paths can only arrive through an index-owned storage_locator.
    """

    def __init__(self, config: Settings = settings):
        self.config = config

    def _dsn(self) -> str:
        if not self.config.index_dsn:
            raise IndexUnavailable("RECIPE_INDEX_DSN is not configured")
        return str(self.config.index_dsn)

    def connect(self) -> duckdb.DuckDBPyConnection:
        dsn = self._dsn()
        if dsn != ":memory:" and not Path(dsn).is_file():
            raise IndexUnavailable(f"index does not exist: {dsn}")
        try:
            return duckdb.connect(dsn, read_only=dsn != ":memory:")
        except (duckdb.Error, OSError, KeyError, TypeError, ValueError) as exc:
            raise IndexUnavailable(f"cannot open DuckDB index: {dsn}") from exc

    def state(self) -> IndexState:
        try:
            con = self.connect()
        except IndexErrorBase as exc:
            return IndexState(self.config.index_dsn, False, False, None, None, REQUIRED_VIEWS, str(exc))
        try:
            views = {
                row[0]
                for row in con.execute(
                    "select table_name from information_schema.tables where table_schema='main'"
                ).fetchall()
            }
            missing = tuple(view for view in REQUIRED_VIEWS if view not in views)
            if "v_catalog_revision" in views:
                row = con.execute("select catalog_revision, schema_version from v_catalog_revision limit 1").fetchone()
                revision, schema_version = (row if row else (None, None))
            else:
                revision, schema_version = None, None
            return IndexState(self.config.index_dsn, True, not missing, revision, schema_version, missing, None if not missing else "published index is missing required views")
        except (duckdb.Error, OSError, KeyError, TypeError, ValueError) as exc:
            return IndexState(self.config.index_dsn, True, False, None, None, REQUIRED_VIEWS, str(exc))
        finally:
            con.close()

    def require_contract(self) -> duckdb.DuckDBPyConnection:
        state = self.state()
        if not state.available:
            raise IndexUnavailable(state.message or "index unavailable")
        if not state.contract_ready:
            raise IndexContractError("index contract is incomplete: " + ", ".join(state.missing_views))
        return self.connect()

    def revision_meta(self, con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
        row = con.execute("select * from v_catalog_revision limit 1").fetchone()
        columns = [item[0] for item in con.description]
        return {key: _json(value) for key, value in zip(columns, row)} if row else {}

    def exchanges(self) -> list[dict[str, Any]]:
        con = self.require_contract()
        try:
            return _records(con.execute("select * from v_exchanges order by exchange_id"))
        finally:
            con.close()

    def products(self, exchange_id: str | None = None) -> list[dict[str, Any]]:
        con = self.require_contract()
        try:
            if exchange_id:
                return _records(con.execute("select * from v_products where upper(exchange_id)=upper(?) order by product_id", [exchange_id]))
            return _records(con.execute("select * from v_products order by exchange_id, product_id"))
        finally:
            con.close()

    def product(self, product_id: str) -> dict[str, Any] | None:
        con = self.require_contract()
        try:
            rows = _records(con.execute("select * from v_products where upper(product_id)=upper(?) limit 1", [product_id]))
            return rows[0] if rows else None
        finally:
            con.close()

    def availability(self, product_id: str) -> list[dict[str, Any]]:
        con = self.require_contract()
        try:
            return _records(con.execute("select * from v_dataset_availability where upper(product_id)=upper(?) order by dataset_key", [product_id]))
        finally:
            con.close()

    def fields(self, dataset_key: str | None = None) -> list[dict[str, Any]]:
        con = self.require_contract()
        try:
            if dataset_key:
                return _records(con.execute("select * from v_dataset_fields where dataset_key=? order by field_name", [dataset_key]))
            return _records(con.execute("select * from v_dataset_fields order by dataset_key, field_name"))
        finally:
            con.close()

    def quality_summary(self, product_id: str) -> list[dict[str, Any]]:
        con = self.require_contract()
        try:
            return _records(con.execute("select * from v_quality_product_summary where upper(product_id)=upper(?) order by quality_run_id desc", [product_id]))
        finally:
            con.close()

    def quality_events(self, product_id: str, limit: int = 200) -> list[dict[str, Any]]:
        con = self.require_contract()
        try:
            return _records(con.execute("select * from v_quality_events where upper(product_id)=upper(?) order by event_time desc nulls last limit ?", [product_id, limit]))
        finally:
            con.close()

    def series(self, product_id: str, series_kind: str | None = None, frequency: str | None = None, contracts: Iterable[str] | None = None) -> list[dict[str, Any]]:
        con = self.require_contract()
        try:
            clauses = ["upper(product_id)=upper(?)"]
            params: list[Any] = [product_id]
            if series_kind:
                clauses.append("series_kind=?")
                params.append(series_kind)
            if frequency:
                clauses.append("frequency=?")
                params.append(frequency)
            contract_values = [_contract_base(str(value)) for value in (contracts or []) if str(value).strip()]
            if contract_values:
                placeholders = ",".join("?" for _ in contract_values)
                clauses.append(f"(contract_code is null or upper(split_part(contract_code, '.', 1)) in ({placeholders}))")
                params.extend(contract_values)
            sql = "select * from v_market_series where " + " and ".join(clauses) + " order by frequency, series_kind, contract_code nulls first, series_id"
            return _records(con.execute(sql, params))
        finally:
            con.close()

    def _calendar_dates(self, con: duckdb.DuckDBPyConnection, start: date, end: date) -> set[date]:
        rows = con.execute(
            """
            select distinct trading_date
            from v_trading_calendar
            where trading_date between ?::DATE and ?::DATE
              and status = 'OFFICIAL'
            """,
            [start, end],
        ).fetchall()
        return {row[0] for row in rows if isinstance(row[0], date)}

    def _session_rules_for(self, con: duckdb.DuckDBPyConnection, product_id: str, trading_date: date) -> list[dict[str, Any]]:
        return _records(con.execute(
            """
            select *
            from v_session_rules
            where upper(product_id) = upper(?)
              and (effective_start is null or effective_start <= ?::DATE)
              and (effective_end is null or effective_end >= ?::DATE)
            order by start_time, session_id
            """,
            [product_id, trading_date, trading_date],
        ))

    def _require_active_contract(self, con: duckdb.DuckDBPyConnection, product_id: str, contract: str, trading_date: date) -> None:
        contract_base = _contract_base(contract)
        count = con.execute(
            """
            select count(*)
            from v_contract_lifecycle
            where upper(product_id) = upper(?)
              and upper(split_part(contract_code, '.', 1)) = upper(?)
              and (effective_start is null or effective_start <= ?::DATE)
              and (effective_end is null or effective_end >= ?::DATE)
            """,
            [product_id, contract_base, trading_date, trading_date],
        ).fetchone()[0]
        if not count:
            raise QueryValidationError(f"contract is not active on trading_date: {contract_base} {trading_date.isoformat()}")

    def _daily_main_from_1min(
        self,
        product_id: str,
        start: datetime,
        end: datetime,
        limit: int,
    ) -> dict[str, Any]:
        """Select all-contract daily bars using the vendor main 1min contract map.

        The vendor main-daily series has no row contract identity.  The main
        1min series does, so it is used as the authoritative daily selector;
        the actual OHLCV values then come from the corresponding contract
        daily files.
        """

        main_1min = self.series(product_id, 'main_continuous', '1min')
        if not main_1min:
            raise IndexUnavailable(f"no main_continuous/1min series for {product_id}")
        con = self.require_contract()
        try:
            trading_dates = self._calendar_dates(con, start.date(), end.date())
            if not trading_dates:
                return {
                    'bars': [], 'series': [], 'truncated': False, 'limit': limit,
                    'selection_source': 'market.main.1min -> market.contract.daily',
                    'semantic_status': {'timezone': 'confirmed', 'timestamp_semantics': 'confirmed', 'trading_date': 'confirmed', 'session': 'not_applicable'},
                    'warnings': [{'code': 'no_trading_dates', 'message': 'No official trading dates in the requested range.'}],
                }
            mapping_start = datetime.combine(start.date() - timedelta(days=1), time.min)
            mapping_end = datetime.combine(end.date() + timedelta(days=1), time.max)
            source_rows: list[dict[str, Any]] = []
            for series_row in main_1min:
                source_rows.extend(self._read_locator(con, series_row, mapping_start, mapping_end, 200000))

            day_counts: dict[date, Counter[str]] = defaultdict(Counter)
            all_counts: dict[date, Counter[str]] = defaultdict(Counter)
            for row in source_rows:
                timestamp = _row_datetime(row.get('timestamp'))
                contract = row.get('contract_code') or row.get('source_symbol')
                if timestamp is None or not contract or timestamp.date() not in trading_dates:
                    continue
                contract_base = _contract_base(str(contract))
                all_counts[timestamp.date()][contract_base] += 1
                # Day-session bars avoid assigning the previous natural day's
                # night bar to the wrong trading date at a roll boundary.
                if time(8, 0) <= timestamp.time() < time(16, 0):
                    day_counts[timestamp.date()][contract_base] += 1
            contract_by_date: dict[date, str] = {}
            for trading_date in sorted(trading_dates):
                counts = day_counts.get(trading_date) or all_counts.get(trading_date)
                if counts:
                    contract_by_date[trading_date] = counts.most_common(1)[0][0]

            selected_contracts = sorted(set(contract_by_date.values()))
            if not selected_contracts:
                return {
                    'bars': [], 'series': [], 'truncated': False, 'limit': limit,
                    'selection_source': 'market.main.1min -> market.contract.daily',
                    'semantic_status': {'timezone': 'confirmed', 'timestamp_semantics': 'confirmed', 'trading_date': 'confirmed', 'session': 'not_applicable'},
                    'warnings': [{'code': 'main_contract_mapping_empty', 'message': 'No contract identity was found in the main 1min series for the requested dates.'}],
                }
            daily_series = self.series(product_id, 'single_contract', 'daily', selected_contracts)
            daily_by_contract = {_contract_base(str(row.get('contract_code') or '')): row for row in daily_series}
            bars_by_key: dict[tuple[date, str], dict[str, Any]] = {}
            for contract in selected_contracts:
                series_row = daily_by_contract.get(contract)
                if not series_row:
                    continue
                for row in self._read_locator(con, series_row, start, end, max(limit, 50000)):
                    timestamp = _row_datetime(row.get('timestamp'))
                    if timestamp is not None:
                        bars_by_key[(timestamp.date(), contract)] = row

            bars: list[dict[str, Any]] = []
            missing_mapping = []
            missing_daily = []
            for trading_date in sorted(trading_dates):
                contract = contract_by_date.get(trading_date)
                if not contract:
                    missing_mapping.append(trading_date.isoformat())
                    continue
                row = bars_by_key.get((trading_date, contract))
                if row is None:
                    missing_daily.append(f"{trading_date.isoformat()}:{contract}")
                    continue
                row['contract_code'] = contract
                row['source_symbol'] = contract
                row['trading_date'] = trading_date.isoformat()
                row['selection_source'] = 'market.main.1min'
                bars.append(row)
            bars.sort(key=lambda row: (row.get('timestamp') or '', row.get('contract_code') or ''))
            rolls = []
            previous = None
            for row in bars:
                current = row.get('contract_code')
                if current and previous and current != previous:
                    rolls.append({'timestamp': row.get('timestamp'), 'old_contract': previous, 'new_contract': current})
                if current:
                    previous = current
            warnings: list[dict[str, str]] = []
            if missing_mapping:
                warnings.append({'code': 'main_contract_mapping_missing', 'message': f"No main 1min contract for {len(missing_mapping)} trading dates."})
            if missing_daily:
                warnings.append({'code': 'selected_daily_missing', 'message': f"Selected contract daily bar missing for {len(missing_daily)} trading dates."})
            public_series = [{key: value for key, value in row.items() if key != 'storage_locator'} for row in daily_series]
            return {
                'bars': bars[:limit],
                'series': public_series,
                'rolls': rolls,
                'selection_source': 'market.main.1min -> market.contract.daily',
                'truncated': len(bars) > limit,
                'limit': limit,
                'semantic_status': {'timezone': 'confirmed', 'timestamp_semantics': 'confirmed', 'trading_date': 'confirmed', 'session': 'not_applicable'},
                'warnings': warnings,
            }
        finally:
            con.close()

    def intraday(self, product_id: str, trading_date: str, mode: str = 'main', contract: str | None = None, limit: int = 50000) -> dict[str, Any]:
        if mode not in {'main', 'single'}:
            raise QueryValidationError('intraday mode must be main or single')
        if limit < 1 or limit > 200000:
            raise QueryValidationError('limit must be between 1 and 200000')
        try:
            selected_date = date.fromisoformat(trading_date)
        except ValueError as exc:
            raise QueryValidationError(f'invalid trading_date: {trading_date}') from exc
        if mode == 'single' and not contract:
            raise QueryValidationError('single intraday mode requires contract')
        con = self.require_contract()
        try:
            if selected_date not in self._calendar_dates(con, selected_date, selected_date):
                raise QueryValidationError(f'trading_date is not an official trading date: {trading_date}')
            rules = self._session_rules_for(con, product_id, selected_date)
            if not rules:
                raise IndexContractError('session_rules_unavailable: trading_date cannot be mapped to natural timestamps')
            selected_contract = _contract_base(contract) if contract else None
            if selected_contract:
                self._require_active_contract(con, product_id, selected_contract, selected_date)
            series_kind = 'main_continuous' if mode == 'main' else 'single_contract'
            series_rows = self.series(product_id, series_kind, '1min', [selected_contract] if selected_contract else None)
            if selected_contract:
                series_rows = [row for row in series_rows if _contract_base(str(row.get('contract_code') or '')) == selected_contract]
            if not series_rows:
                raise IndexUnavailable(f'no {series_kind}/1min series for {product_id}')

            windows: list[tuple[datetime, datetime, str]] = []
            for rule in rules:
                try:
                    start_clock = time.fromisoformat(str(rule['start_time']))
                    end_clock = time.fromisoformat(str(rule['end_time']))
                    end_offset = int(rule.get('end_day_offset') or 0)
                except (KeyError, TypeError, ValueError) as exc:
                    raise IndexContractError(f'invalid session rule for {product_id}') from exc
                is_night = (
                    str(rule.get('session_id') or '').startswith('night')
                    or str(rule.get('trading_date_rule') or '') == 'night_as_next_trading_date'
                )
                session_start_date = selected_date - timedelta(days=1) if is_night else selected_date
                session_end_date = session_start_date + timedelta(days=end_offset)
                windows.append((
                    datetime.combine(session_start_date, start_clock),
                    datetime.combine(session_end_date, end_clock),
                    str(rule.get('session_id') or 'unknown'),
                ))
            windows.sort(key=lambda window: (window[0], window[1], window[2]))
            query_start = min(window[0] for window in windows)
            query_end = max(window[1] for window in windows)
            rows: list[dict[str, Any]] = []
            for series_row in series_rows:
                raw_rows = self._read_locator(con, series_row, query_start, query_end, max(limit, 50000))
                for row in raw_rows:
                    timestamp = _row_datetime(row.get('timestamp'))
                    if timestamp is None:
                        continue
                    matched = next((window for window in windows if window[0] <= timestamp < window[1]), None)
                    if not matched:
                        continue
                    row['trading_date'] = selected_date.isoformat()
                    row['session_id'] = matched[2]
                    rows.append(row)
            rows.sort(key=lambda row: (row.get('timestamp') or '', row.get('contract_code') or ''))
            warnings: list[dict[str, str]] = []
            if any(str(rule.get('confidence')) == 'review' for rule in rules):
                warnings.append({'code': 'session_rule_review', 'message': 'The selected product has a session rule marked review.'})
            public_series = [{key: value for key, value in row.items() if key != 'storage_locator'} for row in series_rows]
            return {
                'bars': rows[:limit],
                'series': public_series,
                'truncated': len(rows) > limit,
                'limit': limit,
                'trading_date': selected_date.isoformat(),
                'session_windows': [
                    {'session_id': session_id, 'start': start.isoformat(sep=' '), 'end': end.isoformat(sep=' ')}
                    for start, end, session_id in windows
                ],
                'semantic_status': {'timezone': 'confirmed', 'timestamp_semantics': 'confirmed', 'trading_date': 'confirmed', 'session': 'review' if warnings else 'confirmed'},
                'warnings': warnings,
            }
        finally:
            con.close()

    def _read_locator(self, con: duckdb.DuckDBPyConnection, series: dict[str, Any], start: datetime | None, end: datetime | None, limit: int) -> list[dict[str, Any]]:
        try:
            locator = json.loads(str(series['storage_locator']))
            paths = locator['paths']
            field_map = locator.get('field_map') or {}
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise IndexContractError(f"invalid storage_locator for {series.get('series_id')}") from exc
        if not isinstance(paths, list) or not paths or not all(isinstance(item, str) and item for item in paths):
            raise IndexContractError(f"storage_locator has no approved paths for {series.get('series_id')}")
        paths = self._resolve_locator_paths(paths, str(series.get('series_id') or 'unknown'))
        timestamp_field = field_map.get('timestamp')
        if not timestamp_field:
            raise IndexContractError(f"series has no timestamp field: {series.get('series_id')}")
        expressions = []
        for logical, alias in (
            ('timestamp', 'timestamp'), ('open', 'open'), ('high', 'high'), ('low', 'low'),
            ('close', 'close'), ('volume', 'volume'), ('amount', 'amount'), ('open_interest', 'open_interest'),
        ):
            source = field_map.get(logical)
            expressions.append(f"{_quote_identifier(source)} AS {alias}" if source else f"NULL AS {alias}")
        contract_field = field_map.get('contract_code')
        if contract_field:
            expressions.append(f"{_quote_identifier(contract_field)} AS contract_code")
        else:
            expressions.append("?::VARCHAR AS contract_code")
        where: list[str] = []
        params: list[Any] = []
        if not contract_field:
            # This placeholder appears in the SELECT list before the WHERE
            # and read_parquet placeholders, so its bound value comes first.
            params.append(series.get('contract_code'))
        params.append(paths)
        # The published contract-daily files currently store their date as
        # VARCHAR, while main-daily and all 1min files use DATE/TIMESTAMP.
        # Compare through a timestamp cast so the index contract accepts all
        # published representations without changing source files.
        timestamp_expr = f"try_cast({_quote_identifier(timestamp_field)} AS TIMESTAMP)"
        if start:
            where.append(f"{timestamp_expr} >= ?")
            params.append(start)
        if end:
            where.append(f"{timestamp_expr} <= ?")
            params.append(end)
        sql = f"select {', '.join(expressions)} from read_parquet(?, union_by_name=true)"
        # The path list is the first parameter; the constant contract is
        # inserted as the final SELECT parameter when there is no row field.
        if where:
            sql += " where " + " and ".join(where)
        sql += " order by " + timestamp_expr + " limit ?"
        params.append(limit + 1)
        rows = _records(con.execute(sql, params))
        for row in rows:
            raw = row.get('timestamp')
            if isinstance(raw, datetime):
                row['timestamp'] = raw.isoformat(sep=' ')
            elif raw is not None:
                row['timestamp'] = str(raw)
            row['raw_datetime'] = row.get('timestamp')
            row['source_symbol'] = row.get('contract_code')
            row['timezone'] = 'Asia/Shanghai'
            row['timestamp_semantics'] = 'bar_start'
            row['trading_date'] = row['timestamp'][:10] if series.get('frequency') == 'daily' and row.get('timestamp') else None
            row['session_id'] = None
            row['is_placeholder'] = bool(row.get('volume') == 0) if row.get('volume') is not None else False
            row['series_id'] = series.get('series_id')
            row['source_content_revision'] = series.get('content_revision')
        return rows

    def _resolve_locator_paths(self, paths: list[str], series_id: str) -> list[str]:
        """Resolve index-owned paths without allowing the index to escape its root."""
        approved_root = self.config.salt_data_root.resolve()
        resolved_paths: list[str] = []
        for raw_path in paths:
            candidate = Path(raw_path).expanduser()
            resolved = (candidate if candidate.is_absolute() else approved_root / candidate).resolve()
            try:
                resolved.relative_to(approved_root)
            except ValueError as exc:
                raise IndexContractError(f"storage_locator escapes SALT_DATA_ROOT for {series_id}: {raw_path}") from exc
            if not resolved.is_file():
                raise IndexUnavailable(f"published data file is missing for {series_id}: {raw_path}")
            resolved_paths.append(str(resolved))
        return resolved_paths

    def market(self, product_id: str, frequency: str, mode: str = 'main', start: str | None = None, end: str | None = None, contracts: Iterable[str] | None = None, contract: str | None = None, limit: int = 50000) -> dict[str, Any]:
        if frequency not in {'1min', 'daily'}:
            raise QueryValidationError("frequency must be 1min or daily")
        if mode not in {'main', 'single', 'overlay', 'splice'}:
            raise QueryValidationError("mode must be main, single, overlay, or splice")
        if mode == 'splice':
            raise QueryValidationError("splice is intentionally disabled in first version")
        if limit < 1 or limit > 200000:
            raise QueryValidationError("limit must be between 1 and 200000")
        start_dt, end_dt = _default_window(start, end, 90) if frequency == 'daily' else (_parse_iso(start), _parse_iso(end))
        if frequency == 'daily' and mode == 'main':
            return self._daily_main_from_1min(product_id, start_dt, end_dt, limit)
        if frequency == '1min' and (start_dt is None or end_dt is None):
            raise QueryValidationError("intraday queries require start and end")
        if frequency == '1min' and end_dt - start_dt > timedelta(days=2):
            raise QueryValidationError("intraday first-phase query is limited to two calendar days")
        kind = 'main_continuous' if mode == 'main' else 'single_contract'
        selected_contracts = [_contract_base(str(value)) for value in (contracts or []) if str(value).strip()]
        normalised_contract = _contract_base(contract) if contract else None
        if normalised_contract:
            selected_contracts.append(normalised_contract)
        series_rows = self.series(product_id, kind, frequency, selected_contracts if kind == 'single_contract' else None)
        if not series_rows:
            raise IndexUnavailable(f"no {kind}/{frequency} series for {product_id}")
        if kind == 'single_contract' and normalised_contract:
            series_rows = [row for row in series_rows if _contract_base(str(row.get('contract_code', ''))) == normalised_contract]
            if not series_rows:
                raise IndexUnavailable(f"contract not found: {normalised_contract}")
        if mode == 'single' and not normalised_contract and len(series_rows) != 1:
            raise QueryValidationError("single mode requires contract")
        if mode == 'overlay' and not selected_contracts:
            raise QueryValidationError("overlay mode requires contracts")
        con = self.require_contract()
        try:
            rows: list[dict[str, Any]] = []
            for series_row in series_rows:
                rows.extend(self._read_locator(con, series_row, start_dt, end_dt, limit))
            rows.sort(key=lambda row: (row.get('timestamp') or '', row.get('contract_code') or ''))
            truncated = len(rows) > limit
            public_series = [{key: value for key, value in series_row.items() if key != 'storage_locator'} for series_row in series_rows]
            return {
                'bars': rows[:limit],
                'series': public_series,
                'truncated': truncated,
                'limit': limit,
                'semantic_status': {
                    'timezone': 'confirmed', 'timestamp_semantics': 'confirmed',
                    'trading_date': 'confirmed' if frequency == 'daily' else 'unknown_without_session_rules',
                    'session': 'unknown_without_session_rules',
                },
                'warnings': [] if frequency == 'daily' else [{'code': 'session_rules_unavailable', 'message': '1min trading_date/session mapping is not published in the index; raw timestamp is returned without night-session inference.'}],
            }
        finally:
            con.close()
