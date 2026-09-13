# 03 — Signal Timing

```text
bar t open → bar t 完成 → 计算 s_t / 形成意图 → bar t+1 open 尝试成交
```

同一根 bar 的 high、low、close 和 volume 不会用于它自己的 open 成交。下一根 bar 无效或零量
时，入场意图取消；退出意图继续等待下一根可交易 open。含平 OHLC 的交易日会在研究数据准备阶段
整体排除，不进入逐 bar 信号与成交循环。

普通滚动策略的 scope 是 day/night session；交易日锚定 FTR001 的 scope 是完整交易日，可在同一
交易日内从夜盘跨到日盘；FID004 的 day/night 是两个独立 session。已知的 scope 收盘前 5 分钟
进入平仓窗口，窗口内首个可交易 open 先平仓并禁止开仓，随后才观察该 bar 的完整范围。
