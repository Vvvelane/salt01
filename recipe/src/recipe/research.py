from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional

EXPECTED_MANIFEST_SCHEMA = "recipe-research-v1"
REFERENCE_KINDS = {"anchor_time", "emitted_at", "custom"}
COORDINATE_STATES = {"unsigned", "raw_signed", "event_aligned"}


@dataclass
class ValidationIssue:
    check_id: str
    severity: str
    status: str
    message: str
    observed: Any = None

    def as_dict(self) -> dict[str, Any]:
        return {"check_id": self.check_id, "severity": self.severity, "status": self.status, "expected": None, "observed": self.observed, "difference": None, "source_artifact": None, "message": self.message}


def _parse_time(value: Any) -> Optional[datetime]:
    if value is None or value == "":
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _issue(issues: list[ValidationIssue], check_id: str, message: str, observed: Any = None, severity: str = "error") -> None:
    issues.append(ValidationIssue(check_id, severity, "fail", message, observed))


def validate_manifest(manifest: Any, run_dir: Optional[Path] = None) -> dict[str, Any]:
    issues: list[ValidationIssue] = []
    if not isinstance(manifest, dict):
        _issue(issues, "manifest_object", "manifest must be a JSON object")
        return {"valid": False, "issues": [item.as_dict() for item in issues], "manifest": None}
    required = ("schema_version", "research_source_id", "project_id", "run_id", "run_version", "created_at", "data_revision", "market_reference", "artifacts")
    for field in required:
        if not manifest.get(field):
            _issue(issues, f"manifest_required:{field}", f"required field missing: {field}")
    if manifest.get("schema_version") != EXPECTED_MANIFEST_SCHEMA:
        _issue(issues, "manifest_version", f"expected {EXPECTED_MANIFEST_SCHEMA}", manifest.get("schema_version"))
    for field in ("created_at",):
        if manifest.get(field) and not _parse_time(manifest[field]):
            _issue(issues, f"manifest_datetime:{field}", f"invalid ISO-8601 datetime: {field}", manifest[field])
    market = manifest.get("market_reference")
    if not isinstance(market, dict):
        _issue(issues, "market_reference_object", "market_reference must be an object")
    else:
        if not isinstance(market.get("asset_ids"), list) or not market.get("asset_ids"):
            _issue(issues, "market_reference_assets", "market_reference.asset_ids must be a non-empty list")
        if not market.get("frequency"):
            _issue(issues, "market_reference_frequency", "market_reference.frequency is required")
        if market.get("timestamp_semantics") not in {None, "pending", "start", "end"}:
            _issue(issues, "market_reference_timestamp_semantics", "timestamp_semantics must be pending/start/end", market.get("timestamp_semantics"))
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        _issue(issues, "artifacts_object", "artifacts must be an object")
    else:
        for name, spec in artifacts.items():
            if not isinstance(spec, dict):
                _issue(issues, f"artifact_object:{name}", "artifact declaration must be an object")
                continue
            status = spec.get("status")
            if status not in {"available", "no_data", "unavailable", "pending"}:
                _issue(issues, f"artifact_status:{name}", "artifact status is invalid", status)
            path = spec.get("path")
            if status == "available" and not path:
                _issue(issues, f"artifact_path:{name}", "available artifact requires path")
            if path and Path(path).is_absolute():
                _issue(issues, f"artifact_path_absolute:{name}", "artifact path must be relative", path)
            if run_dir and status == "available" and path and not (run_dir / path).is_file():
                _issue(issues, f"artifact_missing:{name}", "declared artifact file is missing", path)
    if manifest.get("execution_assumptions") is not None and not isinstance(manifest["execution_assumptions"], dict):
        _issue(issues, "execution_assumptions_object", "execution_assumptions must be an object")
    return {"valid": not issues, "issues": [item.as_dict() for item in issues], "manifest": manifest}


def validate_reference_times(record: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[ValidationIssue] = []
    information_cutoff = _parse_time(record.get("information_cutoff"))
    emitted_at = _parse_time(record.get("emitted_at"))
    decision_time = _parse_time(record.get("decision_time"))
    if record.get("emitted_at") and not emitted_at:
        _issue(issues, "emitted_at_parse", "emitted_at is not parseable")
    if record.get("information_cutoff") and not information_cutoff:
        _issue(issues, "information_cutoff_parse", "information_cutoff is not parseable")
    if emitted_at and information_cutoff and emitted_at < information_cutoff:
        _issue(issues, "emitted_after_cutoff", "emitted_at must be >= information_cutoff")
    if decision_time and emitted_at and decision_time < emitted_at:
        _issue(issues, "decision_after_emitted", "decision_time must be >= emitted_at")
    kind = record.get("reference_time_kind")
    if kind and kind not in REFERENCE_KINDS and not str(kind).startswith("custom:"):
        _issue(issues, "reference_time_kind", "reference_time_kind is not allowed", kind)
    if kind and not record.get("reference_time"):
        _issue(issues, "reference_time_required", "reference_time is required when kind is declared")
    return [item.as_dict() for item in issues]


def validate_coordinate_schema(schema: Any) -> list[dict[str, Any]]:
    issues: list[ValidationIssue] = []
    if not isinstance(schema, list):
        _issue(issues, "coordinate_schema_list", "coordinate schema must be a list")
        return [item.as_dict() for item in issues]
    for field in schema:
        if not isinstance(field, dict):
            _issue(issues, "coordinate_field_object", "coordinate field must be an object")
            continue
        state = field.get("coordinate_state")
        if state not in COORDINATE_STATES:
            _issue(issues, "coordinate_state", "coordinate_state is invalid", state)
    return [item.as_dict() for item in issues]


def validate_direction_transform(record: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[ValidationIssue] = []
    source = record.get("coordinate_state")
    target = record.get("transformed_coordinate_state")
    transformed = bool(record.get("direction_transform_id") or target)
    if not transformed:
        return []
    if source != "raw_signed" or target != "event_aligned":
        _issue(issues, "direction_transform_transition", "only raw_signed -> event_aligned is valid", {"source": source, "target": target})
    if not record.get("event_id"):
        _issue(issues, "direction_transform_event", "direction transform requires event_id")
    if not record.get("direction_transform_id"):
        _issue(issues, "direction_transform_id", "direction transform requires direction_transform_id")
    if record.get("direction") is None:
        _issue(issues, "direction_transform_direction", "direction must not be null when transforming")
    return [item.as_dict() for item in issues]


def validate_event_records(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for record in records:
        issues.extend(validate_reference_times(record))
        issues.extend(validate_direction_transform(record))
        probabilities = record.get("probabilities")
        if probabilities is not None:
            values = probabilities.values() if isinstance(probabilities, dict) else probabilities if isinstance(probabilities, list) else []
            if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in values):
                _issue_obj = ValidationIssue("probabilities_finite", "error", "fail", "probabilities must be finite or null")
                issues.append(_issue_obj.as_dict())
    return issues


def validate_entry_example(record: dict[str, Any]) -> list[dict[str, Any]]:
    if record.get("uses_future_exit") is not False:
        return [ValidationIssue("entry_no_future_exit", "error", "fail", "Entry Example must set uses_future_exit=false").as_dict()]
    return []


def _run_identity(manifest: dict[str, Any]) -> dict[str, Any]:
    return {key: manifest.get(key) for key in ("research_source_id", "project_id", "run_id", "run_version", "data_revision")}


def discover_runs(root: Optional[Path]) -> list[dict[str, Any]]:
    if not root or not root.is_dir():
        return []
    runs: list[dict[str, Any]] = []
    for manifest_path in sorted(root.glob("*/*/manifest.json")):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            validation = validate_manifest(manifest, manifest_path.parent)
            if validation["valid"]:
                runs.append({"identity": _run_identity(manifest), "manifest": manifest, "run_path": str(manifest_path.parent)})
            else:
                runs.append({"identity": _run_identity(manifest), "manifest": manifest, "validation": validation, "run_path": str(manifest_path.parent)})
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            runs.append({"identity": {}, "validation": {"valid": False, "issues": [ValidationIssue("manifest_read", "error", "fail", str(exc)).as_dict()]}, "run_path": str(manifest_path.parent)})
    return runs

