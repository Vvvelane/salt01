# FID004 — 开盘区间突破

## 经济假设与构造

day/night session 的前 30 个完整 1min bar 分别形成一次 opening range，之后冻结：

```text
ORH = max(High), ORL = min(Low)
mid = (ORH + ORL) / 2
hw  = (ORH - ORL) / 2
b_t = (C_t - mid) / hw
```

固定参数：`bar=1min, m_or=30, k=1.0, x=0, drawdown_tau=2.0`。日盘与夜盘分别注册，
因为 09:00/09:30 与 21:00 承接的是不同信息事件。没有夜盘的品种，其夜盘版本自然没有交易。

## 入场与退出

- `b_t > 1` 产生多头意图，`b_t < -1` 产生空头意图；必须由 close 确认。
- 同方向每个 session 最多触发一次。
- 持仓后 `b_t × pos < 0`，跌回区间中点，突破被证伪。
- `peak(b × pos) - b_t × pos > 2` 时，信号从最有利位置回撤两个半区间宽，退出。
- 初始结构保护位是 opening range 的另一侧。bar 内触及按 stop 价成交，跳空越过时按 open 成交。
- session 收盘前 5 分钟进入平仓窗口，在首个可交易 open 无条件平仓。

v3 还提出“超过单笔风险上限则跳过”，但这轮明确不建立账户资金与总风险模型，也没有给出数值
风险上限。代码保留可审计的结构保护位，不虚构 `risk_cap`，因此本版不会按账户预算过滤交易。

## 从信号到成交

opening range 使用 session 开始后的前 30 根有效观测；少量缺失分钟直接跳过，因此形成期可能比
30 分钟墙钟时间略长。突破 bar 的 close 只产生意图，实际开仓使用下一根真实 open，而不是
ORH/ORL。出现有效平 OHLC bar 的 trading date 整体不构造信号或成交。不加仓、不在同一事件
反手。输出保留结构 stop、最大有利/不利变动和退出原因，便于计算假突破与尾部收益分布。
