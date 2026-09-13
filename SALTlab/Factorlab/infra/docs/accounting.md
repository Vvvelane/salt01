# 05 — Accounting

每个 factor × strategy × product 是独立的一手研究账户，累计 PnL 从 0 开始。只有真实 entry 与
exit 才形成完整 trade；意图和未成交 bar 不改变仓位。

```text
gross_pnl = side × (exit_price - entry_price) × multiplier
net_pnl   = gross_pnl - entry_fee - exit_fee
```

同一交易日平仓使用 `close_today_fee`，否则使用 `close_fee`。固定费用按手计；比例费用按
`price × multiplier × rate` 计。`pnl.csv` 按交易日逐 bar 盯市；若涨跌停使退出跨日，中间交易日
仍记录持仓价格变化，不把全部损益挤到最终退出日。逐日累计净损益必须与完整 trades 合计一致。

这不是资金收益率账户：当前没有初始权益、保证金约束、资金共享或仓位缩放。跨品种相加只能表达
“每个品种各交易一手”的金额合计。
