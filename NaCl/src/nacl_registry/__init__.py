"""Runtime JSON reader for the NaCl knowledge registry; no Markdown/Agent dependency."""

from __future__ import annotations

import json
from copy import deepcopy
from importlib.resources import files
from pathlib import Path


def validate_registry(data: dict) -> None:
    """Deterministic schema + identity + relationship validation."""
    from jsonschema import Draft202012Validator

    schema = json.loads(
        files(__package__).joinpath("data/registry.schema.json").read_text()
    )
    Draft202012Validator(schema).validate(data)
    cards = data["cards"]
    ids = [c["factor_id"] for c in cards]
    families = {f["family_id"]: f for f in data["families"]}
    documents = {d["path"]: d for d in data["source_documents"]}
    if len(ids) != len(set(ids)) or len(families) != len(data["families"]):
        raise ValueError("Duplicate factor/family ID")
    if len(documents) != len(data["source_documents"]):
        raise ValueError("Duplicate source document")
    if {d["group"] for d in documents.values()} != {1, 2, 3, 4}:
        raise ValueError("Expected all four source groups")
    if {i: sum(c["group"] == i for c in cards) for i in range(1, 5)} != {
        1: 13,
        2: 14,
        3: 16,
        4: 15,
    }:
        raise ValueError("Incorrect Group 1–4 counts")
    for c in cards:
        family = families.get(c["family"])
        if (
            family is None
            or c["factor_id"][:3] != c["family"]
            or family["group"] != c["group"]
        ):
            raise ValueError(f"Invalid family: {c['factor_id']}")
        if any(c[k] != family[k] for k in ("core_mechanism", "core_hypothesis")):
            raise ValueError("Family inheritance mismatch")
        if c["family_name"] != family["name"] or c["level"] not in c["tags"]:
            raise ValueError("Family name or level mismatch")
        if c["source_gaps"] != (
            ["mathematical_construction"]
            if c["mathematical_construction"] is None
            else []
        ):
            raise ValueError("Source gaps must match missing source fields")
        source = c["source"]
        doc = documents.get(source["path"])
        if (
            doc is None
            or doc["sha256"] != source["file_sha256"]
            or doc["group"] != c["group"]
        ):
            raise ValueError("Source document mismatch")
        import hashlib

        if (
            hashlib.sha256(source["markdown"].encode()).hexdigest()
            != source["card_sha256"]
        ):
            raise ValueError("Source Card hash mismatch")
        if source["line_end"] < source["line_start"]:
            raise ValueError("Invalid source line span")
        for kind in ("competes_with", "composed_with"):
            rel = c[kind]
            if set(rel["factor_ids"]) - set(ids) or set(rel["family_ids"]) - set(
                families
            ):
                raise ValueError(f"Dangling relation: {c['factor_id']}/{kind}")


class Registry:
    def __init__(self, data: dict):
        validate_registry(data)
        self._data = deepcopy(data)
        self._cards = {c["factor_id"]: c for c in self._data["cards"]}

    def get(self, factor_id: str) -> dict:
        return deepcopy(self._cards[factor_id.upper()])

    def list(
        self,
        *,
        family: str | None = None,
        tag: str | None = None,
        level: str | None = None,
    ) -> list[dict]:
        return [
            deepcopy(c)
            for c in self._cards.values()
            if (family is None or c["family"] == family.upper())
            and (tag is None or tag in c["tags"])
            and (level is None or c["level"] == level)
        ]

    def graph(self, factor_ids: list[str] | None = None) -> dict:
        """Induced graph. Edges are directed source assertions, never executable dependencies."""
        ids = set(
            self._cards if factor_ids is None else (i.upper() for i in factor_ids)
        )
        if ids - self._cards.keys():
            raise KeyError(sorted(ids - self._cards.keys()))
        cards = [c for c in self._cards.values() if c["factor_id"] in ids]
        family_ids = {c["family"] for c in cards}
        nodes = [
            {"id": f["family_id"], "kind": "family", "name": f["name"]}
            for f in self._data["families"]
            if f["family_id"] in family_ids
        ]
        nodes += [
            {
                "id": c["factor_id"],
                "kind": "factor",
                "name": c["name"],
                "family": c["family"],
                "tags": c["tags"],
                "level": c["level"],
            }
            for c in cards
        ]
        edges = []
        for c in cards:
            edges.append(
                {"source": c["factor_id"], "target": c["family"], "kind": "belongs_to"}
            )
            for kind in ("competes_with", "composed_with"):
                rel = c[kind]
                for target in rel["factor_ids"] + rel["family_ids"]:
                    if target in ids | family_ids:
                        edges.append(
                            {
                                "source": c["factor_id"],
                                "target": target,
                                "kind": kind,
                                "status": rel["status"],
                                "source_text": rel["text"],
                            }
                        )
        return deepcopy({"schema_version": 1, "nodes": nodes, "edges": edges})


def load_registry(path: str | Path | None = None) -> Registry:
    source = Path(path) if path else files(__package__).joinpath("data/registry.json")
    return Registry(json.loads(source.read_text(encoding="utf-8")))


__all__ = ["Registry", "load_registry", "validate_registry"]
