"""主连日线上的有效价差估计。

Corwin & Schultz (2012), "A Simple Way to Estimate Bid-Ask Spreads from Daily
High and Low Prices", Journal of Finance 67(2)：

    beta  = ln(H_t/L_t)^2 + ln(H_{t+1}/L_{t+1})^2
    gamma = ln(max(H_t,H_{t+1}) / min(L_t,L_{t+1}))^2
    alpha = (sqrt(2*beta) - sqrt(beta)) / (3 - 2*sqrt(2)) - sqrt(gamma / (3 - 2*sqrt(2)))
    S     = 2 * (exp(alpha) - 1) / (1 + exp(alpha))

估计量在单日上会出负值，作者的处理是逐日截 0 再平均，否则均值会被系统性压低。

为什么用日线而不是 1min：这个估计量依赖"两天的高低价里同时含着买卖价差"这一
假设，分钟级的高低价样本太少，alpha 几乎全是噪声。日线口径也是文献里的原始口径。
"""

from __future__ import annotations

DAILY_SQL = """
WITH d AS (
    SELECT ts, high, low, close
    FROM bars
    WHERE high > 0 AND low > 0 AND close > 0 AND high >= low
),
p AS (
    SELECT d.*,
           lag(high) OVER (ORDER BY ts) AS ph,
           lag(low)  OVER (ORDER BY ts) AS pl
    FROM d
),
x AS (
    SELECT
        pow(ln(high / low), 2) + pow(ln(ph / pl), 2)                      AS beta,
        pow(ln(greatest(high, ph) / least(low, pl)), 2)                   AS gamma,
        (high - low)                                                      AS rng_px,
        (high - low) / close                                              AS rng_pct
    FROM p
    WHERE ph IS NOT NULL AND pl > 0
),
a AS (
    SELECT
        (sqrt(2 * beta) - sqrt(beta)) / (3 - 2 * sqrt(2))
            - sqrt(gamma / (3 - 2 * sqrt(2)))                             AS alpha,
        rng_px, rng_pct
    FROM x
)
SELECT
    avg(greatest(2 * (exp(alpha) - 1) / (1 + exp(alpha)), 0.0)) AS cs_spread,
    avg(rng_px)                                                AS range_px,
    avg(rng_pct)                                               AS range_pct,
    count(*)                                                   AS n_pairs
FROM a
WHERE alpha IS NOT NULL AND isfinite(alpha)
"""

# 全部合约 1min：日均有成交的合约数。
# 衡量的是"除了主力还有没有第二条腿"——跨期、日历价差、换月择时都吃这个宽度。
BREADTH_SQL = """
WITH live AS (
    SELECT CAST(ts AS DATE) AS d, contract
    FROM bars
    WHERE volume > 0
    GROUP BY 1, 2
)
SELECT
    count(*)::DOUBLE / nullif(count(DISTINCT d), 0) AS active_contracts,
    count(DISTINCT contract)                        AS contracts_seen,
    count(DISTINCT d)                               AS days_seen
FROM live
"""
