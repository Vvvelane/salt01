"""主连 1min 上的密集度、跳空与非流动性。

一次扫描算完全部指标：DuckDB 会把下面这些标量子查询共享成同一次 parquet 扫描，
比一个指标发一条 SQL 快一个数量级。

两个口径上的坑，都在这一层里解决掉：

**交易日**。夜盘 21:00-01:00 跨午夜，直接拿 ``ts::DATE`` 分组会把周五夜盘算成
"周六"这个多出来的交易日——上期所品种三年下来会凭空多出 130 多天，分钟填充率被
稀释到 0.83。这里统一把时间戳往回推 3 小时再取日期，夜盘就归到它前面那个日盘所在
的自然日，日期集合正好等于官方交易日。

**连续性**。所有涉及"相邻两根 bar"的指标（停滞、跳空、Amihud），只在真正连续的
bar 之间算：要求合约没变，且间隔在 1~CONTIGUOUS_MINUTES 分钟内。这一条同时挡掉了
午休、隔夜、跨节和换月——否则主连换月那一下会被记成一次几百个 tick 的"跳空"。
被挡掉的那些断点不是丢弃，而是单独拿去算跨节跳空。
"""

from __future__ import annotations

from ..config import SETTINGS

# 夜盘跨午夜，往回推 3 小时让它归到前一个日盘的自然日
MARKET_DAY = "CAST(ts - INTERVAL 3 HOUR AS DATE)"

_SAME_CONTRACT = "contract IS NOT DISTINCT FROM p_contract"
_WITHIN = "date_diff('minute', p_ts, ts) BETWEEN 1 AND {gap}"
_ACROSS = "date_diff('minute', p_ts, ts) > {gap}"


def minute_sql(tick: float, *, gap: int | None = None) -> str:
    """返回一条把主连 1min 全部指标一次算完的 SQL。表名固定为 bars。"""
    if not tick or tick <= 0:
        raise ValueError(f"最小变动价位必须为正，收到 {tick!r}")
    g = gap if gap is not None else SETTINGS.contiguous_minutes
    contiguous = f"{_SAME_CONTRACT} AND {_WITHIN.format(gap=g)}"
    across = f"{_SAME_CONTRACT} AND {_ACROSS.format(gap=g)}"
    return f"""
WITH b AS (
    SELECT ts, {MARKET_DAY} AS d, close, volume, amount, contract
    FROM bars
    WHERE close IS NOT NULL AND close > 0
),
seq AS (
    SELECT b.*,
           lag(close)    OVER w AS p_close,
           lag(ts)       OVER w AS p_ts,
           lag(contract) OVER w AS p_contract
    FROM b WINDOW w AS (ORDER BY ts)
),
step AS (
    SELECT ts, amount,
           CASE WHEN {contiguous} THEN close - p_close END              AS dpx,
           CASE WHEN {contiguous} THEN close / p_close - 1 END          AS ret,
           CASE WHEN {contiguous} THEN p_close END                      AS base_close,
           CASE WHEN {across} THEN abs(close / p_close - 1) END         AS gap_ret
    FROM seq
    WHERE p_close IS NOT NULL AND p_close > 0
),
roll AS (
    -- Roll (1984) 有效价差：买卖价差的来回跳动会在成交价里留下负的一阶自协方差，
    -- S = 2*sqrt(-cov(r_t, r_lag))。r 在非连续处已经是 NULL，所以只要求相邻两个 r
    -- 都不为空，就等于要求三根连续的 bar，不会把跨节和换月拼进来。
    SELECT ret AS r, lag(ret) OVER (ORDER BY ts) AS pr FROM step
),
daily AS (
    SELECT d, year(d) AS y, count(*) AS n, sum(amount) AS amt
    FROM b GROUP BY 1, 2
),
base AS (
    SELECT y, quantile_cont(n, 0.9) AS p90 FROM daily GROUP BY 1
)
SELECT
    (SELECT count(*) FROM b)                                   AS n_bars,
    (SELECT count(*) FROM daily)                               AS n_days,
    (SELECT min(d) FROM b)                                     AS first_day,
    (SELECT max(d) FROM b)                                     AS last_day,
    (SELECT avg(least(daily.n / base.p90, 1.0))
       FROM daily JOIN base USING (y) WHERE base.p90 > 0)      AS fill_rate,
    (SELECT avg(CASE WHEN volume = 0 THEN 1.0 ELSE 0.0 END)
       FROM b)                                                 AS zero_vol_share,
    (SELECT count(*) FROM step WHERE dpx IS NOT NULL)          AS n_steps,
    (SELECT avg(CASE WHEN dpx = 0 THEN 1.0 ELSE 0.0 END)
       FROM step WHERE dpx IS NOT NULL)                        AS stale_share,
    (SELECT avg(CASE WHEN abs(dpx) > {tick} * 1.5 THEN 1.0 ELSE 0.0 END)
       FROM step WHERE dpx IS NOT NULL)                        AS jump_share,
    (SELECT quantile_cont(abs(dpx) / {tick}, 0.99)
       FROM step WHERE dpx IS NOT NULL)                        AS jump_p99_ticks,
    (SELECT quantile_cont(abs(ret), 0.99) / nullif(stddev_samp(ret), 0)
       FROM step WHERE ret IS NOT NULL)                        AS tail_ratio,
    (SELECT stddev_samp(ret) FROM step WHERE ret IS NOT NULL)  AS sigma_minute,
    -- 自协方差非负说明没有价差反弹的痕迹（通常是根本没成交），
    -- 这时估计量没有意义，置空而不是记成 0，免得死品种拿到"零价差"的满分
    (SELECT CASE WHEN covar_samp(r, pr) < 0
                 THEN 2 * sqrt(-covar_samp(r, pr)) END
       FROM roll WHERE r IS NOT NULL AND pr IS NOT NULL)       AS roll_spread,
    (SELECT covar_samp(r, pr)
       FROM roll WHERE r IS NOT NULL AND pr IS NOT NULL)       AS roll_cov,
    (SELECT avg(gap_ret) FROM step WHERE gap_ret IS NOT NULL)  AS gap_session,
    (SELECT count(*) FROM step WHERE gap_ret IS NOT NULL)      AS n_gaps,
    (SELECT avg(abs(dpx / base_close) / amount)
       FROM step
      WHERE dpx IS NOT NULL AND amount > 0 AND base_close > 0) AS amihud_raw,
    (SELECT sum(amt) / nullif(count(*), 0) FROM daily)         AS adv
"""
