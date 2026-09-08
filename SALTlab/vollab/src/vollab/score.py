"""打分与排名。

每个分项先经自己的锚点映到 0~1，再乘权重求和，满分 100。

窗口内数据太少的品种不进主榜：它们的分项要么算不出来、要么只反映一小段时间，
混进来会污染排序。它们单独列，并注明为什么出局——排名的用处之一就是把这些说清楚。
"""

from __future__ import annotations

import pandas as pd

from .config import GROUPS, SETTINGS, Settings


def score(raw: pd.DataFrame, settings: Settings = SETTINGS) -> pd.DataFrame:
    """给原始指标表打分，返回按总分降序的主榜。"""
    ranked = raw.loc[_eligible(raw, settings)].copy()

    for component in settings.components:
        values = ranked.get(component.key)
        ranked[f"s_{component.key}"] = [
            component.anchor.score(v) * component.weight
            for v in (values if values is not None else [None] * len(ranked))
        ]

    present = {c.key for c in settings.components}
    for group, keys in GROUPS.items():
        scored = [f"s_{k}" for k in keys if k in present]
        if scored:
            ranked[f"g_{group}"] = sum(ranked[c] for c in scored)

    ranked["total"] = sum(ranked[f"s_{c.key}"] for c in settings.components)
    ranked = ranked.sort_values("total", ascending=False, kind="stable").reset_index(drop=True)
    ranked.insert(0, "rank", range(1, len(ranked) + 1))
    ranked.attrs.update(raw.attrs)
    return ranked


def excluded(raw: pd.DataFrame, settings: Settings = SETTINGS) -> pd.DataFrame:
    """没进主榜的品种，以及原因。"""
    out = raw.loc[~_eligible(raw, settings)].copy()
    out["reason"] = [_reason(row, settings) for row in out.itertuples()]
    order = out["n_days"].fillna(0)
    return out.assign(_o=order).sort_values("_o", ascending=False).drop(columns="_o")


def _eligible(raw: pd.DataFrame, settings: Settings) -> pd.Series:
    days = raw["n_days"].fillna(0)
    return (days >= settings.min_days) & raw["fill_rate"].notna()


def _reason(row, settings: Settings) -> str:
    days = getattr(row, "n_days", None)
    if days is None or pd.isna(days) or days == 0:
        last = getattr(row, "hist_last", None)
        tail = f"，主连数据止于 {last:%Y-%m-%d}" if pd.notna(last) else ""
        return f"评估窗口内没有主连 1min 数据{tail}"
    return f"评估窗口内只有 {int(days)} 个交易日，不足 {settings.min_days} 天"


def missing_from_pool(all_products: pd.DataFrame, raw: pd.DataFrame) -> pd.DataFrame:
    """连候选池都没进的品种：派生数据里没有主连 1min，或者拿不到最小变动价位。"""
    out = all_products.loc[~all_products["product_id"].isin(raw["product_id"])].copy()
    out["reason"] = [
        "派生数据下没有主连 1min 文件"
        if not files
        else "catalog 里没有最小变动价位"
        for files in out["main_1min_files"]
    ]
    return out
