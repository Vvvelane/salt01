# vollab

从 1min 行情评估「这个品种适不适合拿来做技术指标研究」，并给出排名。

只读两类文件：`salt-data/派生数据` 下每个品种的**主连合约 1min** 和**全部合约 1min**。
读取走 [`SaltCore/read`](../../SaltCore/README.md)，vollab 自己不碰路径也不碰 parquet。

## 跑

```bash
export PYTHONPATH=SaltCore/src:SALTlab/vollab/src
python SALTlab/vollab/scripts/run_ranking.py            # 打印
python SALTlab/vollab/scripts/run_ranking.py --write    # 写回 salt-data 的文档
python SALTlab/vollab/scripts/run_ranking.py --window 5 --csv raw.csv
```

全候选池（96 个品种、三年窗口）跑完约 13 秒。

```python
from vollab import collect
from vollab.score import score, excluded

raw = collect()          # 原始指标
ranked = score(raw)      # 打分排名
excluded(raw)            # 没进主榜的，附原因
```

## 指标怎么选的

站在技术指标研究者的角度，一个品种卡在三件事上，权重按痛点排：

| 分档 | 权重 | 为什么是这个位置 |
|---|---:|---|
| 数据密集度 | 45 | 缺失的 bar、零成交的 bar、价格不动的 bar 会让均线/RSI/MACD 直接失真，而且事后补不回来 |
| 流动性与交易摩擦 | 40 | 决定信号能不能变成仓位，但不影响策略逻辑本身能不能被验证 |
| 历史长度 | 15 | 只影响样本量，满 5 年封顶 |

### 数据密集度（45）

- **分钟填充率 18**：实际 bar 数 / 该品种当年日 bar 数的 P90。用逐年经验基准而不是
  `v_session_rules`——catalog 的时段规则是按合约生命周期给的整段，`SHFE.CU` 从 1995 年
  起就标着有夜盘，而夜盘 2013 年才上线，拿它当基准会把正常历史判成缺失。
- **零成交分钟占比 12**：时间戳在、成交量为 0。这类 bar 比缺失 bar 更阴险，它不报错。
- **价格停滞占比 10**：相邻连续 bar 收盘价相同的比例。Lesmond/Ogden/Trzcinka (1999)
  zero-return 测度的分钟版。
- **交易日内部缺口 5**：品种自身首末日之间、全市场有交易而它没有的日子。只算内部，
  尾端停更不计。

### 流动性与交易摩擦（40）

- **日均成交额 14**：`log10`，锚点 1 亿 ~ 1000 亿元/日。
- **Amihud 非流动性 8**：Amihud (2002) `mean(|r| / 成交额)` 的分钟版。
- **Roll 有效价差 8**：Roll (1984) `S = 2*sqrt(-cov(r_t, r_{t-1}))`。
- **跨节跳空占比 6**：跨节跳空幅度 / 日均振幅。
- **价格分辨率 4**：日均振幅 / 最小变动价位。

### 历史长度（15）

主连 1min 首末日跨度，5 年封顶。

## 为什么用 Roll 而不是 Corwin-Schultz

一开始用的是 Corwin & Schultz (2012) 高低价价差估计，跑完发现铜是 30bp——而铜的真实
买卖价差是 1 个 tick / 8 万元 ≈ 1.25bp，高了 24 倍。CS 依赖「日内高低价分别来自
卖价成交和买价成交」这个假设，对连续交易、价差只有一个 tick 的期货，高低价几乎完全
由波动率决定，估计量就崩了。

换成 Roll，同一窗口下：铜 1.81bp、黄金 1.34bp、10 年国债 0.51bp、焦煤 6.95bp、
胶合板 32.9bp——量级和排序都对得上。CS 保留为诊断项一起列出，两者秩相关只有 0.47，
分歧本身有信息。

自协方差非负时 Roll 置空而不是记 0，否则完全没成交的死品种会拿到「零价差」的满分。

## 两个必须处理的口径坑

**夜盘跨午夜**。直接 `ts::DATE` 分组，周五夜盘会变成「周六」这个凭空多出来的交易日，
上期所品种三年多出 130 多天，分钟填充率被稀释到 0.83。统一把时间戳往回推 3 小时再
取日期，日期集合正好等于官方交易日。

**主连换月**。换月那一分钟价格会跳几百个 tick。所有涉及相邻 bar 的指标都要求
「合约没变，且间隔 ≤ 5 分钟」，一次挡掉换月、午休、隔夜、跨节；被挡掉的断点单独
拿去算跨节跳空。

## 结构

```
src/vollab/
    config.py          权重、锚点、窗口——改行为只改这里
    collect.py         跑批，每个品种 4 条 SQL
    metrics/minute.py  主连 1min：密集度、跳空、Roll、Amihud（一次扫描算完）
    metrics/daily.py   主连日线的 CS 价差 + 全部合约的合约宽度
    score.py           打分、排名、出局原因
    report.py          markdown
scripts/run_ranking.py
tests/                 SQL 语义用手搓小样本验证，不依赖真实数据
```

## 参考

- Amihud, Y. (2002). Illiquidity and stock returns. *Journal of Financial Markets*, 5(1).
- Corwin, S. & Schultz, P. (2012). A simple way to estimate bid-ask spreads from daily
  high and low prices. *Journal of Finance*, 67(2).
- Lesmond, D., Ogden, J. & Trzcinka, C. (1999). A new estimate of transaction costs.
  *Review of Financial Studies*, 12(5).
- Roll, R. (1984). A simple implicit measure of the effective bid-ask spread in an
  efficient market. *Journal of Finance*, 39(4).
