from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sqlite3
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator

from .schemas import KNOWN_SCHEMAS, fingerprint, json_dumps, stable_hash
from .settings import Settings, settings


SCHEMA_VERSION = "catalog-v1"
MINUTE_RE = re.compile(r"^\d+min$")
HIGH_FREQUENCIES = {"日", "周", "月", "季度"}


@dataclass(frozen=True)
class ParsedPath:
    relative_path: str
    family: str | None
    frequency: str | None
    exchange_raw: str | None
    exchange: str | None
    product_raw: str | None
    product: str | None
    contract_raw: str | None
    contract: str | None
    asset_kind: str | None
    status: str
    warning_codes: tuple[str, ...]
    canonical_relative_path: str | None


def _canonical_token(value: str | None) -> str | None:
    return value.upper() if value is not None else None


def parse_market_path(relative_path: str) -> ParsedPath:
    path = PurePosixPath(relative_path)
    parts = path.parts
    name = path.name
    warnings: list[str] = []
    if any(part.startswith(".") for part in parts) or name == ".DS_Store":
        return ParsedPath(relative_path, None, None, None, None, None, None, None, None, None, "excluded", ("hidden_path",), None)
    if not name.lower().endswith(".csv"):
        return ParsedPath(relative_path, None, None, None, None, None, None, None, None, None, "excluded", ("not_csv",), None)

    if parts and parts[0] == "IM指数数据":
        if len(parts) != 2 or name not in {"SH.000852.csv", "SH.000852-daily.csv"}:
            return ParsedPath(relative_path, None, None, None, None, None, None, None, None, None, "unclassified", ("unknown_index_path",), None)
        frequency = "1min" if name == "SH.000852.csv" else "日"
        return ParsedPath(relative_path, "指数", frequency, "SSE", "SSE", "SH.000852", "SH.000852", "SH.000852", "SH.000852", "cash_index", "canonical", tuple(), relative_path)

    if len(parts) < 1 or parts[0] not in {"主要合约", "全部合约"}:
        return ParsedPath(relative_path, None, None, None, None, None, None, None, None, None, "unclassified", ("unknown_root",), None)
    family = parts[0]
    frequency = parts[1] if len(parts) > 1 else None
    if frequency is None or not (MINUTE_RE.match(frequency) or frequency in HIGH_FREQUENCIES):
        return ParsedPath(relative_path, family, frequency, None, None, None, None, None, None, None, "unclassified", ("unknown_frequency",), None)

    # The known nested IC copies are aliases of the direct all-contract files.
    nested_alias = family == "全部合约" and len(parts) == 6 and parts[4] == "1min"
    if nested_alias:
        warnings.append("suspected_alias")
        parts = (parts[0], parts[1], parts[2], parts[3], parts[5])

    if family == "主要合约" and MINUTE_RE.match(frequency) and len(parts) == 5:
        exchange, product, file_name = parts[2], parts[3], parts[4]
        if file_name == f"{product}.csv":
            return ParsedPath(relative_path, family, frequency, exchange, _canonical_token(exchange), product, _canonical_token(product), "continuous", "continuous", "continuous", "canonical", tuple(warnings), relative_path)
    if family == "主要合约" and frequency in HIGH_FREQUENCIES and len(parts) == 3:
        exchange, file_stem = parts[2].split(".", 1) if "." in parts[2] else ("", "")
        if exchange and file_stem:
            return ParsedPath(relative_path, family, frequency, exchange, _canonical_token(exchange), file_stem, _canonical_token(file_stem), "continuous", "continuous", "continuous", "canonical", tuple(warnings), relative_path)

    if family == "全部合约" and MINUTE_RE.match(frequency) and len(parts) == 5:
        exchange, product, file_name = parts[2], parts[3], parts[4]
        contract = file_name[:-4] if file_name.endswith(".csv") else ""
        if exchange and product and contract:
            canonical = str(PurePosixPath(family, frequency, exchange, product, file_name))
            status = "alias" if warnings else "canonical"
            return ParsedPath(relative_path, family, frequency, exchange, _canonical_token(exchange), product, _canonical_token(product), contract, _canonical_token(contract), "contract", status, tuple(warnings), canonical)
    if family == "全部合约" and frequency in HIGH_FREQUENCIES and len(parts) == 4:
        product, file_name = parts[2], parts[3]
        stem = file_name[:-4] if file_name.endswith(".csv") else ""
        if "." in stem and product:
            exchange, contract = stem.split(".", 1)
            canonical = relative_path
            return ParsedPath(relative_path, family, frequency, exchange, _canonical_token(exchange), product, _canonical_token(product), contract, _canonical_token(contract), "contract", "canonical", tuple(warnings), canonical)

    return ParsedPath(relative_path, family, frequency, None, None, None, None, None, None, None, "unclassified", ("unrecognized_path_shape",), None)


def _iter_csv_paths(root: Path) -> Iterator[tuple[str, Path]]:
    if not root.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(root):
        # Keep hidden directories in the file inventory so checkpoint copies
        # are explicitly auditable, while parse_market_path excludes them
        # from formal assets.
        dirnames[:] = sorted(dirnames)
        for filename in sorted(filenames):
            if not filename.lower().endswith(".csv"):
                continue
            path = Path(dirpath) / filename
            yield path.relative_to(root).as_posix(), path


def _read_header_and_bounds(path: Path) -> tuple[list[str], str | None, str | None, str | None]:
    # Metadata refresh must never turn a malformed file into an unbounded read.
    # A normal CSV header and first row fit comfortably in this window.
    window_size = 16 * 1024
    try:
        with path.open("rb") as handle:
            head = handle.read(window_size)
        if not head:
            return [], None, None, "empty_file"
        lines = head.splitlines()
        if len(lines) < 2:
            return [], None, None, "header_or_first_row_not_found_in_window"
        header_line = lines[0].decode("utf-8-sig", errors="replace")
        fields = next(csv.reader([header_line]))
        first_data = next((line.decode("utf-8", errors="replace") for line in lines[1:] if line.strip()), None)
        last_data = None
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            handle.seek(max(0, handle.tell() - window_size))
            tail = handle.read(window_size).decode("utf-8", errors="replace")
        for line in reversed(tail.splitlines()):
            if line.strip():
                last_data = line.strip()
                break
        def first_value(row: str | None) -> str | None:
            if not row:
                return None
            try:
                values = next(csv.reader([row]))
                index = fields.index("datetime")
                return values[index] if index < len(values) else None
            except (ValueError, csv.Error):
                return None
        return fields, first_value(first_data), first_value(last_data), None
    except (OSError, UnicodeError) as exc:
        return [], None, None, f"read_error:{type(exc).__name__}"


def _sample_dtype(path: Path, fields: list[str]) -> dict[str, str]:
    # A bounded sample is enough for Catalog semantics; values are never loaded as a table.
    result: dict[str, str] = {}
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            rows = csv.DictReader(handle, fieldnames=fields)
            next(rows, None)
            sample = next(rows, None)
        for field in fields:
            value = (sample or {}).get(field, "")
            if value is None or value == "":
                result[field] = "unknown"
            else:
                try:
                    float(value)
                    result[field] = "number"
                except ValueError:
                    result[field] = "string"
    except OSError:
        result = {field: "unknown" for field in fields}
    return result


def _create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        PRAGMA journal_mode=DELETE;
        CREATE TABLE catalog_meta (
          schema_version TEXT NOT NULL, catalog_revision TEXT NOT NULL,
          built_at TEXT NOT NULL, market_root_signature TEXT NOT NULL,
          scan_mode TEXT NOT NULL, file_count INTEGER NOT NULL,
          warning_count INTEGER NOT NULL
        );
        CREATE TABLE files (
          file_id TEXT PRIMARY KEY, relative_path TEXT UNIQUE NOT NULL,
          family TEXT, frequency TEXT, exchange_raw TEXT, exchange_canonical TEXT,
          product_raw TEXT, product_canonical TEXT, contract_raw TEXT,
          contract_canonical TEXT, asset_kind TEXT, size_bytes INTEGER NOT NULL,
          mtime_ns INTEGER NOT NULL, header_text TEXT, header_fingerprint TEXT,
          field_set_fingerprint TEXT, first_raw_datetime TEXT, last_raw_datetime TEXT,
          status TEXT NOT NULL, canonical_file_id TEXT, warning_json TEXT NOT NULL
        );
        CREATE TABLE assets (
          asset_id TEXT PRIMARY KEY, family TEXT, frequency TEXT, exchange TEXT,
          product TEXT, contract TEXT, asset_kind TEXT, canonical_file_id TEXT NOT NULL,
          schema_id TEXT, capability_json TEXT NOT NULL, semantic_status_json TEXT NOT NULL
        );
        CREATE TABLE schemas (
          schema_id TEXT PRIMARY KEY, ordered_fields_json TEXT NOT NULL,
          field_set_json TEXT NOT NULL, sample_dtype_json TEXT NOT NULL,
          source_count INTEGER NOT NULL, status TEXT NOT NULL
        );
        CREATE TABLE field_semantics (
          schema_id TEXT NOT NULL, raw_field TEXT NOT NULL, display_name TEXT NOT NULL,
          economic_identity TEXT NOT NULL, semantic_status TEXT NOT NULL,
          aggregation_note TEXT NOT NULL, missing_note TEXT NOT NULL, warning TEXT,
          PRIMARY KEY(schema_id, raw_field)
        );
        CREATE INDEX assets_filter ON assets(family, frequency, exchange, product, asset_kind);
        CREATE INDEX files_status ON files(status);
        """
    )


def _capabilities(fields: list[str], family: str | None, asset_kind: str | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for field in ("open", "high", "low", "close", "volume"):
        result[field] = "available" if field in fields else "unsupported"
    result["amount" if "amount" in fields else "money" if "money" in fields else "activity"] = "pending" if ("amount" in fields or "money" in fields) else "unsupported"
    result["position" if "position" in fields else "open_interest" if "open_interest" in fields else "open_interest"] = "pending" if "position" in fields else "available" if "open_interest" in fields else "unsupported"
    result["symbol"] = "available" if "symbol" in fields or asset_kind == "contract" else "path-derived"
    result.update({"timezone": "pending", "session": "pending", "trading_date": "pending", "timestamp_semantics": "pending", "level2": "unsupported", "research_outputs": "no_data"})
    return result


def _field_semantic(field: str) -> tuple[str, str, str, str, str | None]:
    known = {
        "datetime": ("Timestamp", "confirmed", "raw timestamp; no timezone/session inference", "missing values remain warnings", "timezone and bar boundary are pending"),
        "open": ("Bar open price", "confirmed", "price first within an existing bar", "missing values remain warnings", None),
        "high": ("Bar high price", "confirmed", "price max within an existing bar", "missing values remain warnings", None),
        "low": ("Bar low price", "confirmed", "price min within an existing bar", "missing values remain warnings", None),
        "close": ("Bar close price", "confirmed", "price last within an existing bar", "missing values remain warnings", None),
        "volume": ("Reported volume", "confirmed", "raw supplier field; not order-book depth", "missing values remain warnings", "does not identify orders or cancellations"),
        "amount": ("Reported amount", "pending", "aggregation is pending unit and interval semantics", "raw field retained", "unit and cumulative/flow meaning are pending"),
        "money": ("Reported money", "pending", "aggregation is pending unit and interval semantics", "raw field retained", "unit and cumulative/flow meaning are pending"),
        "position": ("Reported position", "pending", "raw state field; not renamed", "raw field retained", "equivalence to open interest is pending"),
        "open_interest": ("Reported open interest", "confirmed", "supplier field; not merged with position", "missing values remain warnings", None),
        "symbol": ("Contract symbol", "pending", "row identity when present", "path identity remains available", "main-contract selection/roll semantics are pending"),
    }
    return known.get(field, (field, "pending", "display only; no automatic aggregation", "raw field retained", "no semantic definition supplied"))


def _root_signature(root: Path, paths: list[tuple[str, Path]]) -> str:
    digest = hashlib.sha256()
    digest.update(str(root).encode("utf-8"))
    for relative, path in paths:
        try:
            stat = path.stat()
            digest.update(f"{relative}\0{stat.st_size}\0{stat.st_mtime_ns}".encode("utf-8"))
        except OSError:
            digest.update(f"{relative}\0missing".encode("utf-8"))
    return digest.hexdigest()


def _content_sample_key(parsed: ParsedPath) -> tuple[str | None, str | None, str | None]:
    """Choose a bounded representative set for the initial catalog.

    Full schema-drift verification is a resumable maintenance task. The
    initial build records every file from stat/path metadata and reads only
    one representative per family/frequency/kind, matching the evidence
    boundary in recipe.md.
    """
    return parsed.family, parsed.frequency, parsed.asset_kind


def refresh_catalog(config: Settings = settings) -> dict[str, Any]:
    root = config.market_root
    config.catalog_db.parent.mkdir(parents=True, exist_ok=True)
    paths = list(_iter_csv_paths(root))
    old: dict[str, tuple[Any, ...]] = {}
    if config.catalog_db.exists():
        try:
            with sqlite3.connect(config.catalog_db) as connection:
                for row in connection.execute("SELECT relative_path,size_bytes,mtime_ns,header_text,header_fingerprint,field_set_fingerprint,first_raw_datetime,last_raw_datetime,status,warning_json,family,frequency,exchange_raw,exchange_canonical,product_raw,product_canonical,contract_raw,contract_canonical,asset_kind,canonical_file_id,file_id FROM files"):
                    old[row[0]] = row[1:]
        except sqlite3.DatabaseError:
            old = {}

    fd, temp_name = tempfile.mkstemp(prefix="catalog.", suffix=".sqlite", dir=str(config.catalog_db.parent))
    os.close(fd)
    temp_path = Path(temp_name)
    warnings_count = 0
    schema_rows: dict[str, dict[str, Any]] = {}
    file_rows: list[dict[str, Any]] = []
    sampled_content_keys: set[tuple[str | None, str | None, str | None]] = set()
    try:
        with sqlite3.connect(temp_path) as connection:
            _create_schema(connection)
            for relative, path in paths:
                parsed = parse_market_path(relative)
                stat = path.stat()
                cached = old.get(relative)
                if cached and cached[0] == stat.st_size and cached[1] == stat.st_mtime_ns:
                    # Preserve metadata on unchanged files; reparse identity to catch parser upgrades.
                    header_text, header_fp, field_fp, first_raw, last_raw, status, warning_json = cached[2:9]
                    fields = json.loads(header_text) if header_text.startswith("[") else [v for v in header_text.split(",") if v]
                    read_error = None
                else:
                    sample_key = _content_sample_key(parsed)
                    should_sample = parsed.status not in {"excluded", "unclassified"} and bool(parsed.asset_kind) and sample_key not in sampled_content_keys
                    if should_sample:
                        sampled_content_keys.add(sample_key)
                    if not should_sample:
                        fields, first_raw, last_raw, read_error = [], None, None, None
                        header_text = "[]"
                        header_fp = None
                        field_fp = None
                        status = parsed.status if parsed.status in {"canonical", "alias"} else parsed.status
                        warning_codes = list(parsed.warning_codes)
                        if parsed.status not in {"excluded", "unclassified"}:
                            warning_codes.append("schema_deferred")
                        warning_json = json_dumps(sorted(set(warning_codes)))
                    else:
                        fields, first_raw, last_raw, read_error = _read_header_and_bounds(path)
                        header_text = json_dumps(fields)
                        header_fp = fingerprint(fields, ordered=True) if fields else None
                        field_fp = fingerprint(fields, ordered=False) if fields else None
                        status = parsed.status if not read_error else "unreadable"
                        warning_codes = list(parsed.warning_codes)
                        if read_error:
                            warning_codes.append(read_error)
                        warning_json = json_dumps(sorted(set(warning_codes)))
                if read_error:
                    status = "unreadable"
                if parsed.status == "unclassified" and status != "unreadable":
                    status = "unclassified"
                warning_list = json.loads(warning_json or "[]")
                warnings_count += len(warning_list) + (1 if status in {"unclassified", "unreadable"} else 0)
                file_id = stable_hash("file", relative)
                canonical_relative = parsed.canonical_relative_path or relative
                canonical_file_id = stable_hash("file", canonical_relative) if canonical_relative else None
                file_row = {
                    "file_id": file_id, "relative_path": relative, "family": parsed.family,
                    "frequency": parsed.frequency, "exchange_raw": parsed.exchange_raw,
                    "exchange_canonical": parsed.exchange, "product_raw": parsed.product_raw,
                    "product_canonical": parsed.product, "contract_raw": parsed.contract_raw,
                    "contract_canonical": parsed.contract, "asset_kind": parsed.asset_kind,
                    "size_bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns,
                    "header_text": header_text, "header_fingerprint": header_fp,
                    "field_set_fingerprint": field_fp, "first_raw_datetime": first_raw,
                    "last_raw_datetime": last_raw, "status": status,
                    "canonical_file_id": canonical_file_id, "warning_json": json_dumps(warning_list),
                }
                file_rows.append(file_row)
                if header_fp and parsed.status not in {"excluded", "unclassified"}:
                    entry = schema_rows.setdefault(header_fp, {"fields": fields, "dtypes": {}, "count": 0})
                    entry["count"] += 1
                    if not entry["dtypes"]:
                        entry["dtypes"] = _sample_dtype(path, fields)

            connection.executemany(
                "INSERT INTO files VALUES (:file_id,:relative_path,:family,:frequency,:exchange_raw,:exchange_canonical,:product_raw,:product_canonical,:contract_raw,:contract_canonical,:asset_kind,:size_bytes,:mtime_ns,:header_text,:header_fingerprint,:field_set_fingerprint,:first_raw_datetime,:last_raw_datetime,:status,:canonical_file_id,:warning_json)",
                file_rows,
            )
            for schema_id, info in schema_rows.items():
                connection.execute("INSERT INTO schemas VALUES (?,?,?,?,?,?)", (schema_id, json_dumps(info["fields"]), json_dumps(sorted(info["fields"])), json_dumps(info["dtypes"]), info["count"], "known" if schema_id in KNOWN_SCHEMAS else "unknown"))
                for field in info["fields"]:
                    display, semantic_status, aggregation, missing, warning = _field_semantic(field)
                    connection.execute("INSERT INTO field_semantics VALUES (?,?,?,?,?,?,?,?)", (schema_id, field, display, display if field not in {"amount", "money", "position", "open_interest"} else display, semantic_status, aggregation, missing, warning))

            # One asset per stable business identity; aliases point to the direct canonical file.
            assets: dict[str, dict[str, Any]] = {}
            for row in file_rows:
                if row["status"] not in {"canonical", "alias"} or not row["asset_kind"] or not row["canonical_file_id"]:
                    continue
                asset_id = stable_hash("asset", row["family"], row["frequency"], row["exchange_canonical"], row["product_canonical"], row["contract_canonical"], row["asset_kind"])
                assets.setdefault(asset_id, {"asset_id": asset_id, "family": row["family"], "frequency": row["frequency"], "exchange": row["exchange_canonical"], "product": row["product_canonical"], "contract": row["contract_canonical"], "asset_kind": row["asset_kind"], "canonical_file_id": row["canonical_file_id"], "schema_id": row["header_fingerprint"], "fields": json.loads(row["header_text"]) if row["header_text"] else []})
            for asset in assets.values():
                capability = _capabilities(asset["fields"], asset["family"], asset["asset_kind"])
                semantic = {"status": "pending", "warnings": ["timezone", "session", "trading_date", "timestamp_semantics"]}
                connection.execute("INSERT INTO assets VALUES (?,?,?,?,?,?,?,?,?,?,?)", (asset["asset_id"], asset["family"], asset["frequency"], asset["exchange"], asset["product"], asset["contract"], asset["asset_kind"], asset["canonical_file_id"], asset["schema_id"], json_dumps(capability), json_dumps(semantic)))
            revision = stable_hash("revision", _root_signature(root, paths), datetime.now(timezone.utc).isoformat(), length=32)
            connection.execute("INSERT INTO catalog_meta VALUES (?,?,?,?,?,?,?)", (SCHEMA_VERSION, revision, datetime.now(timezone.utc).isoformat(), _root_signature(root, paths), "metadata", len(file_rows), warnings_count))
            connection.commit()
        os.replace(temp_path, config.catalog_db)
    finally:
        if temp_path.exists():
            temp_path.unlink()
    return {"catalog_revision": revision, "file_count": len(file_rows), "asset_count": len(assets), "schema_count": len(schema_rows), "warning_count": warnings_count}


def connect_catalog(config: Settings = settings) -> sqlite3.Connection:
    if not config.catalog_db.exists():
        raise FileNotFoundError(str(config.catalog_db))
    connection = sqlite3.connect(config.catalog_db)
    connection.row_factory = sqlite3.Row
    return connection


def catalog_meta(config: Settings = settings) -> dict[str, Any] | None:
    try:
        with connect_catalog(config) as connection:
            row = connection.execute("SELECT * FROM catalog_meta LIMIT 1").fetchone()
            return dict(row) if row else None
    except (FileNotFoundError, sqlite3.DatabaseError):
        return None


def row_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


def list_assets(config: Settings = settings, filters: dict[str, str | None] | None = None, page_size: int = 50, cursor: str | None = None) -> tuple[list[dict[str, Any]], str | None]:
    filters = filters or {}
    try:
        with connect_catalog(config) as connection:
            where, values = [], []
            for key in ("family", "frequency", "exchange", "product", "asset_kind"):
                if filters.get(key):
                    where.append(f"{key} = ?")
                    values.append(filters[key])
            if filters.get("status") == "alias":
                where.append("0 = 1")  # aliases are file anomalies, never duplicate assets
            if filters.get("search"):
                term = f"%{filters['search']}%"
                where.append("(product LIKE ? OR contract LIKE ? OR exchange LIKE ?)")
                values.extend([term, term, term])
            if cursor:
                where.append("asset_id > ?")
                values.append(cursor)
            sql = "SELECT * FROM assets" + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY asset_id LIMIT ?"
            values.append(min(max(page_size, 1), 200) + 1)
            rows = [dict(row) for row in connection.execute(sql, values).fetchall()]
            next_cursor = rows[-1]["asset_id"] if len(rows) > page_size else None
            return rows[:page_size], next_cursor
    except (FileNotFoundError, sqlite3.DatabaseError):
        return [], None


def catalog_options(config: Settings = settings, filters: dict[str, str | None] | None = None) -> dict[str, list[str]]:
    filters = filters or {}
    options = {key: [] for key in ("family", "frequency", "exchange", "product", "asset_kind")}
    try:
        with connect_catalog(config) as connection:
            where, values = [], []
            for key in options:
                if filters.get(key):
                    where.append(f"{key} = ?")
                    values.append(filters[key])
            predicate = " WHERE " + " AND ".join(where) if where else ""
            for key in options:
                rows = connection.execute(f"SELECT DISTINCT {key} FROM assets{predicate} ORDER BY {key}", values).fetchall()
                options[key] = [row[0] for row in rows if row[0] is not None]
    except (FileNotFoundError, sqlite3.DatabaseError):
        pass
    return options


def get_asset(config: Settings, asset_id: str) -> dict[str, Any] | None:
    try:
        with connect_catalog(config) as connection:
            asset = row_dict(connection.execute("SELECT * FROM assets WHERE asset_id = ?", (asset_id,)).fetchone())
            if not asset:
                return None
            asset["capability"] = json.loads(asset.pop("capability_json"))
            asset["semantic_status"] = json.loads(asset.pop("semantic_status_json"))
            asset["file"] = row_dict(connection.execute("SELECT relative_path,size_bytes,mtime_ns,header_text,header_fingerprint,field_set_fingerprint,first_raw_datetime,last_raw_datetime,status,warning_json FROM files WHERE file_id = ?", (asset["canonical_file_id"],)).fetchone())
            if asset["file"]:
                asset["file"]["fields"] = json.loads(asset["file"].pop("header_text") or "[]")
                asset["file"]["warnings"] = json.loads(asset["file"].pop("warning_json") or "[]")
            return asset
    except (FileNotFoundError, sqlite3.DatabaseError):
        return None


def list_schemas(config: Settings = settings) -> list[dict[str, Any]]:
    try:
        with connect_catalog(config) as connection:
            rows = []
            for row in connection.execute("SELECT * FROM schemas ORDER BY schema_id"):
                item = dict(row)
                item["ordered_fields"] = json.loads(item.pop("ordered_fields_json"))
                item["field_set"] = json.loads(item.pop("field_set_json"))
                item["sample_dtype"] = json.loads(item.pop("sample_dtype_json"))
                item["label"] = KNOWN_SCHEMAS.get(item["schema_id"], "unknown")
                rows.append(item)
            return rows
    except (FileNotFoundError, sqlite3.DatabaseError):
        return []


def get_schema(config: Settings, schema_id: str) -> dict[str, Any] | None:
    for item in list_schemas(config):
        if item["schema_id"] == schema_id:
            try:
                with connect_catalog(config) as connection:
                    fields = [dict(row) for row in connection.execute("SELECT * FROM field_semantics WHERE schema_id = ? ORDER BY rowid", (schema_id,))]
                item["fields"] = fields
            except (FileNotFoundError, sqlite3.DatabaseError):
                item["fields"] = []
            return item
    return None


def anomalies(config: Settings = settings) -> list[dict[str, Any]]:
    try:
        with connect_catalog(config) as connection:
            rows = []
            for row in connection.execute("SELECT relative_path,status,canonical_file_id,warning_json FROM files WHERE status IN ('alias','unclassified','unreadable') OR warning_json != '[]' ORDER BY relative_path"):
                item = dict(row)
                item["warnings"] = json.loads(item.pop("warning_json") or "[]")
                rows.append(item)
            return rows
    except (FileNotFoundError, sqlite3.DatabaseError):
        return []


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if argv[:1] == ["refresh"]:
        print(json.dumps(refresh_catalog(), ensure_ascii=False, indent=2))
        return 0
    print("usage: python -m recipe.catalog refresh", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
