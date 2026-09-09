import hashlib
import json
import runpy
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema.exceptions import ValidationError
from nacl_registry import load_registry, validate_registry

NACL = Path(__file__).resolve().parents[1]


def test_all_58_cards_have_exact_source_spans_and_hashes():
    registry = load_registry()
    cards = registry.list()
    assert len(cards) == 58
    for card in cards:
        src = card["source"]
        path = NACL / src["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == src["file_sha256"]
        lines = path.read_text().splitlines()
        assert (
            "\n".join(lines[src["line_start"] - 1 : src["line_end"]]) == src["markdown"]
        )
        assert card["factor_id"] in lines[src["line_start"] - 1]


def test_registry_and_graph_reproduce_without_an_agent():
    builder = runpy.run_path(str(NACL / "scripts/build_registry.py"))
    for name, expected in builder["rendered_outputs"]().items():
        assert (NACL / "src/nacl_registry/data" / name).read_text() == expected


def test_missing_source_math_is_not_invented():
    cards = load_registry().list()
    assert {
        c["factor_id"] for c in cards if c["mathematical_construction"] is None
    } == {"FVR002", "FVR004", "FVO004", "FOT003"}
    assert all(c["engineering_role"] == "待定" for c in cards)


def test_ranges_family_references_and_ambiguous_text():
    r = load_registry()
    assert r.get("FTR007")["composed_with"]["factor_ids"] == [
        f"FTR{i:03}" for i in range(1, 7)
    ]
    assert r.get("FRV003")["competes_with"]["family_ids"] == ["FTR"]
    rel = r.get("FVR006")["composed_with"]
    assert rel["factor_ids"] == ["FTR004"]
    assert rel["unresolved_references"] == ["FRV04/005"]


def test_reader_filters_and_graph_subset_do_not_mutate_registry():
    r = load_registry()
    assert len(r.list(family="ftr")) == 7
    card = r.get("ftr001")
    card["tags"].clear()
    assert r.get("FTR001")["tags"]
    graph = r.graph(["FTR001", "FRV001"])
    ids = {n["id"] for n in graph["nodes"]}
    assert ids == {"FTR001", "FRV001", "FTR", "FRV"}
    assert all(e["source"] in ids and e["target"] in ids for e in graph["edges"])
    with pytest.raises(KeyError):
        r.graph(["FTR999"])


@pytest.mark.parametrize(
    "defect", ["duplicate", "dangling", "missing_field", "altered_source"]
)
def test_validation_rejects_corrupt_registry(defect):
    data = json.loads((NACL / "src/nacl_registry/data/registry.json").read_text())
    if defect == "duplicate":
        data["cards"][1] = deepcopy(data["cards"][0])
    elif defect == "dangling":
        data["cards"][0]["competes_with"]["factor_ids"] = ["FRV999"]
    elif defect == "missing_field":
        del data["cards"][0]["strategy_translation"]["latency_assumption"]
    else:
        data["cards"][0]["source"]["markdown"] += " changed"
    with pytest.raises((ValueError, ValidationError)):
        validate_registry(data)


def test_graph_node_mutation_cannot_change_registry():
    registry = load_registry()
    graph = registry.graph(["FTR001"])
    next(n for n in graph["nodes"] if n["id"] == "FTR001")["tags"].clear()
    assert registry.get("FTR001")["tags"]
