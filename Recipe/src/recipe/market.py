"""Bounded, chronological windows over SaltCore's published history."""

from __future__ import annotations

import re
from typing import Literal

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from saltcore import scan

from .database import market_products
from .research import records

router = APIRouter(prefix="/api")


def product_info(identifier: str, available: list[dict] | None = None) -> dict:
    source = available if available is not None else market_products()
    item = next((p for p in source if p["product_id"] == identifier), None)
    if item is None:
        raise HTTPException(422, "Choose a product with published bars in salt-data")
    return {"id": identifier, "code": identifier.split(".")[1], "name": item["name"]}


def bar_slice(product: str, contract: str | None, freq: str):
    """Validate once against the Catalog and return the product with its bar source."""
    item = product_info(product)
    if contract and not re.fullmatch(re.escape(item["code"]) + r"\d{3,4}", contract):
        raise HTTPException(422, "Contract does not belong to the selected product")
    return item, scan(
        product=None if contract else product, contract=contract, freq=freq
    ).one()


def timestamp(value: str) -> str:
    try:
        parsed = pd.Timestamp(value)
        if pd.isna(parsed) or parsed.tzinfo is not None:
            raise ValueError("Use exchange-local timestamps without a timezone suffix")
        return parsed.isoformat(sep=" ")
    except (ValueError, TypeError) as exc:
        raise HTTPException(422, "Invalid exchange-local timestamp") from exc


@router.get("/universe")
def universe() -> dict:
    exchanges: dict[str, list] = {}
    catalog_products = market_products()
    for item in catalog_products:
        exchanges.setdefault(item["exchange"], []).append(
            product_info(item["product_id"], catalog_products)
        )
    return {
        "phase": "Database",
        "source": "salt-data Catalog · v_products",
        "exchanges": [
            {"id": k, "name": k, "products": v} for k, v in exchanges.items()
        ],
    }


@router.get("/contracts")
def contracts(product: str) -> dict:
    product_info(product)
    try:
        source = scan(product=product, kind="all", freq="daily").one()
        frame = source.query(
            "SELECT contract, min(ts) AS start, max(ts) AS end FROM bars GROUP BY contract ORDER BY contract DESC"
        )
        return {"contracts": records(frame)}
    except (FileNotFoundError, ValueError, KeyError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/bars")
def bars(
    product: str,
    freq: Literal["daily", "1min"] = "daily",
    contract: str | None = None,
    anchor: str | None = None,
    before: str | None = None,
    after: str | None = None,
    limit: int = Query(default=1600, ge=100, le=5000),
) -> dict:
    if sum(v is not None for v in [anchor, before, after]) > 1:
        raise HTTPException(422, "Use one of anchor, before or after")
    try:
        item, source = bar_slice(product, contract, freq)
        bounds = source.query(
            "SELECT min(ts) AS first, max(ts) AS last, count(*) AS count FROM bars"
        ).iloc[0]
        if freq == "daily":
            frame = source.query("SELECT * FROM bars ORDER BY ts")
        elif anchor:
            pivot = timestamp(anchor)
            # Include context before the selected daily bar, not just the start of a new file.
            frame = pd.concat(
                [
                    source.query(
                        f"SELECT * FROM bars WHERE ts < TIMESTAMP '{pivot}' ORDER BY ts DESC LIMIT {limit // 4}"
                    ),
                    source.query(
                        f"SELECT * FROM bars WHERE ts >= TIMESTAMP '{pivot}' ORDER BY ts LIMIT {limit * 3 // 4}"
                    ),
                ]
            ).sort_values("ts")
        else:
            where = (
                f"WHERE ts {'<' if before else '>'} TIMESTAMP '{timestamp(before or after)}'"
                if before or after
                else ""
            )
            order = "ASC" if after else "DESC"
            frame = source.query(
                f"SELECT * FROM bars {where} ORDER BY ts {order} LIMIT {limit}"
            ).sort_values("ts")
        return {
            "product": item,
            "contract": contract,
            "freq": freq,
            "rows": records(frame),
            "row_count": int(bounds["count"]),
            "returned": len(frame),
            "truncated": bool(len(frame) < bounds["count"]),
            "has_before": bool(len(frame) and frame["ts"].iloc[0] > bounds["first"]),
            "has_after": bool(len(frame) and frame["ts"].iloc[-1] < bounds["last"]),
        }
    except (FileNotFoundError, KeyError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc
