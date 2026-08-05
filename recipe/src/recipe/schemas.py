from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable


def stable_hash(*parts: object, length: int = 24) -> str:
    payload = "\x1f".join(str(part) for part in parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:length]


def fingerprint(fields: Iterable[str], ordered: bool = True) -> str:
    values = [str(value).strip() for value in fields]
    if not ordered:
        values = sorted(values)
    return hashlib.sha256(json.dumps(values, ensure_ascii=False).encode("utf-8")).hexdigest()


KNOWN_SCHEMAS = {
    fingerprint(["datetime", "open", "high", "low", "close", "volume", "amount", "position", "symbol"]): "M",
    fingerprint(["datetime", "open", "high", "low", "close", "volume", "money", "open_interest"]): "C-Min",
    fingerprint(["symbol", "open", "high", "low", "close", "volume", "money", "open_interest", "datetime"]): "C-Day",
    fingerprint(["datetime", "symbol", "open", "high", "low", "close", "volume", "money", "open_interest"]): "C-Period",
    fingerprint(["datetime", "open", "high", "low", "close", "volume", "amount"]): "I",
}


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

