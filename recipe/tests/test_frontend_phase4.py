from pathlib import Path

STATIC = Path(__file__).parents[1] / "static"


def test_data_atlas_has_required_surfaces():
    source = (STATIC / "js/views/data_atlas.js").read_text(encoding="utf-8")
    for token in ("Catalog Tree", "Schema Compare", "Field Inspector", "Capability Matrix", "anomalies", "amount ↔ money", "position ↔ open_interest", "path-derived"):
        assert token in source


def test_semantics_config_is_present():
    semantics = (Path(__file__).parents[1] / "semantics" / "fields.yaml").read_text(encoding="utf-8")
    assert "amount:" in semantics and "position:" in semantics and "pending" in semantics

