from __future__ import annotations

import csv
import math
import re
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional

from ..catalog import connect_catalog, get_asset
from ..settings import Settings, settings


class MarketError(Exception):
    code = "market_error"


class AssetNotFound(MarketError):
    code = "asset_not_found"


class RangeTooLarge(MarketError):
    code = "range_too_large"


class UnsupportedField(MarketError):
    code = "unsupported_field"


class InvalidQuery(MarketError):
    code = "invalid_query"


_DATE_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d", "%Y/%m/%d %H:%M:%S")
_SAFE_FIELDS = {"datetime", "open", "high", "low", "close", "volume", "amount", "money", "position", "open_interest", "symbol"}


def parse_timestamp(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def _json_number(value: Any, warnings: list[dict[str, Any]], field: str, row_number: int) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and not math.isfinite(value):
        warnings.append({"code": "non_finite_value", "field": field, "row": row_number})
        return None
    return value


def _read_header(path: Path) -> list[str]:
    with path.open("rb") as handle:
        data = handle.read(64 * 1024)
    if not data:
        return []
    line = data.splitlines()[0].decode("utf-8-sig", errors="replace")
    return next(csv.reader([line]))


def _iso(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat(sep=" ") if value else None


def _raw_value(row: dict[str, Any], field: str) -> Any:
    value = row.get(field)
    if value is None:
        return None
    try:
        if isinstance(value, str) and value.strip().lower() in {"nan", "+nan", "-nan", "inf", "+inf", "-inf", "infinity", "+infinity", "-infinity"}:
            return float(value)
        return float(value) if isinstance(value, str) and ("." in value or "e" in value.lower()) else int(value) if isinstance(value, str) and re.match(r"^-?\d+$", value) else value
    except (TypeError, ValueError):
        return value


class MarketCSVAdapter:
    schema_version = "market-adapter-v1"

    def __init__(self, config: Settings = settings):
        self.config = config

    def _asset_and_path(self, asset_id: str) -> tuple[dict[str, Any], Path, list[str], dict[str, Any]]:
        asset = get_asset(self.config, asset_id)
        if not asset or not asset.get("file"):
            raise AssetNotFound(asset_id)
        file_meta = asset["file"]
        path = self.config.market_root / file_meta["relative_path"]
        if not path.is_file():
            raise AssetNotFound(asset_id)
        fields = file_meta.get("fields") or _read_header(path)
        if not fields:
            raise InvalidQuery("CSV header is unavailable")
        return asset, path, fields, file_meta

    def _scan(self, path: Path, fields: list[str]) -> list[dict[str, Any]]:
        # The preferred deployment can replace this bounded reader with
        # Polars scan_csv. This stdlib path is used here because the local
        # Python 3.9/Rosetta runtime cannot execute the installed Polars
        # wheel; it still opens only the selected canonical file and projects
        # only requested fields.
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle)
            return [{field: row.get(field) for field in fields} for row in reader]

    def bars(self, asset_id: str, start: Optional[str], end: Optional[str], fields: Optional[Iterable[str]], limit: int) -> dict[str, Any]:
        if limit < 1 or limit > 5000:
            raise InvalidQuery("limit must be between 1 and 5000")
        if not start and not end:
            raise InvalidQuery("start and end are required for bars")
        start_dt = parse_timestamp(start) if start else None
        end_dt = parse_timestamp(end) if end else None
        if (start and not start_dt) or (end and not end_dt) or (start_dt and end_dt and start_dt > end_dt):
            raise InvalidQuery("invalid datetime range")
        asset, path, available, file_meta = self._asset_and_path(asset_id)
        requested = [f.strip() for f in (fields or available) if f and f.strip()]
        requested = list(dict.fromkeys(requested))
        unsupported = [field for field in requested if field not in _SAFE_FIELDS or field not in available]
        if unsupported:
            raise UnsupportedField(",".join(unsupported))
        activity_field = "amount" if "amount" in available else "money" if "money" in available else None
        position_field = "position" if "position" in available else "open_interest" if "open_interest" in available else None
        scan_fields = list(dict.fromkeys(["datetime"] + requested + (["symbol"] if "symbol" in available else []) + ([activity_field] if activity_field else []) + ([position_field] if position_field else [])))
        rows = self._scan(path, scan_fields)
        warnings: list[dict[str, Any]] = [
            {"code": "timezone_pending", "message": "Timezone is not configured; timestamp has no offset."},
            {"code": "timestamp_semantics_pending", "message": "Bar timestamp start/end semantics are pending."},
            {"code": "trading_date_pending", "message": "Natural date is not inferred as trading_date."},
            {"code": "session_pending", "message": "Session labels are not configured."},
        ]
        normalized: list[dict[str, Any]] = []
        previous_ts: Optional[datetime] = None
        symbols: list[str] = []
        for index, raw in enumerate(rows):
            raw_datetime = raw.get("datetime")
            timestamp = parse_timestamp(raw_datetime)
            if timestamp is None:
                warnings.append({"code": "timestamp_parse_error", "row": index, "raw_datetime": raw_datetime})
                continue
            if start_dt and timestamp < start_dt or end_dt and timestamp > end_dt:
                continue
            if previous_ts and timestamp < previous_ts:
                warnings.append({"code": "timestamp_non_monotonic", "row": index})
            previous_ts = timestamp
            if raw.get("symbol") is not None:
                symbols.append(str(raw["symbol"]))
            item: dict[str, Any] = {
                "asset_id": asset["asset_id"],
                "source_file_id": asset["canonical_file_id"],
                "family": asset["family"], "asset_kind": asset["asset_kind"],
                "frequency": asset["frequency"], "exchange": asset["exchange"],
                "product": asset["product"], "contract": asset["contract"],
                "source_symbol": str(raw["symbol"]) if raw.get("symbol") is not None else asset["contract"],
                "symbol_source": "row" if "symbol" in available else "path",
                "raw_datetime": str(raw_datetime) if raw_datetime is not None else None,
                "timestamp": _iso(timestamp), "timezone": None,
                "timestamp_semantics": "pending", "trading_date": None, "session_id": None,
            }
            for field in requested:
                if field in raw:
                    item[field] = _json_number(_raw_value(raw, field), warnings, field, index)
            item["activity_value"] = _json_number(_raw_value(raw, activity_field), warnings, activity_field, index) if activity_field else None
            item["activity_raw_field"] = activity_field
            item["position_value"] = _json_number(_raw_value(raw, position_field), warnings, position_field, index) if position_field else None
            item["position_raw_field"] = position_field
            item["semantic_status"] = {"activity": "pending" if activity_field else "unsupported", "position": "pending" if position_field == "position" else "available" if position_field else "unsupported"}
            normalized.append(item)
        if len(normalized) > limit:
            raise RangeTooLarge(f"query returned {len(normalized)} bars; limit is {limit}")
        if len(set(symbols)) > 1:
            warnings.append({"code": "symbol_switch_observed", "symbols": list(dict.fromkeys(symbols))})
        for item in normalized:
            o, h, low, c = item.get("open"), item.get("high"), item.get("low"), item.get("close")
            if all(isinstance(v, (int, float)) for v in (o, h, low, c)) and not (low <= o <= h and low <= c <= h):
                warnings.append({"code": "ohlc_relation_warning", "timestamp": item["timestamp"]})
        return {
            "bars": normalized, "field_map": {field: {"raw_field": field, "status": "available"} for field in requested},
            "source_identity": {"asset_id": asset["asset_id"], "source_file_id": asset["canonical_file_id"], "relative_path": file_meta["relative_path"]},
            "semantic_status": {"timezone": "pending", "timestamp_semantics": "pending", "trading_date": "pending", "session": "pending"},
            "warnings": _dedupe_warnings(warnings), "truncated": False, "limit": limit,
        }

    def context(self, asset_id: str, timestamp: str, before: int, after: int) -> dict[str, Any]:
        if before < 0 or after < 0 or before > 100 or after > 100:
            raise InvalidQuery("before/after must be between 0 and 100")
        asset, path, available, _ = self._asset_and_path(asset_id)
        parsed = parse_timestamp(timestamp)
        if not parsed:
            raise InvalidQuery("invalid timestamp")
        rows = self._scan(path, list(dict.fromkeys(["datetime"] + available)))
        parsed_rows = [(i, parse_timestamp(row.get("datetime")), row) for i, row in enumerate(rows)]
        selected = min((entry for entry in parsed_rows if entry[1] is not None), key=lambda entry: abs((entry[1] - parsed).total_seconds()), default=None)
        if selected is None:
            return {"bars": [], "selected_index": None, "warnings": [{"code": "no_data"}]}
        start_index = max(0, selected[0] - before)
        end_index = min(len(rows), selected[0] + after + 1)
        start = _iso(parsed_rows[start_index][1]) if parsed_rows[start_index][1] else timestamp
        end = _iso(parsed_rows[end_index - 1][1]) if parsed_rows[end_index - 1][1] else timestamp
        result = self.bars(asset_id, start, end, available, before + after + 1)
        result["selected_timestamp"] = _iso(selected[1])
        result["selected_index"] = selected[0] - start_index
        return result


def _dedupe_warnings(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        key = repr(sorted(item.items()))
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


class ResponseCache:
    def __init__(self, max_entries: int = 64):
        self.max_entries = max_entries
        self._data: OrderedDict[str, dict[str, Any]] = OrderedDict()

    def get(self, key: str) -> Optional[dict[str, Any]]:
        value = self._data.get(key)
        if value is not None:
            self._data.move_to_end(key)
        return value

    def put(self, key: str, value: dict[str, Any]) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        while len(self._data) > self.max_entries:
            self._data.popitem(last=False)

    def clear(self) -> None:
        self._data.clear()


query_cache = ResponseCache()
