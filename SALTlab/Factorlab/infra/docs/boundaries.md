# 01 — 当前职责边界

`saltcore` 只负责从 `salt-data` 返回结构化行情。Factorlab 给行情附加交易日/session，构造信号，
执行固定的一手策略并记账。Recipe 只读取 Factorlab 已落盘结果，不在网页请求中重新跑回测。

当前执行链只有：

```text
saltcore bars → factor construction → intent → next-open fill → completed trade → daily PnL
```

每个 factor 的公式与特有状态在自己的目录；两个以上 factor 真正共用的逻辑才进入 `infra/`。
组合资金分配、总仓位、板块控制和账户级风控未定义，也不在代码中以空模块占位。
