"""Read-only catalog and manifest views over the published salt-data store."""

from __future__ import annotations

import hashlib
import json
import re
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from saltcore.read import data_root

router = APIRouter(prefix="/api/database", tags=["database"])

DOMAIN_DEFINITIONS = [
    {
        "id": "market",
        "name": "行情数据",
        "name_en": "Market Data",
        "raw": ("market",),
        "derived": (),
        "derived_marker": "0.行情数据",
        "availability": (
            "market.main.1min",
            "market.main.daily",
            "market.contract.1min",
            "market.contract.daily",
        ),
    },
    {
        "id": "contract-reference",
        "name": "合约信息",
        "name_en": "Contract Reference",
        "raw": ("contract_info",),
        "derived": ("contract_info",),
        "availability": (),
    },
    {
        "id": "product-configuration",
        "name": "品种配置",
        "name_en": "Product Configuration",
        "raw": (),
        "derived": ("product_config",),
        "availability": (),
    },
    {
        "id": "warehouse-receipts",
        "name": "仓单库存",
        "name_en": "Warehouse Receipts",
        "raw": ("1",),
        "derived": (),
        "derived_marker": "1.仓库货单",
        "availability": ("warehouse_receipts",),
    },
    {
        "id": "position-rankings",
        "name": "持仓排名",
        "name_en": "Position Rankings",
        "raw": ("2",),
        "derived": (),
        "derived_marker": "2.每日持仓排名",
        "availability": ("daily_positions",),
    },
    {
        "id": "spot-prices",
        "name": "现货价格",
        "name_en": "Spot Prices",
        "raw": ("3",),
        "derived": (),
        "derived_marker": "3.现货",
        "availability": ("spot_daily",),
    },
    {
        "id": "price-limits",
        "name": "涨跌停价格",
        "name_en": "Price Limits",
        "raw": ("4",),
        "derived": (),
        "derived_marker": "4.涨跌停",
        "availability": ("price_limits",),
    },
    {
        "id": "main-contract-map",
        "name": "主力合约映射",
        "name_en": "Main-contract Mapping",
        "raw": ("5",),
        "derived": (),
        "derived_marker": "5.主力合约时间表",
        "availability": ("main_contract_map",),
    },
    {
        "id": "settlement-parameters",
        "name": "结算参数",
        "name_en": "Settlement Parameters",
        "raw": ("6",),
        "derived": (),
        "derived_marker": "6.每日结算",
        "availability": ("daily_settlement",),
    },
]
DOMAIN_BY_ID = {item["id"]: item for item in DOMAIN_DEFINITIONS}
MANIFEST_FILES = {
    "raw": "元数据/manifest/current_raw.parquet",
    "derived": "元数据/manifest/current_derived.parquet",
}
HASH_PATTERN = re.compile(r"^[a-fA-F0-9]{64}$")
HASH_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="recipe-db-hash")
LOCK = threading.Lock()
OBSERVATIONS: dict[str, dict[str, Any]] = {}
TASKS: dict[str, dict[str, Any]] = {}
ACTIVE_TASK: str | None = None
CACHE_PATH = Path(__file__).resolve().parents[2] / ".cache" / "database" / "observations.json"


def _load_observations() -> None:
    try:
        values = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(values, list):
        return
    for value in values[-5_000:]:
        if (
            isinstance(value, dict)
            and isinstance(value.get("relative_path"), str)
            and isinstance(value.get("expected_sha256"), str)
            and value.get("kind") in MANIFEST_FILES
            and value.get("status")
            in {"verified", "mismatch", "missing", "unreadable", "updating"}
        ):
            OBSERVATIONS[value["relative_path"]] = value


def _save_observations() -> None:
    with LOCK:
        values = list(OBSERVATIONS.values())[-5_000:]
    safe_values = [
        {
            key: value[key]
            for key in (
                "relative_path",
                "expected_sha256",
                "observed_sha256",
                "kind",
                "dataset",
                "status",
                "stable",
                "matches",
                "expected_size_bytes",
                "observed_size_bytes",
                "size_matches",
                "mtime_matches",
                "checked_at",
                "message",
            )
            if key in value
        }
        for value in values
    ]
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary = CACHE_PATH.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(safe_values, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        temporary.replace(CACHE_PATH)
    except OSError:
        # Local cache failure does not affect the read-only view or hash result.
        return


_load_observations()


def _root() -> Path:
    return Path(data_root()).resolve()


def _manifest_path(kind: str) -> Path:
    return _root() / MANIFEST_FILES[kind]


def _catalog_path() -> Path:
    return _root() / "元数据" / "catalog.duckdb"


def _connect() -> duckdb.DuckDBPyConnection:
    path = _catalog_path()
    if not path.is_file():
        raise RuntimeError("salt-data Catalog is unavailable")
    return duckdb.connect(str(path), read_only=True)


def market_products() -> list[dict[str, str]]:
    """Products with published market bars, sourced from the salt-data Catalog."""
    db = _connect()
    try:
        rows = db.execute(
            """SELECT exchange_id, product_id, product_code, product_name
               FROM v_products WHERE has_market ORDER BY exchange_id, product_code"""
        ).fetchall()
        return [
            {"exchange": row[0], "product_id": row[1], "code": row[2], "name": row[3]}
            for row in rows
        ]
    finally:
        db.close()


def _domain_for(kind: str, dataset: str, relative_path: str = "") -> str | None:
    for domain in DOMAIN_DEFINITIONS:
        datasets = domain["raw"] if kind == "raw" else domain["derived"]
        if dataset in datasets:
            return domain["id"]
        marker = domain.get("derived_marker")
        if kind == "derived" and dataset == "derived" and marker in relative_path:
            return domain["id"]
    return None


def _domain_case(kind: str) -> str:
    cases: list[str] = []
    for domain in DOMAIN_DEFINITIONS:
        datasets = domain["raw"] if kind == "raw" else domain["derived"]
        if datasets:
            quoted = ",".join("'" + value.replace("'", "''") + "'" for value in datasets)
            cases.append(f"WHEN dataset IN ({quoted}) THEN '{domain['id']}'")
        marker = domain.get("derived_marker")
        if kind == "derived" and marker:
            escaped = marker.replace("'", "''")
            cases.append(
                f"WHEN dataset = 'derived' AND contains(relative_path, '{escaped}') THEN '{domain['id']}'"
            )
    return "CASE " + " ".join(cases) + " ELSE NULL END"


def _manifest_stats() -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = {}
    for kind, relative in MANIFEST_FILES.items():
        path = _root() / relative
        info = path.stat()
        stats[kind] = {
            "path": relative,
            "size_bytes": info.st_size,
            "mtime_ns": info.st_mtime_ns,
        }
    return stats


def _read_revision(db: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    rows = db.execute(
        "SELECT catalog_revision, built_at, schema_version FROM v_catalog_revision LIMIT 1"
    ).fetchone()
    if not rows:
        return {"revision": None, "built_at": None, "schema_version": None}
    return {"revision": rows[0], "built_at": rows[1], "schema_version": rows[2]}


def _observed_counts() -> tuple[dict[str, int], dict[str, int]]:
    verified = {domain["id"]: 0 for domain in DOMAIN_DEFINITIONS}
    review = {domain["id"]: 0 for domain in DOMAIN_DEFINITIONS}
    with LOCK:
        values = list(OBSERVATIONS.values())
    current_hashes: dict[tuple[str, str], str | None] = {}
    db = duckdb.connect(":memory:")
    try:
        for kind in MANIFEST_FILES:
            relevant = [item for item in values if item["kind"] == kind]
            if not relevant:
                continue
            paths = list({item["relative_path"] for item in relevant})
            placeholders = ",".join("?" for _ in paths)
            rows = db.execute(
                f"""SELECT relative_path, sha256 FROM read_parquet(?)
                    WHERE relative_path IN ({placeholders})""",
                [str(_manifest_path(kind)), *paths],
            ).fetchall()
            current_hashes.update({(kind, row[0]): row[1] for row in rows})
    except (OSError, duckdb.Error):
        return verified, review
    finally:
        db.close()
    for observation in values:
        kind = observation["kind"]
        key = (kind, observation["relative_path"])
        if current_hashes.get(key) != observation.get("expected_sha256"):
            continue
        domain_id = _domain_for(kind, observation["dataset"], observation["relative_path"])
        if not domain_id:
            continue
        if observation.get("status") == "verified":
            verified[domain_id] += 1
        elif observation.get("status") in {"mismatch", "missing", "unreadable", "updating"}:
            review[domain_id] += 1
    return verified, review


def _cached_observation(relative_path: str, expected_sha256: str | None) -> dict[str, Any] | None:
    if not expected_sha256:
        return None
    with LOCK:
        observation = OBSERVATIONS.get(relative_path)
        if not observation or observation.get("expected_sha256") != expected_sha256:
            return None
        return {
            key: observation[key]
            for key in (
                "status",
                "observed_sha256",
                "checked_at",
                "stable",
                "matches",
                "message",
            )
            if key in observation
        }


def _recent_batches(root: Path, maximum: int = 8) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in (root / "元数据" / "runs").glob("**/batch.json"):
        try:
            batch = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        entries = batch.get("items") or []
        actions: dict[str, int] = {}
        for entry in entries:
            action = str(entry.get("action") or "UNKNOWN").upper()
            actions[action] = actions.get(action, 0) + 1
        items.append(
            {
                "run_id": batch.get("run_id") or path.parent.name,
                "created_at": batch.get("created_at"),
                "completed_at": batch.get("completed_at"),
                "status": str(batch.get("status") or "UNKNOWN").upper(),
                "item_count": len(entries),
                "actions": actions,
                "provider": batch.get("provider"),
                "path": str(path.relative_to(root)).replace("\\", "/"),
            }
        )
    items.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
    return items[:maximum]


@router.get("/overview")
def overview() -> dict[str, Any]:
    root = _root()
    db = _connect()
    try:
        revision = _read_revision(db)
        products = db.execute(
            """SELECT exchange_id, exchange_code, exchange_name, product_id,
                      product_code, product_name, status, has_market
               FROM v_products ORDER BY exchange_id, product_code"""
        ).fetchall()
        availability = db.execute(
            """SELECT dataset_key, product_id, status, row_count, series_count,
                      min_time, max_time, content_revision, schema_version
               FROM v_dataset_availability ORDER BY product_id, dataset_key"""
        ).fetchall()
        quality_events = db.execute("SELECT count(*) FROM v_quality_events").fetchone()[0]
        quality_runs = db.execute(
            "SELECT count(*) FROM v_quality_product_summary"
        ).fetchone()[0]
        series_count = db.execute("SELECT count(*) FROM v_market_series").fetchone()[0]
        domain_summaries: dict[str, dict[str, int]] = {
            domain["id"]: {"files": 0, "bytes": 0, "hashes": 0}
            for domain in DOMAIN_DEFINITIONS
        }
        registered_files = registered_bytes = hash_registered = 0
        for kind, relative in MANIFEST_FILES.items():
            manifest = root / relative
            stats = db.execute(
                f"""SELECT {_domain_case(kind)} AS domain, count(*), coalesce(sum(size_bytes), 0),
                          count(*) FILTER (WHERE regexp_matches(sha256, '^[a-fA-F0-9]{{64}}$'))
                   FROM read_parquet(?) GROUP BY domain""",
                [str(manifest)],
            ).fetchall()
            for domain_id, count, size_bytes, hash_count in stats:
                registered_files += int(count)
                registered_bytes += int(size_bytes or 0)
                hash_registered += int(hash_count or 0)
                if domain_id:
                    summary = domain_summaries[domain_id]
                    summary["files"] += int(count)
                    summary["bytes"] += int(size_bytes or 0)
                    summary["hashes"] += int(hash_count or 0)
        raw_latest = db.execute(
            "SELECT max(scanned_at) FROM read_parquet(?)", [str(_manifest_path("raw"))]
        ).fetchone()[0]
        derived_latest = db.execute(
            "SELECT max(scanned_at) FROM read_parquet(?)",
            [str(_manifest_path("derived"))],
        ).fetchone()[0]
        product_rows = [
            {
                "exchange_id": row[0],
                "exchange_code": row[1],
                "exchange_name": row[2],
                "product_id": row[3],
                "product_code": row[4],
                "product_name": row[5],
                "status": row[6],
                "has_market": bool(row[7]),
            }
            for row in products
        ]
        availability_rows = [
            {
                "dataset_key": row[0],
                "product_id": row[1],
                "status": row[2],
                "row_count": int(row[3] or 0),
                "series_count": int(row[4] or 0),
                "min_time": row[5],
                "max_time": row[6],
                "content_revision": row[7],
                "schema_version": row[8],
            }
            for row in availability
        ]
        observed, review = _observed_counts()
        domains = []
        for definition in DOMAIN_DEFINITIONS:
            keys = definition["availability"]
            rows = [row for row in availability_rows if row["dataset_key"] in keys]
            covered = len({row["product_id"] for row in rows if row["status"] == "available"})
            total_pairs = len(rows)
            summary = domain_summaries[definition["id"]]
            domains.append(
                {
                    "id": definition["id"],
                    "name": definition["name"],
                    "name_en": definition["name_en"],
                    "file_count": summary["files"],
                    "size_bytes": summary["bytes"],
                    "hash_registered": summary["hashes"],
                    "hash_total": summary["files"],
                    "verified_files": observed[definition["id"]],
                    "review_files": review[definition["id"]],
                    "coverage_products": covered if keys else None,
                    "coverage_total": len(product_rows) if keys else None,
                    "available_pairs": sum(row["status"] == "available" for row in rows),
                    "total_pairs": total_pairs,
                    "series_count": series_count if definition["id"] == "market" else None,
                    "integrity": "unverified",
                }
            )
        observed_total = sum(observed.values())
        review_total = sum(review.values())
        manifest_stats = _manifest_stats()
        return {
            "source": "salt-data",
            "catalog": revision,
            "manifests": {
                "raw": {**manifest_stats["raw"], "latest_scanned_at": raw_latest},
                "derived": {
                    **manifest_stats["derived"],
                    "latest_scanned_at": derived_latest,
                },
            },
            "metrics": {
                "registered_files": registered_files,
                "registered_bytes": registered_bytes,
                "hash_registered": hash_registered,
                "hash_total": registered_files,
                "verified_files": observed_total,
                "unverified_files": max(0, registered_files - observed_total - review_total),
                "review_files": review_total,
                "product_count": len(product_rows),
                "market_series": int(series_count),
            },
            "domains": domains,
            "products": product_rows,
            "availability": availability_rows,
            "quality": {
                "assessed": bool(quality_events or quality_runs),
                "events": int(quality_events),
                "product_summaries": int(quality_runs),
                "status": "indexed" if quality_events or quality_runs else "not_assessed",
            },
            "recent_batches": _recent_batches(root),
            "read_only": True,
        }
    except Exception as exc:
        raise HTTPException(503, f"Could not read salt-data catalog: {exc}") from exc
    finally:
        db.close()


def _domain_predicate(domain_id: str, kind: str) -> tuple[str, list[str]]:
    definition = DOMAIN_BY_ID.get(domain_id)
    if definition is None:
        raise HTTPException(422, "Unknown database domain")
    dataset_ids = definition["raw"] if kind == "raw" else definition["derived"]
    terms: list[str] = []
    values: list[str] = []
    if dataset_ids:
        marks = ",".join("?" for _ in dataset_ids)
        terms.append(f"dataset IN ({marks})")
        values.extend(dataset_ids)
    marker = definition.get("derived_marker")
    if kind == "derived" and marker:
        terms.append("(dataset = 'derived' AND contains(relative_path, ?))")
        values.append(marker)
    return " OR ".join(terms) if terms else "FALSE", values


@router.get("/files")
def files(
    domain: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=60, ge=1, le=200),
    product_id: str | None = None,
) -> dict[str, Any]:
    db = _connect()
    try:
        product_pattern = None
        product_scoped_domain = domain in {
            "market",
            "contract-reference",
            "product-configuration",
        }
        if product_id:
            product = db.execute(
                "SELECT exchange_code, product_code FROM v_products WHERE product_id = ? LIMIT 1",
                [product_id],
            ).fetchone()
            if not product:
                raise HTTPException(422, "Choose a product from the salt-data Catalog")
            product_pattern = f"%{product[0]}-%/{product[1]}-%/%"
        predicates = []
        parameters: list[Any] = []
        count_queries = []
        count_parameters: list[Any] = []
        scope_note = (
            "File records are scoped to the selected data domain. Some raw daily files contain multiple products; product coverage is reported separately by the Catalog."
        )
        for kind in ("raw", "derived"):
            clause, datasets = _domain_predicate(domain, kind)
            query_values: list[Any] = [kind, str(_manifest_path(kind)), *datasets]
            count_values: list[Any] = [str(_manifest_path(kind)), *datasets]
            if product_id and product_scoped_domain:
                if kind == "raw":
                    clause = "FALSE"
                    query_values = [kind, str(_manifest_path(kind))]
                    count_values = [str(_manifest_path(kind))]
                else:
                    clause += " AND relative_path LIKE ?"
                    query_values.append(product_pattern)
                    count_values.append(product_pattern)
            predicates.append(
                f"SELECT ?, relative_path, dataset, kind, format, size_bytes, mtime_ns, sha256, row_count, schema_hash, schema_columns, scanned_at FROM read_parquet(?) WHERE {clause}"
            )
            parameters.extend(query_values)
            count_queries.append(
                f"SELECT count(*) FROM read_parquet(?) WHERE {clause}"
            )
            count_parameters.extend(count_values)
        if product_id and product_scoped_domain:
            scope_note = "Showing product-specific derived files in the Manifest. Shared raw sources are omitted here; their product coverage is shown in the Catalog matrix."
        elif product_id:
            scope_note = "The published raw files are shared across products. This list shows the complete data-domain file scope; product availability is reported separately by the Catalog."
        combined = " UNION ALL ".join(predicates)
        total = sum(
            int(row[0])
            for row in db.execute(
                " UNION ALL ".join(count_queries), count_parameters
            ).fetchall()
        )
        rows = db.execute(
            f"""SELECT * FROM ({combined}) AS files
                ORDER BY size_bytes DESC, relative_path
                LIMIT ? OFFSET ?""",
            [*parameters, limit, offset],
        ).fetchall()
        return {
            "domain": domain,
            "product_id": product_id,
            "offset": offset,
            "limit": limit,
            "total": total,
            "files": [
                {
                    "kind": row[0],
                    "relative_path": row[1],
                    "dataset": row[2],
                    "manifest_kind": row[3],
                    "format": row[4],
                    "size_bytes": int(row[5] or 0),
                    "mtime_ns": int(row[6] or 0),
                    "sha256": row[7],
                    "row_count": int(row[8]) if row[8] is not None else None,
                    "schema_hash": row[9],
                    "schema_columns": row[10],
                    "scanned_at": row[11],
                    "observation": _cached_observation(row[1], row[7]),
                }
                for row in rows
            ],
            "scope_note": scope_note,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(503, f"Could not read salt-data manifests: {exc}") from exc
    finally:
        db.close()


class ObservationRequest(BaseModel):
    relative_path: str = Field(min_length=1, max_length=2048)


def _registered_file(relative_path: str) -> dict[str, Any]:
    for kind in ("raw", "derived"):
        db = duckdb.connect(":memory:")
        identity_before = _snapshot_identity(kind)
        try:
            row = db.execute(
                """SELECT path, relative_path, dataset, size_bytes, mtime_ns, sha256
                   FROM read_parquet(?) WHERE relative_path = ? LIMIT 1""",
                [str(_manifest_path(kind)), relative_path],
            ).fetchone()
        finally:
            db.close()
        if identity_before != _snapshot_identity(kind):
            raise HTTPException(409, "The manifest changed while the file record was read")
        if row:
            root = _root()
            path = (root / str(row[0])).resolve()
            if not path.is_relative_to(root):
                raise HTTPException(422, "Manifest path is outside the salt-data root")
            return {
                "kind": kind,
                "relative_path": str(row[1]),
                "dataset": str(row[2]),
                "expected_size": int(row[3] or 0),
                "expected_mtime_ns": int(row[4] or 0),
                "expected_sha256": str(row[5] or ""),
                "manifest_identity": identity_before,
                "absolute_path": path,
            }
    raise HTTPException(404, "File is not registered in the current salt-data manifests")


def _snapshot_identity(kind: str) -> tuple[int, int, int, int]:
    info = _manifest_path(kind).stat()
    return info.st_dev, info.st_ino, info.st_mtime_ns, info.st_size


def _manifest_is_current(kind: str, identity: tuple[int, int, int, int]) -> bool:
    try:
        return identity == _snapshot_identity(kind)
    except OSError:
        return False


def _complete_observation(
    task_id: str, registered: dict[str, Any], result: dict[str, Any]
) -> None:
    global ACTIVE_TASK
    status = result["status"]
    with LOCK:
        TASKS[task_id].update(result=result, status="complete")
        OBSERVATIONS[registered["relative_path"]] = {
            **result,
            "relative_path": registered["relative_path"],
            "expected_sha256": registered["expected_sha256"],
            "kind": registered["kind"],
            "dataset": registered["dataset"],
            "status": status,
        }
        ACTIVE_TASK = None
    _save_observations()


def _hash_file(task_id: str, registered: dict[str, Any], cancel: threading.Event) -> None:
    global ACTIVE_TASK
    path: Path = registered["absolute_path"]
    manifest_identity = registered["manifest_identity"]
    try:
        if not _manifest_is_current(registered["kind"], manifest_identity):
            _complete_observation(
                task_id,
                registered,
                {
                    "status": "updating",
                    "message": "The manifest changed before verification started.",
                },
            )
            return
        before = path.stat()
    except FileNotFoundError:
        status = (
            "missing"
            if _manifest_is_current(registered["kind"], manifest_identity)
            else "updating"
        )
        _complete_observation(
            task_id,
            registered,
            {
                "status": status,
                "message": "The registered file is absent."
                if status == "missing"
                else "The manifest changed during the existence check.",
            },
        )
        return
    except OSError as exc:
        _complete_observation(
            task_id,
            registered,
            {"status": "unreadable", "message": str(exc)},
        )
        return
    digest = hashlib.sha256()
    bytes_read = 0
    try:
        with path.open("rb") as stream:
            while chunk := stream.read(8 * 1024 * 1024):
                if cancel.is_set():
                    with LOCK:
                        TASKS[task_id]["status"] = "cancelled"
                        ACTIVE_TASK = None
                    return
                digest.update(chunk)
                bytes_read += len(chunk)
                with LOCK:
                    TASKS[task_id]["bytes_read"] = bytes_read
        observed = digest.hexdigest()
        after = path.stat()
        stable = (
            (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
            and _manifest_is_current(registered["kind"], manifest_identity)
        )
        matches = observed == registered["expected_sha256"]
        status = "updating" if not stable else "verified" if matches else "mismatch"
        result = {
            "status": status,
            "stable": stable,
            "matches": matches,
            "expected_sha256": registered["expected_sha256"],
            "observed_sha256": observed,
            "expected_size_bytes": registered["expected_size"],
            "observed_size_bytes": bytes_read,
            "size_matches": bytes_read == registered["expected_size"],
            "mtime_matches": after.st_mtime_ns == registered["expected_mtime_ns"],
            "relative_path": registered["relative_path"],
            "checked_at": datetime.now(UTC).isoformat(),
            "manifest_kind": registered["kind"],
        }
        _complete_observation(task_id, registered, result)
    except OSError as exc:
        status = (
            "unreadable"
            if _manifest_is_current(registered["kind"], manifest_identity)
            else "updating"
        )
        _complete_observation(
            task_id,
            registered,
            {"status": status, "message": str(exc)},
        )


@router.post("/observations", status_code=202)
def start_observation(request: ObservationRequest) -> dict[str, Any]:
    global ACTIVE_TASK
    registered = _registered_file(request.relative_path)
    if not HASH_PATTERN.fullmatch(registered["expected_sha256"]):
        raise HTTPException(409, "The manifest has no valid SHA-256 for this file")
    try:
        current_size = registered["absolute_path"].stat().st_size
    except OSError:
        current_size = registered["expected_size"]
    with LOCK:
        # Tasks start as running; the single worker and this guard serialize checks.
        if ACTIVE_TASK and TASKS.get(ACTIVE_TASK, {}).get("status") == "running":
            raise HTTPException(409, "A file integrity check is already running")
        task_id = uuid.uuid4().hex
        cancel = threading.Event()
        TASKS[task_id] = {
            "task_id": task_id,
            "relative_path": registered["relative_path"],
            "total_bytes": current_size,
            "bytes_read": 0,
            "status": "running",
            "cancel_event": cancel,
            "result": None,
        }
        ACTIVE_TASK = task_id
        HASH_EXECUTOR.submit(_hash_file, task_id, registered, cancel)
    return _public_task(TASKS[task_id])


def _public_task(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": task["task_id"],
        "relative_path": task["relative_path"],
        "total_bytes": task["total_bytes"],
        "bytes_read": task["bytes_read"],
        "status": task["status"],
        "result": task["result"],
    }


@router.get("/observations/{task_id}")
def observation(task_id: str) -> dict[str, Any]:
    with LOCK:
        task = TASKS.get(task_id)
        if not task:
            raise HTTPException(404, "Observation task not found")
        return _public_task(task)


@router.delete("/observations/{task_id}")
def cancel_observation(task_id: str) -> dict[str, Any]:
    with LOCK:
        task = TASKS.get(task_id)
        if not task:
            raise HTTPException(404, "Observation task not found")
        if task["status"] == "running":
            task["cancel_event"].set()
        return _public_task(task)
