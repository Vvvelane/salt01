# 07 — Backtest Invariants

| ID | 不能违反的条件 |
|---|---|
| CAU-01 | bar close 形成的信号不能在同一 bar open 成交 |
| CAU-02 | `sd_480` 不能包含当前 bar 收益；`g` 不能用报告期未来样本 |
| SES-01 | 滚动收益不跨 day/night session 或合约变化 |
| SES-02 | scope 收盘前5分钟禁止开仓，已有仓位在首个可交易open优先平仓 |
| DAT-01 | 无效或零量的单分钟不能提供成交证据；含平 OHLC 的 trading date 整体不参与信号与成交 |
| DAT-02 | 少量缺失分钟只跳过观测，不得因此排除整个 session 或补出虚构价格 |
| EXE-01 | 未成交意图不改变仓位；已有同向仓位不能加仓 |
| EXE-02 | FID004 突破成交价是下一根 open，不是 ORH/ORL |
| ACC-01 | `net = gross - entry_fee - exit_fee`，费用只扣一次 |
| ACC-02 | 空仓时价格变化不能产生 PnL；运行结束披露任何未平仓 |
| REP-01 | 固定数据、代码和配置必须生成相同 trades 与 PnL |

这些约束由 `infra/test_infra.py` 和各 factor 根目录的测试覆盖。新增参数或运行规则必须先进入唯一
配置并解释经济含义，不能为了历史结果临时分支。
