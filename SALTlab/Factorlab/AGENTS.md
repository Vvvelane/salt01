# Factorlab implementation rules

Before editing executable research code, read `README.md` and `docs/01-boundaries.md` through `docs/06-invariants.md`.

- This phase is a scaffold. Do not implement a backtest engine, strategy, sizing rule or visualization unless the active user task requests it.
- An Idea Card is a research hypothesis. Its Strategy Translation and named `BT_*` profile are not automatically frozen execution policy.
- Keep knowledge, factor construction, experiment definition, signal generation, execution, accounting and evaluation separate.
- Every future feature must declare data cutoff and availability. Never feed forward labels into features, selection, normalization or sizing.
- For future engine changes, cite the applicable invariant IDs in the change description and provide the corresponding small adversarial tests. Do not replace an unresolved assumption with a plausible default.
- Read market data through `saltcore`; treat `salt-data` as read-only. Do not rebuild continuous contracts here.
- Fail explicitly for missing execution semantics or unimplemented paths. Never return an empty result that appears to be a successful backtest.
- Record data/config/code/registry versions and failed runs. Do not silently drop invalid bars, orders or losing trades.
