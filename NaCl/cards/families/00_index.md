# NaCl Card 家族索引

58 张 Card 按 [factor_architecture.md](../factor_architecture.md) 第二部分的结构重排：

- **轴 A · 经济假设** → 家族（每张卡只属于一个家族）
- **轴 B · 表达** → 家族内的表达簇（同一假设的不同侧重，可用窗口对齐后的 X 相关性检验）
- **轴 C · 结构** → 卡片属性：方向性 / 条件性 / 形状性；单标的 / 截面 / 多腿；数据需求。只打标签，不再按 C 重复分组。

卡片正文与原四份研究组文档逐字一致，仅在每张卡标题下新增一行“结构位置”。机器可读版本见 [cards_registry_gpt5.6sol.json](../../data/cards_registry_gpt5.6sol.json)。

## 结构树

- **[TRD 趋势延续](01_TRD.md)** · Trend continuation · 15 张
  - TRD-B1 过去收益线性加权（净位移核）：FTR001（方向性·单标的）、FTR002（方向性·单标的）、FTR003（方向性·单标的）、FTR005（方向性·单标的）、FTR006（方向性·单标的）、FCM001（方向性·截面）、FCM003（方向性·截面）、FCS004（方向性·截面）
  - TRD-B2 开盘时段信息延续：FID001（方向性·单标的）、FID002（方向性·单标的）
  - TRD-B3 区间突破：FTR004（形状性·单标的）、FID004（形状性·单标的）
  - TRD-B4 趋势 × 参与确认：FVO007（方向性×条件性·单标的）、FCM004（方向性×条件性·截面）
  - TRD-B5 趋势路径效率：FTR007（条件性·单标的）
- **[REV 短期反转](02_REV.md)** · Short-term reversal · 8 张
  - REV-B1 负净位移：FRV001（方向性·单标的）、FCM002（方向性·截面）
  - REV-B2 偏离局部锚点：FRV004（方向性·单标的）、FRV005（方向性·单标的）
  - REV-B3 跨时段压力回吐：FRV006（方向性·单标的）、FID003（方向性·单标的）
  - REV-B4 反转 × 活动门控：FRV002（方向性×条件性·单标的）、FRV003（方向性×条件性·单标的）
- **[REG 序列依赖状态](03_REG.md)** · Serial-dependence regime · 1 张
  - REG-B1 方差比：FOT003（条件性·单标的）
- **[VOL 波动持续](04_VOL.md)** · Volatility persistence · 7 张
  - VOL-B1 收益平方估计：FVR001（条件性·单标的）、FVR007（条件性·单标的）
  - VOL-B2 价格区间估计：FVR002（条件性·单标的）、FVR003（条件性·单标的）、FVR004（条件性·单标的）、FVR005（条件性·单标的）、FVR006（条件性·单标的）
- **[ACT 交易活动与持仓](05_ACT.md)** · Trading activity & open interest · 5 张
  - ACT-B1 成交量与成交额：FVO001（条件性·单标的）、FVO002（条件性·单标的）、FVO003（条件性·单标的）
  - ACT-B2 持仓量：FVO005（条件性·单标的）、FVO006（条件性·单标的）
- **[PRM 风险特征溢价](06_PRM.md)** · Risk-characteristic premia · 7 张
  - PRM-B1 波动率定价：FCS001（方向性·截面）、FCS002（方向性·截面）
  - PRM-B2 偏度与上下行不对称：FCS005（方向性·截面）、FOT001（方向性·单标的）、FOT002（方向性·单标的）
  - PRM-B3 非流动性补偿：FVO004（条件性·单标的）、FCS003（方向性·截面）
- **[TSC 期限结构与持有收益](07_TSC.md)** · Term structure & carry · 7 张
  - TSC-B1 静态曲线斜率（carry）：FCA001（方向性·截面）、FCA002（方向性·单标的）、FCA003（方向性·单标的）
  - TSC-B2 曲线曲率：FCA004（方向性·多腿）
  - TSC-B3 期限价差动态：FCA005（方向性·截面）、FCA006（方向性·多腿）、FCA007（方向性·多腿）
- **[RLV 相对价值收敛](08_RLV.md)** · Relative-value convergence · 4 张
  - RLV-B1 统计关系偏离：FRL001（方向性·多腿）、FRL002（方向性·多腿）、FRL003（方向性·截面）
  - RLV-B2 产业加工价差：FRL004（方向性·多腿）
- **[SEA 日历季节性](09_SEA.md)** · Calendar seasonality · 4 张
  - SEA-B1 年内季节：FSE001（方向性·单标的）
  - SEA-B2 月内与周内节奏：FSE002（方向性·单标的）、FSE003（方向性·单标的）、FSE004（方向性·单标的）

## 四段式卡片框架

试行范围：FTR001、FRV001、FID004、FCM001（已在 Factorlab 实践）。其余 54 张卡暂保持原样，四段待处理。

1. **只写经济层**（[factor_architecture.md](../factor_architecture.md) §3）：规则的形式与符号，不写数值。数值只在 `SALTlab/Factorlab/config/factors.json`，可调，是后续学习与修改的对象。
2. **四段**：
   - **构造**：$X_t$ 的公式、可用时点、有效性条件；同一 idea 的实现变体在这里区分。
   - **入场**：空仓时 $X_t$ 满足什么形式开仓。
   - **持仓更新**：持仓期间经济状态怎么变化；没有就写"无"。
   - **出场**：$X_t$ 与持仓满足什么形式平仓。
3. **层归属按 §6.3 判据**：
   - 只依赖 $X_t$ 与上一期持仓 → 经济层，写进四段。
   - 依赖入场时点、入场价、持仓期极值、交易史或账户 → 仓位层。
   - 依赖交易所合约规则或时钟 → 制度层。
   - 研究时选定的持仓范围（session / 交易日 / 研究期）→ 研究边界。它不是交易所规则，同一 idea 的不同变体可以不同。
   - 后三类不写进四段；卡末"本卡不定义"只列这张卡特有的规则。
4. **判据判不了的**写 ⚠ 并说明理由（§6.4），不强行归类。
5. 原 Tab A / Tab B 移入卡末附录，暂不删除。重新生成 JSON 时以四段为唯一来源；附录中的失效风险、关系等是否保留，由重生成时决定。

### 所有卡共享、不在卡内重复的非经济规则

| 规则 | 层 | Factorlab 位置 |
| --- | --- | --- |
| bar 收盘后出信号，下一根 open 尝试成交，另可再等待若干根 bar | 执行 | `config/execution.json`（`execution_delay_bars`）、`infra/backtest.py` |
| 滑点、手续费 | 执行 | `config/instruments.json` |
| 不加仓；同一事件不反手 | 仓位层 | `infra/backtest.py` |
| 持仓范围收盘前若干分钟强平并禁止开仓 | 研究边界 | `config/factors.json` 的 `holding_scope` + `config/execution.json` 的 `force_flat_minutes_before_scope_end` |
| 主连换月、合约最后交易日强制退出 | 制度层 | `infra/backtest.py`、`fcm001/dev/factor.py` |
| 平 OHLC 或无效 bar 不出信号、不成交 | 数据有效性 | `config/execution.json` |

## 旧研究组对照

| 旧家族 | 新位置 |
| --- | --- |
| FTR | FTR001→TRD-B1、FTR002→TRD-B1、FTR003→TRD-B1、FTR005→TRD-B1、FTR006→TRD-B1、FTR004→TRD-B3、FTR007→TRD-B5 |
| FCM | FCM001→TRD-B1、FCM003→TRD-B1、FCM004→TRD-B4、FCM002→REV-B1 |
| FCS | FCS004→TRD-B1、FCS001→PRM-B1、FCS002→PRM-B1、FCS005→PRM-B2、FCS003→PRM-B3 |
| FID | FID001→TRD-B2、FID002→TRD-B2、FID004→TRD-B3、FID003→REV-B3 |
| FVO | FVO007→TRD-B4、FVO001→ACT-B1、FVO002→ACT-B1、FVO003→ACT-B1、FVO005→ACT-B2、FVO006→ACT-B2、FVO004→PRM-B3 |
| FRV | FRV001→REV-B1、FRV004→REV-B2、FRV005→REV-B2、FRV006→REV-B3、FRV002→REV-B4、FRV003→REV-B4 |
| FOT | FOT003→REG-B1、FOT001→PRM-B2、FOT002→PRM-B2 |
| FVR | FVR001→VOL-B1、FVR007→VOL-B1、FVR002→VOL-B2、FVR003→VOL-B2、FVR004→VOL-B2、FVR005→VOL-B2、FVR006→VOL-B2 |
| FCA | FCA001→TSC-B1、FCA002→TSC-B1、FCA003→TSC-B1、FCA004→TSC-B2、FCA005→TSC-B3、FCA006→TSC-B3、FCA007→TSC-B3 |
| FRL | FRL001→RLV-B1、FRL002→RLV-B1、FRL003→RLV-B1、FRL004→RLV-B2 |
| FSE | FSE001→SEA-B1、FSE002→SEA-B2、FSE003→SEA-B2、FSE004→SEA-B2 |

## 旧文档前言 · factor_research_group1_cards 3d59c0273afd80c89430c90ada4cacdd.md

## 研究组 1：趋势与时间序列动量、短期反转与均值回复

> 本文件是 Factor Lab 的独立研究组文档。每次研究先抽象经济逻辑，再审阅数学构造和因果时序，最后审阅入场、出场与执行规则；参数暂不视为最终冻结。统一成交约定见 [`factor_research.md`](factor_research.md)。
> 

## 1. 候选因子主表

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | --- | --- | --- |
| 趋势与时间序列动量 | `FTR` | 7 | 延迟反应、行为持续、趋势风险溢价 | 高 |
| 短期反转与均值回复 | `FRV` | 6 | 过度反应、流动性供给、短期价格压力 | 高 |


## 旧文档前言 · factor_research_group2_cards 3d59c0273afd80a18f9de68a358fb35b.md

## 研究组 2：波动率与价格区间、成交量与持仓量

> 本文件是 Factor Lab 的独立研究组文档。每次研究先抽象经济逻辑，再审阅数学构造和因果时序，最后审阅入场、出场与执行规则；参数暂不视为最终冻结。统一成交约定见 [`factor_research.md`](factor_research.md)。
> 

## 1. 候选因子主表

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | --- | --- | --- |
| 波动率与价格区间 | `FVR` | 7 | 风险状态、波动持续、价格路径信息 | 高 |
| 成交量、成交额与持仓量 | `FVO` | 7 | 参与度、信息流、拥挤和风险承接 | 高/中 |


## 旧文档前言 · factor_research_group3_cards 3d59c0273afd80a486dedb01250eb132.md

## 研究组 3：截面、期限结构与跨期

> 本文件是 Factor Lab 的独立研究组文档。每次研究先抽象经济逻辑，再审阅数学构造和因果时序，最后审阅入场、出场与执行规则；参数暂不视为最终冻结。统一成交约定见 [`factor_research.md`](factor_research.md)。
> 

## 1. 候选因子主表

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | --- | --- | --- |
| 截面动量与反转 | `FCM` | 4 | 相对强弱、跨品种延迟反应 | 高 |
| 截面波动率、流动性与相对强弱 | `FCS` | 5 | 风险补偿、彩票偏好、流动性 | 中 |
| 期限结构、跨期与 roll yield | `FCA` | 7 | 库存/便利收益、套保压力、期限错位 | 高但需 metadata |


## 旧文档前言 · factor_research_group4_cards 3d59c0273afd80638987e2babd5fed79.md

## 研究组 4：相对价值、季节性、低频日内与其他因子

> 本文件是 Factor Lab 的独立研究组文档。每次研究先抽象经济逻辑，再审阅数学构造和因果时序，最后审阅入场、出场与执行规则；参数暂不视为最终冻结。统一成交约定见 [`factor_research.md`](factor_research.md)。
> 

## 1. 候选因子主表

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | --- | --- | --- |
| 跨品种相对价值与统计套利 | `FRL` | 4 | 共同经济驱动、长期均衡、加工利润 | 中 |
| 季节性与日历 | `FSE` | 4 | 生产周期、套保节奏、资金流 | 低/中 |
| 低频日内 | `FID` | 4 | 开盘信息、日内持续或流动性反转 | 中但 session pending |
| 其他 OHLCV/OI 因子 | `FOT` | 3 | 偏度偏好、上下行风险、序列依赖 | 中 |

