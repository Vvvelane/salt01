from __future__ import annotations

from pathlib import Path

from recipe.research import (
    EXPECTED_MANIFEST_SCHEMA,
    validate_coordinate_schema,
    validate_direction_transform,
    validate_entry_example,
    validate_event_records,
    validate_manifest,
)


def valid_manifest():
    return {
        "schema_version": EXPECTED_MANIFEST_SCHEMA,
        "research_source_id": "source-a", "project_id": "project-a", "run_id": "run-1", "run_version": "1.0.0",
        "created_at": "2026-01-01T00:00:00Z", "data_revision": "market-r1",
        "market_reference": {"source_id": "market", "asset_ids": ["opaque-asset"], "frequency": "1min", "timezone": None, "timestamp_semantics": "pending"},
        "splits": ["dev"], "artifacts": {"factors": {"path": None, "status": "no_data"}, "daily_pnl": {"path": None, "status": "no_data"}},
        "execution_assumptions": {"price_source": "next_bar_open_proxy"},
    }


def test_valid_manifest_and_malformed_manifest():
    assert validate_manifest(valid_manifest())["valid"] is True
    malformed = valid_manifest(); malformed["schema_version"] = "wrong"; malformed["artifacts"]["factors"] = {"path": "missing.csv", "status": "available"}
    result = validate_manifest(malformed, Path("/tmp/not-a-real-run"))
    ids = {issue["check_id"] for issue in result["issues"]}
    assert "manifest_version" in ids and "artifact_missing:factors" in ids


def test_event_lifecycle_reference_and_optional_postprocess():
    valid = {"event_id": "e1", "information_cutoff": "2026-01-01T09:00:00", "emitted_at": "2026-01-01T09:01:00", "reference_time_kind": "anchor_time", "reference_time": "2026-01-01T09:00:00"}
    assert validate_event_records([valid]) == []
    invalid = dict(valid); invalid["decision_time"] = "2026-01-01T07:59:00"; invalid["emitted_at"] = "2026-01-01T08:00:00"; invalid["postprocess_id"] = None
    ids = {issue["check_id"] for issue in validate_event_records([invalid])}
    assert "emitted_after_cutoff" in ids and "decision_after_emitted" in ids


def test_coordinate_contract_does_not_transform_values():
    assert validate_coordinate_schema([{"field_name": "x", "coordinate_state": "unsigned"}]) == []
    assert validate_coordinate_schema([{"field_name": "x", "coordinate_state": "bad"}])
    valid = {"event_id": "e1", "direction": 1, "coordinate_state": "raw_signed", "transformed_coordinate_state": "event_aligned", "direction_transform_id": "t1"}
    assert validate_direction_transform(valid) == []
    invalid = dict(valid); invalid["coordinate_state"] = "event_aligned"
    assert validate_direction_transform(invalid)
    assert validate_direction_transform({"coordinate_state": "unsigned", "transformed_coordinate_state": "event_aligned", "direction": 1})


def test_entry_example_requires_no_future_exit():
    assert validate_entry_example({"uses_future_exit": False}) == []
    assert validate_entry_example({"uses_future_exit": True})
