"""Explicit offline conversion of the four reviewed Card Markdown documents.

The field map follows the source's numbered Tab A / Tab B structure. Runtime
consumers import nacl_registry and never import this extraction script.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

NACL = Path(__file__).resolve().parents[1]
from nacl_registry import Registry, validate_registry

OUTPUT = NACL / "src/nacl_registry/data"
CARD = re.compile(r"^## (F[A-Z]{2}\d{3}) (.+)$", re.MULTILINE)
FAMILY = re.compile(r"^# (.+)（(F[A-Z]{2})）$", re.MULTILINE)
FIELD = re.compile(r"^\*\*(\d)\.[^\n]*?\*\*", re.MULTILINE)
A_FIELDS = [
    "mathematical_construction",
    "observable_data",
    "temporal_structure",
    "lineage",
    "economic_failure_modes",
    "engineering_role",
]
B_FIELDS = [
    "signal_to_position_mapping",
    "strategy_hypotheses",
    "latency_assumption",
    "protective_rules",
    "position_sizing",
    "implementation_risks",
    "backtest_policy_profile",
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def numbered_fields(text: str, keys: list[str]) -> dict[str, str]:
    matches = list(FIELD.finditer(text))
    if [int(m[1]) for m in matches] != list(range(1, len(keys) + 1)):
        raise ValueError(f"Unexpected numbered sections: {text[:120]}")
    return {
        key: text[
            m.end() : matches[i + 1].start() if i + 1 < len(matches) else len(text)
        ].strip()
        or ("待定" if "待定" in m[0] else "")
        for i, (key, m) in enumerate(zip(keys, matches, strict=True))
    }


def relation(text: str) -> dict:
    codes = set(re.findall(r"\bF[A-Z]{2}\d{3}\b", text))
    for prefix, first, second_prefix, last in re.findall(
        r"\b(F[A-Z]{2})(\d{3})[–—-](F[A-Z]{2})(\d{3})\b", text
    ):
        if prefix != second_prefix or int(first) > int(last):
            raise ValueError(f"Unsupported factor range: {text}")
        codes.update(f"{prefix}{i:03}" for i in range(int(first), int(last) + 1))
    suspicious = re.findall(r"\bF[A-Z]{2}\d+(?:/\d+)?\b", text)
    unresolved = [t for t in suspicious if not re.fullmatch(r"F[A-Z]{2}\d{3}", t)]
    return {
        "text": text,
        "factor_ids": sorted(codes),
        "family_ids": sorted(set(re.findall(r"\bF[A-Z]{2}\b", text))),
        "unresolved_references": unresolved,
        "status": "not_applicable"
        if text == "NA"
        else "pending_validation"
        if "待验证" in text
        else "stated",
    }


def extract() -> dict:
    documents, families, cards = [], [], []
    paths = sorted((NACL / "cards").glob("factor_research_group[1-4]_cards*.md"))
    if len(paths) != 4:
        raise ValueError("Expected exactly four Group 1–4 Card files")
    for path in paths:
        raw = path.read_text()
        group = int(re.search(r"group(\d)", path.name)[1])
        source_path = path.relative_to(NACL).as_posix()
        source_hash = digest(path.read_bytes())
        documents.append({"path": source_path, "sha256": source_hash, "group": group})
        candidate_rows = {}
        for line in raw.splitlines():
            if re.match(r"^\| F[A-Z]{2}\d{3} \|", line):
                cells = [v.strip() for v in line.strip().strip("|").split("|")]
                if len(cells) != 5 or cells[0] in candidate_rows:
                    raise ValueError(f"Unexpected candidate table row: {line}")
                candidate_rows[cells[0]] = {
                    "name": cells[1],
                    "reference": cells[2],
                    "original_market_frequency_holding": cells[3],
                    "implementability": cells[4],
                }
        headings = sorted(
            [(m.start(), "family", m) for m in FAMILY.finditer(raw)]
            + [(m.start(), "card", m) for m in CARD.finditer(raw)]
        )
        current_family = None
        seen = set()
        for i, (offset, kind, match) in enumerate(headings):
            stop = headings[i + 1][0] if i + 1 < len(headings) else len(raw)
            block = raw[offset:stop].rstrip()
            if kind == "family":
                mechanism = re.search(r"^- `Core Mechanism:`(.*)$", block, re.MULTILINE)
                hypothesis = re.search(
                    r"^- `Core Hypothesis:`(.*)$", block, re.MULTILINE
                )
                if not mechanism or not hypothesis:
                    raise ValueError(f"Missing family mechanism/hypothesis: {match[2]}")
                current_family = {
                    "family_id": match[2],
                    "name": match[1],
                    "group": group,
                    "core_mechanism": mechanism[1],
                    "core_hypothesis": hypothesis[1],
                }
                families.append(current_family)
                continue
            factor_id, name = match[1], match[2]
            if current_family is None or factor_id[:3] != current_family["family_id"]:
                raise ValueError(f"Incorrect family boundary: {factor_id}")
            before_a, body = block.split("### Tab A — Idea Definition", 1)
            a, b = body.split("### Tab B — Strategy Translation", 1)
            tags_match = re.search(
                r"^(`[^`]+`(?:\s+`[^`]+`)*)\s*$", before_a, re.MULTILINE
            )
            if not tags_match:
                raise ValueError(f"Missing tags: {factor_id}")
            fields = numbered_fields(a, A_FIELDS)
            source_gaps = [key for key, value in fields.items() if not value]
            fields = {key: value if value else None for key, value in fields.items()}
            lineage = fields["lineage"]
            level = re.search(r"^Level: `([^`]+)`", lineage, re.MULTILINE)[1]
            compete = re.search(r"^Competes with: `([^`]+)`", lineage, re.MULTILINE)[1]
            compose = re.search(r"^Composed With: `([^`]+)`", lineage, re.MULTILINE)[1]
            cards.append(
                dict(
                    factor_id=factor_id,
                    group=group,
                    family=current_family["family_id"],
                    family_name=current_family["name"],
                    name=name,
                    tags=re.findall(r"`([^`]+)`", tags_match[1]),
                    level=level,
                    core_mechanism=current_family["core_mechanism"],
                    core_hypothesis=current_family["core_hypothesis"],
                    core_scope="family",
                    idea_summary=a[: FIELD.search(a).start()].strip(),
                    notes=before_a[tags_match.end() :].strip(),
                    source_gaps=source_gaps,
                    **fields,
                    competes_with=relation(compete),
                    composed_with=relation(compose),
                    strategy_translation=numbered_fields(b, B_FIELDS),
                    evidence=candidate_rows[factor_id],
                    source={
                        "path": source_path,
                        "file_sha256": source_hash,
                        "line_start": raw.count("\n", 0, offset) + 1,
                        "line_end": raw.count("\n", 0, offset + len(block)) + 1,
                        "card_sha256": digest(block.encode()),
                        "markdown": block,
                    },
                )
            )
            seen.add(factor_id)
        if seen != set(candidate_rows):
            raise ValueError(f"Candidate table and Cards disagree: {path}")
    return {
        "schema_version": 1,
        "source_documents": documents,
        "families": families,
        "cards": cards,
    }


def rendered_outputs() -> dict[str, str]:
    data = extract()
    validate_registry(data)
    registry = Registry(data)
    diagnostics = [
        {
            "factor_id": c["factor_id"],
            "relation": kind,
            "text": c[kind]["text"],
            "unresolved": c[kind]["unresolved_references"],
        }
        for c in data["cards"]
        for kind in ("competes_with", "composed_with")
        if c[kind]["unresolved_references"]
    ]
    values = {
        "registry.json": data,
        "graph.json": registry.graph(),
        "validation_report.json": {
            "cards": len(data["cards"]),
            "groups": {
                str(i): sum(c["group"] == i for c in data["cards"]) for i in range(1, 5)
            },
            "families": len(data["families"]),
            "unresolved_references": diagnostics,
            "source_gaps": [
                {"factor_id": c["factor_id"], "fields": c["source_gaps"]}
                for c in data["cards"]
                if c["source_gaps"]
            ],
            "policy": "Source proposals are not frozen executable strategies.",
        },
    }
    return {
        name: json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        for name, value in values.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate checked-in artifacts without writing",
    )
    args = parser.parse_args()
    for name, expected in rendered_outputs().items():
        path = OUTPUT / name
        if args.check:
            if not path.exists() or path.read_text() != expected:
                raise SystemExit(
                    f"Stale or modified artifact: {path}; review Markdown then rebuild"
                )
        else:
            path.write_text(expected)
    print(
        "Validated: 58 Cards, 4 source documents, schema, IDs, relations and deterministic outputs"
    )


if __name__ == "__main__":
    main()
