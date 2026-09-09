"""把排名写成 markdown。"""

from __future__ import annotations

import datetime as dt

import pandas as pd

from .config import GROUPS, SETTINGS, Settings

TITLE = "中国期货品种 1min 数据可用性与流动性排名"


def _num(value, digits: int = 2, dash: str = "—") -> str:
    if value is None or (isinstance(value, float) and value != value) or pd.isna(value):
        return dash
    return f"{value:,.{digits}f}"


def _pct(value, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value * 100:.{digits}f}%"


def _day(value) -> str:
    return "—" if value is None or pd.isna(value) else f"{pd.Timestamp(value):%Y-%m-%d}"


def _table(header: list[str], rows: list[list[str]], align: str | None = None) -> str:
    sep = align or ("---:" + "|---" * (len(header) - 1))
    lines = ["| " + " | ".join(header) + " |", "|" + sep.replace("|", "|") + "|"]
    lines[1] = "|" + "|".join(sep.split("|")) + "|"
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(lines)


def render(
    ranked: pd.DataFrame,
    excluded_rows: pd.DataFrame,
    unranked: pd.DataFrame,
    *,
    settings: Settings = SETTINGS,
    generated_at: dt.datetime | None = None,
) -> str:
    asof = ranked.attrs.get("asof")
    start = ranked.attrs.get("window_start")
    end = ranked.attrs.get("window_end")
    now = generated_at or dt.datetime.now()

    out: list[str] = [f"# {TITLE}", ""]
    out += [
        f"> 生成时间：{now:%Y-%m-%d %H:%M}（Asia/Shanghai）  ",
        f"> 数据来源：`salt-data/派生数据` 下每个品种的 **主连合约 1min** 与 "
        f"**全部合约 1min**，不使用其他文件。  ",
        f"> 评估窗口：{start:%Y-%m-%d} ~ {end:%Y-%m-%d}（{settings.window_years} 年），"
        f"基准日取全候选池最新的一根 bar：{asof:%Y-%m-%d}。  ",
        f"> 生成方式：`SALTlab/vollab`，读取层 `SaltCore/read`。重跑："
        f"`python SALTlab/vollab/scripts/run_ranking.py --write`。  ",
        "> 用途：决定技术指标研究先在哪些品种上做。不是收益率排名，也不构成交易建议。",
        "",
        "## 这份排名回答什么",
        "",
        "站在做技术指标研究的人的角度，一个品种能不能用，卡在三件事上，按痛点排序：",
        "",
        "1. **分钟序列有没有洞**。缺失的 bar、成交量为 0 的 bar、价格一动不动的 bar，"
        "会让均线、RSI、MACD 这类依赖连续价格的指标直接失真，而且事后没法补救。",
        "2. **进得去出得来**。成交额、冲击成本、有效价差决定了信号能不能变成仓位；"
        "另外还要看波动是在盘中走出来的，还是在跨节跳空里一次性跳掉的。",
        "3. **历史够不够长**。只影响样本量，满五年之后边际价值很低，所以权重最小、且封顶。",
        "",
        f"总分 {settings.total_weight:.0f} 分，三档权重 "
        f"{sum(c.weight for c in settings.components if c.key in GROUPS['数据密集度']):.0f}"
        f" / {sum(c.weight for c in settings.components if c.key in GROUPS['流动性与交易摩擦']):.0f}"
        f" / {sum(c.weight for c in settings.components if c.key in GROUPS['历史长度']):.0f}。",
        "",
    ]

    out += _method_section(settings)
    out += _main_table(ranked)
    out += _detail_table(ranked)
    out += _findings(ranked, excluded_rows)
    out += _excluded_section(excluded_rows, unranked)
    out += _limits()
    return "\n".join(out) + "\n"


def _method_section(settings: Settings) -> list[str]:
    rows = []
    for group, keys in GROUPS.items():
        for key in keys:
            c = settings.by_key(key)
            direction = "越小越好" if c.anchor.lower_is_better else "越大越好"
            rows.append(
                [
                    group,
                    c.label,
                    f"{c.weight:.0f}",
                    direction,
                    f"{c.anchor.lo:g} → {c.anchor.hi:g}",
                ]
            )
    body = _table(
        ["分档", "指标", "权重", "方向", "0 分 → 满分"],
        rows,
        align="---|---|---:|---|---",
    )
    notes = []
    for group, keys in GROUPS.items():
        for key in keys:
            c = settings.by_key(key)
            notes.append(f"- **{c.label}**{f'（{c.unit}）' if c.unit else ''}：{c.note}")
    return [
        "## 打分口径",
        "",
        body,
        "",
        "每个分项按上表的锚点线性映到 0~1 再乘权重。锚点是绝对值不是横截面分位——"
        "换一批候选品种，同一个品种的分数不会变。",
        "",
        "### 每一项到底在量什么",
        "",
        *notes,
        "",
        "### 两个容易算错的地方",
        "",
        "- **交易日**。夜盘 21:00–01:00 跨午夜，直接按自然日分组会把周五夜盘算成"
        "「周六」这个凭空多出来的交易日，上期所品种三年会多出 130 多天，分钟填充率被"
        "稀释到 0.83。这里把时间戳统一往回推 3 小时再取日期，日期集合正好等于官方交易日。",
        "- **换月**。主连在换月那一分钟会有一次几百个 tick 的价格跳变。所有涉及相邻 bar "
        "的指标都要求「合约没变，且间隔在 5 分钟以内」，把换月、午休、隔夜、跨节一起挡掉；"
        "被挡掉的断点单独拿去算跨节跳空。",
        "",
    ]


def _main_table(ranked: pd.DataFrame) -> list[str]:
    rows = []
    for r in ranked.itertuples():
        rows.append(
            [
                str(r.rank),
                f"`{r.product_id}` {r.name}",
                _num(r.total, 1),
                _num(getattr(r, "g_数据密集度"), 1),
                _num(getattr(r, "g_流动性与交易摩擦"), 1),
                _num(getattr(r, "g_历史长度"), 1),
                _pct(r.fill_rate),
                _pct(r.stale_share, 1),
                _num(r.adv / 1e8, 1),
                _num(r.roll_bp, 2),
                _num(r.history_years, 1),
            ]
        )
    return [
        "## 总排名",
        "",
        "成交额单位为亿元/日，Roll 价差单位为 bp。",
        "",
        _table(
            [
                "#",
                "品种",
                "总分",
                "密集",
                "流动",
                "长度",
                "填充率",
                "停滞",
                "成交额",
                "价差",
                "历史",
            ],
            rows,
            align="---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:",
        ),
        "",
    ]


def _detail_table(ranked: pd.DataFrame) -> list[str]:
    rows = []
    for r in ranked.itertuples():
        rows.append(
            [
                str(r.rank),
                f"`{r.product_id}`",
                _pct(r.zero_vol_share, 2),
                _pct(r.day_gap_share, 2),
                _num(r.amihud, 2),
                _pct(r.gap_ratio, 1),
                _num(r.range_ticks, 0),
                _num(r.active_contracts, 1),
                _num(r.cs_spread * 1e4, 1) if pd.notna(r.cs_spread) else "—",
                _day(r.last_day),
            ]
        )
    return [
        "## 分项明细",
        "",
        "`CS 价差` 只作诊断：Corwin-Schultz 对连续交易的期货系统性偏高（铜 30bp vs "
        "真实 1.25bp），不参与打分，列在这里是为了和 Roll 相互印证——两者的秩相关只有 0.47，"
        "分歧本身就是信息。`合约宽度` 是全部合约 1min 里日均有成交的合约数，"
        "决定了能不能做跨期和日历价差。",
        "",
        _table(
            ["#", "品种", "零成交", "日缺口", "Amihud", "跳空占比", "分辨率", "合约宽度", "CS价差", "数据止于"],
            rows,
            align="---:|---|---:|---:|---:|---:|---:|---:|---:|---",
        ),
        "",
    ]


def _findings(ranked: pd.DataFrame, excluded_rows: pd.DataFrame) -> list[str]:
    top = ranked.head(10)
    worst_stale = ranked.nlargest(5, "stale_share")
    worst_fill = ranked.nsmallest(5, "fill_rate")
    coarse = ranked.nsmallest(5, "range_ticks")
    big_but_coarse = ranked[(ranked["log_adv"] > 10.3) & (ranked["range_ticks"] < 60)]

    lines = [
        "## 结果里值得注意的几点",
        "",
        f"- **第一梯队是股指、贵金属和几个头部农产品**："
        + "、".join(f"`{r.product_id}` {r.name}" for r in top.head(5).itertuples())
        + "。共同点是分钟填充率接近 1、几乎没有零成交 bar、停滞率在 10% 以下。",
    ]

    if len(big_but_coarse):
        names = "、".join(
            f"`{r.product_id}` {r.name}（{r.range_ticks:.0f} tick/日，停滞 {r.stale_share:.0%}）"
            for r in big_but_coarse.head(6).itertuples()
        )
        lines.append(
            f"- **成交额巨大但价格粗颗粒的一类**：{names}。"
            "这些品种按成交额排能进前十，但最小变动价位相对价格太大，一天只走几十个 tick，"
            "分钟收益里大量是 0。做技术指标研究时，它们更适合放到 5min 以上的周期，"
            "在 1min 上做形态和突破会大量踩到量化台阶造成的假信号。"
        )

    lines += [
        "- **停滞率最高的五个**："
        + "、".join(f"`{r.product_id}` {r.name} {r.stale_share:.0%}" for r in worst_stale.itertuples())
        + "。",
        "- **填充率最低的五个**："
        + "、".join(f"`{r.product_id}` {r.name} {r.fill_rate:.1%}" for r in worst_fill.itertuples())
        + "。",
        "- **价格分辨率最低的五个**："
        + "、".join(
            f"`{r.product_id}` {r.name} {r.range_ticks:.0f} tick/日" for r in coarse.itertuples()
        )
        + "。",
        "",
    ]
    return lines


def _excluded_section(excluded_rows: pd.DataFrame, unranked: pd.DataFrame) -> list[str]:
    lines = ["## 没进排名的品种", ""]
    if len(excluded_rows):
        rows = [
            [
                f"`{r.product_id}` {r.name}",
                _num(getattr(r, "n_days", None), 0),
                _day(getattr(r, "hist_last", None)),
                r.reason,
            ]
            for r in excluded_rows.itertuples()
        ]
        lines += [
            "### 窗口内数据不足",
            "",
            _table(["品种", "窗口内交易日", "主连数据止于", "原因"], rows, align="---|---:|---|---"),
            "",
        ]
    if len(unranked):
        rows = [
            [f"`{r.product_id}` {r.name}", str(r.main_1min_files), str(r.all_1min_files), r.reason]
            for r in unranked.itertuples()
        ]
        lines += [
            "### 连候选池都没进",
            "",
            _table(["品种", "主连1min文件", "全部合约1min文件", "原因"], rows, align="---|---:|---:|---"),
            "",
        ]
    return lines


def _limits() -> list[str]:
    return [
        "## 使用限制",
        "",
        "- 这是**数据可用性**排名，不是收益率、夏普或可交易性排名。手续费、保证金、"
        "涨跌停、持仓限额、换月冲击都没有进分数。",
        "- 分数只在同一套锚点下可比。改了 `SALTlab/vollab/src/vollab/config.py` 里的权重或锚点，"
        "就要整份重跑，不能和旧版混着看。",
        "- **本轮排名跑在已经补齐的派生数据上**。2026-09-08 之前，派生数据是落后于原始数据的："
        "主连 1min 有 72 个品种停在 2026-08-07、81 个品种共缺 555512 行，"
        "另有 43 个主连文件和 9482 个合约日线文件把 `时间` 存成了 VARCHAR，"
        "任何不显式 CAST 的巡检都查不到它们。根因是失败的下载批次更新了原始文件和 manifest、"
        "派生却没做完，之后每一批都判定「没变」而永久跳过。"
        "现已用 `代码/scripts/rederive_market.py` 全部补齐并加了回归测试；"
        "补齐前后本排名的秩相关是 0.995，78 个品种里 48 个名次未变——"
        "三年窗口里差 21 天确实影响很小，但那 9525 个错类型的文件是实打实会让巡检出错的。",
        "- `元数据/catalog.duckdb` 里的 `row_count` / `max_time` 仍可能滞后于一次 `scan`；"
        "本排名的所有行数和时间范围都是现扫 parquet 得到的，catalog 只用来取"
        "最小变动价位和交易日历。",
        "- 「有分钟记录」不等于「这一分钟有成交」，所以填充率和零成交占比必须一起看："
        "填充率 100% 而零成交 86% 的品种（如 `DCE.BB` 胶合板），时间戳是齐的，价格是死的。",
        "",
    ]
