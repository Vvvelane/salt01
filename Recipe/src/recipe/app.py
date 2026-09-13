from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from saltcore.read import data_root, read_bars

RECIPE_DIR = Path(__file__).resolve().parents[2]
WORKSPACE_DIR = RECIPE_DIR.parent
UNIVERSE_FILE = RECIPE_DIR / "config" / "phase1_universe.json"
REGISTRY_FILE = WORKSPACE_DIR / "NaCl" / "data" / "cards_registry_gpt5.6sol.json"
STATIC_DIR = RECIPE_DIR / "static" / "dist"
FACTORLAB_DIR = WORKSPACE_DIR / "SALTlab" / "Factorlab"
FACTOR_CONFIG = FACTORLAB_DIR / "config" / "factors.json"
FACTOR_UNIVERSE = FACTORLAB_DIR / "config" / "universe.json"

app = FastAPI(title="SALT Research Terminal", version="0.1.0", docs_url="/api/docs")


def _json_file(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _phase1_products() -> dict[str, dict]:
    universe = _json_file(UNIVERSE_FILE)
    return {
        product["id"]: product
        for exchange in universe["exchanges"]
        for product in exchange["products"]
    }


def _factor_strategies() -> dict[str, dict]:
    return {
        item["strategy_id"]: item
        for item in _json_file(FACTOR_CONFIG)["strategies"]
        if item.get("accounting_unit") != "normalized_return"
    }


def _factor_products() -> dict[str, dict]:
    return {
        item["product_id"]: item
        for item in _json_file(FACTOR_UNIVERSE)["products"]
    }


def _run_dir(strategy: dict) -> Path:
    return FACTORLAB_DIR / strategy["factor_id"].lower() / "runs" / "v3_10y"


@app.get("/api/health")
def health() -> dict:
    registry = _json_file(REGISTRY_FILE)
    try:
        market_root = str(data_root())
        market_status = "ready"
    except RuntimeError as exc:
        market_root = str(exc)
        market_status = "unavailable"
    return {
        "status": "ok",
        "market": market_status,
        "salt_data_root": market_root,
        "cards": len(registry["cards"]),
        "families": len(registry["families"]),
    }


@app.get("/api/universe")
def universe() -> dict:
    return _json_file(UNIVERSE_FILE)


@app.get("/api/cards")
def cards() -> dict:
    practiced: dict[str, list[dict]] = {}
    for item in _json_file(FACTOR_CONFIG)["strategies"]:
        practiced.setdefault(item["factor_id"], []).append(
            {"strategy_id": item["strategy_id"], "name": item["name"], "frequency": item["frequency"]}
        )
    return {**_json_file(REGISTRY_FILE), "factorlab": practiced}


@app.get("/api/factors")
def factors() -> dict:
    products = _factor_products()
    items = []
    for strategy in _factor_strategies().values():
        run_dir = _run_dir(strategy)
        available = [
            product_id
            for product_id in products
            if (run_dir / strategy["strategy_id"] / product_id / "pnl.csv").is_file()
        ]
        items.append({**strategy, "available_products": available})
    return {
        "version": _json_file(FACTOR_CONFIG)["version"],
        "strategies": items,
        "products": list(products.values()),
    }


def _curve(frame: pd.DataFrame, product_id: str) -> dict:
    daily = frame.groupby("date", as_index=False)["net_pnl"].sum().sort_values("date")
    daily["cumulative_net_pnl"] = daily["net_pnl"].cumsum()
    return {
        "product_id": product_id,
        "points": daily.to_dict(orient="records"),
    }


@app.get("/api/factor-results")
def factor_results(
    strategy: str,
    products: str,
    start: str | None = None,
    end: str | None = None,
) -> dict:
    strategies = _factor_strategies()
    if strategy not in strategies:
        raise HTTPException(status_code=422, detail=f"未知策略：{strategy}")
    selected = [value.strip().upper() for value in products.split(",") if value.strip()]
    known_products = _factor_products()
    if not selected or len(selected) != len(set(selected)) or not set(selected) <= set(known_products):
        raise HTTPException(status_code=422, detail="品种必须来自 Factorlab research11，且不能重复")

    strategy_config = strategies[strategy]
    run_dir = _run_dir(strategy_config)
    frames: dict[str, pd.DataFrame] = {}
    trades: list[pd.DataFrame] = []
    for product_id in selected:
        directory = run_dir / strategy / product_id
        pnl_file, trades_file = directory / "pnl.csv", directory / "trades.csv"
        if not pnl_file.is_file() or not trades_file.is_file():
            raise HTTPException(status_code=404, detail=f"尚未生成 {strategy} / {product_id} 的结果")
        frame = pd.read_csv(pnl_file, parse_dates=["date"])
        if start:
            frame = frame[frame["date"].ge(pd.Timestamp(start))]
        if end:
            frame = frame[frame["date"].le(pd.Timestamp(end))]
        frame = frame.copy()
        frame["date"] = frame["date"].dt.strftime("%Y-%m-%d")
        frames[product_id] = frame
        trade_frame = pd.read_csv(trades_file)
        if not trade_frame.empty:
            trade_frame["trading_date"] = pd.to_datetime(trade_frame["trading_date"])
            if start:
                trade_frame = trade_frame[trade_frame["trading_date"].ge(pd.Timestamp(start))]
            if end:
                trade_frame = trade_frame[trade_frame["trading_date"].le(pd.Timestamp(end))]
            trade_frame["trading_date"] = trade_frame["trading_date"].dt.strftime("%Y-%m-%d")
            trades.append(trade_frame)

    curves = [_curve(frame, product_id) for product_id, frame in frames.items()]
    total_input = pd.concat(
        [frame[["date", "net_pnl"]] for frame in frames.values()], ignore_index=True
    )
    total_curve = _curve(total_input, "TOTAL")
    total_daily = pd.DataFrame(total_curve["points"])
    if total_daily.empty:
        annual = []
        total_net = 0.0
        max_drawdown = 0.0
    else:
        total_daily["year"] = total_daily["date"].str[:4]
        annual_frame = total_daily.groupby("year", as_index=False)["net_pnl"].sum()
        annual_frame["cumulative_net_pnl"] = annual_frame["net_pnl"].cumsum()
        annual = annual_frame.to_dict(orient="records")
        equity = pd.concat([pd.Series([0.0]), total_daily["cumulative_net_pnl"]], ignore_index=True)
        max_drawdown = float((equity - equity.cummax()).min())
        total_net = float(total_daily["net_pnl"].sum())

    all_trades = pd.concat(trades, ignore_index=True) if trades else pd.DataFrame()
    trade_count = len(all_trades)
    win_rate = float(all_trades["net_pnl"].gt(0).mean()) if trade_count else None
    visible_trades = all_trades.sort_values("exit_time", ascending=False).head(500) if trade_count else all_trades
    trade_rows = json.loads(visible_trades.to_json(orient="records", date_format="iso"))

    summary_file = run_dir / "summary.csv"
    incomplete: list[str] = []
    if summary_file.is_file():
        summary = pd.read_csv(summary_file)
        matched = summary[summary["strategy_id"].eq(strategy) & summary["product_id"].isin(selected)]
        complete = matched["coverage_complete"].astype(str).str.lower().eq("true")
        incomplete = matched.loc[~complete, "product_id"].tolist()
    return {
        "strategy": strategy_config,
        "products": [known_products[value] for value in selected],
        "range": {
            "start": min((point["date"] for curve in curves for point in curve["points"]), default=None),
            "end": max((point["date"] for curve in curves for point in curve["points"]), default=None),
        },
        "curves": curves,
        "total_curve": total_curve,
        "annual": annual,
        "metrics": {
            "net_pnl": total_net,
            "max_drawdown": max_drawdown,
            "trades": trade_count,
            "win_rate": win_rate,
        },
        "trades": trade_rows,
        "trades_returned": len(trade_rows),
        "incomplete_ten_year_products": incomplete,
    }


@app.get("/api/bars")
def bars(
    product: str,
    start: str,
    end: str,
    freq: Literal["1min", "daily"] = "daily",
    contract: str | None = None,
    limit: int = Query(default=1800, ge=1, le=5000),
) -> dict:
    products = _phase1_products()
    product_id = product.strip().upper()
    if product_id not in products:
        raise HTTPException(status_code=422, detail=f"不在 Recipe Phase 1 清单中：{product}")

    contract_code = contract.strip().upper() if contract and contract.strip() else None
    if contract_code:
        match = re.match(r"^[A-Z]+", contract_code)
        if match is None or match.group() != products[product_id]["code"]:
            raise HTTPException(status_code=422, detail=f"{contract_code} 不属于 {product_id}")

    try:
        result = read_bars(
            contract=contract_code,
            product=None if contract_code else product_id,
            start=start,
            end=end,
            freq=freq,
        )
    except (FileNotFoundError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    frame = result.one()
    total = len(frame)
    visible = frame.tail(limit)
    rows = json.loads(visible.to_json(orient="records", date_format="iso"))
    return {
        "product": products[product_id],
        "contract": contract_code,
        "freq": freq,
        "rows": rows,
        "row_count": total,
        "returned": len(rows),
        "truncated": total > limit,
    }


if STATIC_DIR.is_dir():
    assets = STATIC_DIR / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    page = STATIC_DIR / "index.html"
    if not page.is_file():
        raise HTTPException(status_code=503, detail="先运行 npm run build 生成 Recipe 前端")
    return FileResponse(page)
