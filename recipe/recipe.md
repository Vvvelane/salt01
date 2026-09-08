# Recipe：量化研究可视化项目实施规格

> 状态：设计冻结候选（Phase 0）
>
> 本文供后续 Codex 按 Phase 直接实施。当前阶段不得创建 `/Users/kangbohang/Desktop/start/salt01/recipe`，不得编写网页、服务、配置、测试或 placeholder。

## 0. 一句话定义

Recipe 是一个轻量、只读的量化研究 Web App，固定包含三类功能：

1. **市场路径（Market Explorer）**：浏览当前真实的分钟及以上 OHLCV/OI 类行情。
2. **数据语义（Data Atlas）**：解释数据族、schema、字段身份、来源与能力边界。
3. **研究审计（Research Audit）**：展示并核验其他项目已经产出的因子、信号、决策、交易与回测结果。

Recipe 不采集、不清洗生产数据，不计算因子，不训练模型，不产生交易信号，不执行回测，也不下单。

---

## 1. 项目定位与边界

### 1.1 Recipe 是什么

- 研究数据浏览工具；
- 数据结构和经济语义解释工具；
- 因子与回测输出的只读展示和一致性审计工具；
- 当前 CSV 数据源和未来研究输出之间的轻量适配层。

### 1.2 Recipe 不是什么

- 行情采集或生产 ETL；
- 实时行情或交易系统；
- 下单、账户或权限系统；
- 因子计算、selector、label、模型训练或回测引擎；
- 自动调参或实验管理平台；
- NaCl、pathpulse 或其他通用量化框架；
- 通用 BI Dashboard。

### 1.3 强制业务边界

- 顶部导航始终只有三个主视图：市场路径、数据语义、研究审计。
- 任何新增组件必须归属于上述三类之一；不能增加第四类业务。
- 当前数据没有 Level2 时，不能用 bar 字段模拟 Level2。
- 当前没有研究输出时，研究审计页必须展示真实空状态，不能生成示例 PnL。
- 前端永远只接收 `asset_id`、`run_id` 等逻辑身份，不接收或硬编码行情绝对路径。

---

## 2. 输入资料、事实优先级与证据等级

### 2.1 本规格使用的输入

1. 当前行情目录：
   `/Users/kangbohang/Desktop/start/salt01/量化/Alpha01/data/价格行为`
2. 旧可视化需求：
   `/Users/kangbohang/Desktop/start/salt01/knowledge/notes/复线内容/可视化.md`
3. 当前数据审计：
   `/Users/kangbohang/Desktop/start/salt01/blueprints/current_state_audit.md`
4. 架构参考：
   `/Users/kangbohang/Desktop/start/salt01/blueprints/architecture.md`
5. 迁移参考：
   `/Users/kangbohang/Desktop/start/salt01/blueprints/legacy_migration_map.md`

### 2.2 事实优先级

1. 当前行情目录中的实际路径、文件和字段；
2. `current_state_audit.md` 已确认事实；
3. 本规格定义的新 Recipe 边界；
4. 旧可视化的功能目的和交互语义；
5. 旧路径、旧 factor/policy ID、旧结果与历史实现名称。

### 2.3 本次检查的证据等级

| 证据等级 | 本次实际操作 | 可支持的结论 |
| --- | --- | --- |
| 完整目录扫描 | 枚举全部文件名和路径层级，按数据族、频率、交易所、品种和路径深度统计 | 文件数量、路径模式、覆盖结构和异常路径 |
| 分层表头扫描 | 从 122 个“数据族 × 频率 × 交易所”代表文件读取表头 | 代表性 schema 家族；不能声称全库无 schema 漂移 |
| 内容边界抽样 | 从 26 个跨数据族、频率和交易所的代表文件读取表头、首行、尾行及文件大小 | 代表性时间文本、边界日期、夜盘存在、字段值形态 |
| 既有审计 | 采用 `current_state_audit.md` 的 dtype 样本与能力判断 | 样本 dtype、已知缺失能力和 pending 语义 |
| 旧需求来源 | 完整阅读旧 `可视化.md` | 功能目的和历史交互，不代表当前数据存在 |
| 设计假设 | 本规格中的 API、页面和缓存方案 | 后续实现决策，不是当前行情事实 |

### 2.4 未完成的全库检查

曾尝试逐一打开全部 86,397 个 CSV 读取表头；当前存储对大量小文件的冷访问耗时过长，因此停止。后续不得把 122 个代表文件的五类表头写成“全库只有五类 schema”。

完整 schema 漂移验证属于 Catalog Phase 的显式、可续跑维护任务。服务启动和普通 API 请求不得依赖全库表头重扫。

---

## 3. 当前数据资产与能力

### 3.1 完整目录扫描结果

行情目录共有：

- 文件总数：86,448
- CSV：86,397
- `.DS_Store`：51
- 逻辑文件大小约 31.4 GiB（`du -skA`）
- 当前文件系统实际占用约 0.85 GiB（`du -sk`）；服务容量设计应按逻辑大小和读取成本判断，不能按压缩/克隆后的占用判断。

CSV 分布：

| 数据族 | 频率 | CSV 数 |
| --- | --- | ---: |
| 主要合约 | 1、3、5、10、15、30、60 分钟 | 每个频率 97 |
| 主要合约 | 日、周、月、季度 | 每个频率 91 |
| 全部合约 | 1 分钟 | 10,095 |
| 全部合约 | 5、15、30、60 分钟 | 每个频率 9,639 |
| 全部合约 | 日、周、月、季度 | 每个频率 9,175 |
| IM 指数数据 | 分钟、日 | 2 个规范文件 |
| IM 指数 checkpoint | 日 | 1 个隐藏副本，默认排除 |

交易所目录覆盖：

- 期货：CFFEX、CZCE、DCE、GFEX、INE、SHFE
- 指数：SSE（由 `SH.000852` 文件身份映射，不是期货交易所目录）

目录名层面观察到：

- 主要合约约 100 个“交易所 × 品种”组合；
- 全部合约约 98 个“交易所 × 品种”组合；
- 不同频率的品种覆盖并不完全一致；
- 这些是路径身份统计，不代表每个文件均已完成内容质量验证。

### 3.2 路径家族

#### 主要合约分钟

```text
主要合约/{frequency}/{exchange}/{product}/{product}.csv
```

示例：

```text
主要合约/1min/CFFEX/IC/IC.csv
主要合约/1min/SHFE/RB/RB.csv
```

#### 主要合约高周期

```text
主要合约/{日|周|月|季度}/{exchange}.{product}.csv
```

#### 全部合约分钟

```text
全部合约/{frequency}/{exchange}/{product}/{contract}.csv
```

#### 全部合约高周期

```text
全部合约/{日|周|月|季度}/{product}/{exchange}.{contract}.csv
```

#### 指数

```text
IM指数数据/SH.000852.csv
IM指数数据/SH.000852-daily.csv
```

### 3.3 已发现的路径异常

#### IC 1 分钟嵌套副本

存在 134 个文件：

```text
全部合约/1min/CFFEX/IC/1min/*.csv
```

它们全部有同名直接路径：

```text
全部合约/1min/CFFEX/IC/*.csv
```

本次检查结果：

- 134/134 有直接路径同名文件；
- 134/134 文件大小相同；
- 134/134 mtime 相同；
- 5 个样本的首尾 32 KiB 相同；
- 未对 134 对文件执行完整字节 hash。

Catalog 必须把嵌套路径标记为 `suspected_alias`，默认以直接路径为 canonical。不能让前端把二者显示成两个合约，也不能在未完整校验前删除或修改源文件。

#### checkpoint

`IM指数数据/.ipynb_checkpoints/SH.000852-daily-checkpoint.csv` 默认排除。隐藏目录和编辑器副本不进入正式资产 catalog。

### 3.4 分层表头扫描得到的五类代表性 schema

> 这是 122 个分层代表文件的结果，不是全库证明。

#### Schema M：主要合约，各抽样频率一致

```text
datetime,open,high,low,close,volume,amount,position,symbol
```

#### Schema C-Min：全部合约分钟

```text
datetime,open,high,low,close,volume,money,open_interest
```

分钟文件没有行内 symbol；合约身份来自路径和文件名。

#### Schema C-Day：全部合约日线

```text
symbol,open,high,low,close,volume,money,open_interest,datetime
```

#### Schema C-Period：全部合约周、月、季度

```text
datetime,symbol,open,high,low,close,volume,money,open_interest
```

#### Schema I：指数分钟与日线

```text
datetime,open,high,low,close,volume,amount
```

适配器必须按字段名读取，不能依赖列位置。

### 3.5 内容抽样事实

- 代表文件首尾时间显示数据覆盖多个历史区间，末行普遍到 2026-02-27。
- 主要合约 1 分钟代表文件单个可达约 80–107 MB；不能把全部文件加载到浏览器。
- INE、SHFE 等分钟样本中存在 21:00 或 23:xx 记录，证明夜盘客观存在。
- 文件没有显式 `trading_date` 或 `session`；自然日不能自动等同交易日。
- 指数日线使用如 `2014/10/17`、`2026/2/27` 的斜杠日期，其他样本多为横线格式。
- 部分高周期文件内 symbol 使用小写品种部分，例如 `DCE.pp2111`；Catalog 必须同时保存 raw symbol 和 canonical identity。
- CSV 数值列在不同文件中可能被推断为整数或浮点；前端不能依赖 JSON 数字是否原为 int。

### 3.6 能力矩阵

| 能力 | 当前状态 | Recipe 处理 |
| --- | --- | --- |
| OHLC | available | 市场路径主图 |
| volume | available | 成交活动子图；不解释为订单簿深度 |
| amount / money | available，语义 pending | 以原字段名和 pending 徽标展示 |
| position | available，是否为 OI pending | 保存为 `raw_position`，不自动改名 |
| open_interest | 全部合约 available | 展示为供应商字段；不与 position 自动合并 |
| symbol / contract | 部分行内、部分路径推导 | 保留 identity source |
| trading_date | unavailable/pending | 不从自然日静默推断 |
| session | unavailable/pending | 未配置时不显示 AM/PM/night 语义 |
| timezone | pending | API 返回 `null` 和 warning |
| bar timestamp 是 start/end | pending | 保存 raw datetime 和 pending 状态 |
| tick size / multiplier | unavailable | 未来 metadata 接入；不能由价格小数位猜测 |
| bid/ask、五档 | unsupported | 不生成盘口图 |
| mid、spread、depth、imbalance、microprice | unsupported | 不以 close/high/low/volume 替代 |
| snapshot detail / 5 秒 asof | unsupported | 改为 bar detail；未来有真实 L2 才启用新 capability |
| 因子与回测正式输出 | no data | 研究审计页显示空状态 |

---

## 4. 旧需求迁移与冲突处理

状态定义：

- `retain`：功能可直接保留；
- `redesign`：目的保留，按当前数据重做；
- `degraded`：保留研究目的，但当前表达能力下降；
- `pending`：接口或状态可设计，依赖尚未确认；
- `unsupported`：当前输入无法提供；
- `remove`：不进入 Recipe。

| 旧需求 | 状态 | Recipe 去向 |
| --- | --- | --- |
| 三页顶部导航 | retain | 改名为市场路径、数据语义、研究审计，仍只有三页 |
| 研究笔记/交易工作台风格 | retain | 使用紧凑信息层级、语义徽标和响应式布局 |
| 快照表、成交表共同驱动盘口页 | unsupported | 当前只有 bar CSV；不创建 snapshot adapter |
| 日期、合约和分钟选择 | redesign | 改为数据族、交易所、品种、资产、频率和时间范围选择 |
| 1 分钟 OHLC 蜡烛图 | retain | 当前可实现；查询所选资产和有限时间范围 |
| 5 秒 mid 曲线 | unsupported | 不显示；可选叠加线只能明确命名为 `close` |
| AM/PM 同轴和午间处理 | pending | 真实 session 规则未确认；先使用 raw timestamp，配置日历后再提供 session 标记 |
| 拖动、缩放、tooltip | retain | 使用 K 线图的 zoom/pan/tooltip |
| 点击蜡烛打开该分钟 | redesign | 打开 Bar Inspector，而不是 snapshot detail |
| 点击判定同时考虑 x/y 价格范围 | redesign | 图表库使用真实 candle item selection；不得只按时间 nearest 强制选择 |
| 分钟内所有 snapshot | unsupported | 当前没有；显示单根 bar 原始/规范化字段与前后 bar |
| bid/ask 五档横向挂单量 | unsupported | 不显示空造盘口；显示 capability 说明 |
| mid、last、spread、imbalance tooltip | unsupported | 替换为 OHLC、volume、raw amount/money、position/OI、symbol |
| 右侧前后 K 线和返回整日 | retain/redesign | Bar Inspector 提供前后 N 根 context 和返回选定范围 |
| quote state 与成交事实语义提示 | retain | 改为 bar 语义提示，并保留未来 L2 的概念说明 |
| 数据 Tree 中心语义树 | retain | 重做为 Catalog Tree + Field Inspector |
| 成交事实、盘口、持仓、聚合、派生、不可观测分支 | redesign | 改为资产身份、价格 bar、活动字段、持仓字段、时间/连续性、当前不可观测 |
| 字段经济身份、聚合动作、示例、边界 | retain | Field Inspector 的核心内容 |
| 盘口聚合规则 | unsupported/pending | 作为未来能力说明；不对当前 bar 应用 |
| 价格 OHLC、volume sum、OI last | pending | 作为语义说明；不执行重采样，且 amount/position 的供应商语义未确认 |
| 不可观测：撤单、队列、隐藏流动性等 | retain | 明确列在 capability matrix |
| 固定 shortlist 数量 | remove | shortlist 为可选研究输出；无数据时不显示空表或虚假条目 |
| 写死 current RSI / legacy RSI | remove | 不写死任何因子；使用 namespaced research identity |
| current/legacy 数据隔离目的 | retain | 扩展为 source/project/run/factor/policy/version 全身份隔离 |
| 累计 real PnL 曲线 | pending | 仅真实 `daily_pnl` 存在时显示；缺失时显示 no data |
| 固定 ask/bid fill 执行口径 | unsupported | 当前无 bid/ask；只展示上游 manifest 声明的执行假设 |
| 动态 policy checkbox 和图例 | retain | 从真实 run manifest 和 policy metadata 生成 |
| shortlist 三分类和排名 | pending | 仅在真实 shortlist 文件存在时启用；分类由上游提供 |
| 因子公式、lookback、trigger | retain | 从 factor metadata 展示，不写死 RSI |
| Entry Example | retain/pending | 只使用上游 entry context 和匹配的行情；不展示未来退出解释 |
| Trade Audit 指标与拆解 | retain/pending | 从真实 summary/trades/breakdown 加载，并做一致性核验 |
| 动态 PnL Matrix | retain/pending | 行列来自真实 factor/policy 并集；不存在的组合显示 `null`/`—` |
| `/api/day`、`/api/session` | redesign | 使用通用 asset/time-range bars API；session 未确认前不提供伪 session |
| 单一巨大 `/api/strategy` | redesign | 拆为 run manifest、PnL、summary、trades 等按需 API |
| mtime 自动刷新研究输出 | retain/redesign | 使用 file signature + 显式 catalog/research refresh，不在 import 时永久缓存 |
| 前端本地 fallback 到固定端口 | remove | 同源部署；host/port 仅后端配置 |
| 原生前端与 Canvas | retain/redesign | 原生 ES modules；K 线使用单一 Canvas 图表库，语义页面使用可访问 DOM |
| 旧目录和旧文件名清单 | remove | 使用新的轻量目录，不机械迁移 |

### 4.1 采用当前事实而放弃旧实现的冲突

1. 旧页面要求 L2，当前只有 bar：采用当前数据，盘口页重构为市场路径页。
2. 旧页面把 close 以外的 mid/quotes 作为核心，当前不存在：不做代理字段。
3. 旧策略页假定 factor registry、signals、trades 和 PnL 已存在，当前没有正式输入：研究页先实现 contract-aware empty shell。
4. 旧需求写死 RSI 和 legacy IDs，新 Recipe 必须通用于未来真实项目：保留隔离原则，删除具体 ID。
5. 旧需求按自然交易日和 AM/PM 组织，当前数据未提供 session/trading_date：保持 pending，不猜测。

---

## 5. 总体技术架构

### 5.1 形态

使用一个本地单体应用：

```text
浏览器静态前端
      |
      v
同源 JSON API
      |
      +--> SQLite metadata catalog
      +--> Market CSV adapter（按需读一个 canonical 文件）
      +--> Research output adapter（按需读一个 run）
```

不使用微服务、消息队列、远程数据库、全局插件系统或复杂依赖注入。

### 5.2 建议技术栈

- 后端：Python + FastAPI。
- 行情读取：Polars lazy CSV scan；只投影所需列并限制时间范围。
- Catalog：Python 标准库 SQLite 单文件。
- 前端：原生 HTML/CSS/JavaScript ES modules，不使用 React/Vue 等 SPA 框架。
- 图表：Apache ECharts，默认 Canvas renderer；只引入项目使用的 candlestick、line、bar、dataZoom、tooltip 等组件。
- 部署：FastAPI 同源提供 `/api/v1/...` 和静态前端。

选型依据：

- FastAPI 可挂载静态目录，适合单进程同源 API 与前端：[FastAPI Static Files](https://fastapi.tiangolo.com/tutorial/static-files/)。
- Polars 的 `scan_csv` 提供延迟执行和投影/查询优化，适合选中文件的按需读取：[Polars lazy file usage](https://docs.pola.rs/user-guide/lazy/using/)、[Polars CSV scan](https://docs.pola.rs/user-guide/io/csv/)。
- SQLite 是无需独立服务进程的轻量磁盘数据库，适合本地 catalog：[Python sqlite3](https://docs.python.org/3/library/sqlite3.html)。
- ECharts 原生支持 candlestick、dataZoom 及 Canvas/SVG renderer；Canvas 适合较多图形元素：[ECharts option](https://echarts.apache.org/en/option.html)、[Canvas vs SVG](https://echarts.apache.org/handbook/en/best-practices/canvas-vs-svg/)。

实施时必须固定经过验证的依赖版本和 lock 文件；本文不指定具体版本号。

### 5.3 数据源与前端解耦

- 行情绝对根路径只出现在后端配置或环境变量。
- Catalog 给前端返回 opaque `asset_id`、相对来源身份和 capability。
- 前端不拼接文件路径，不猜 schema，不解析 CSV。
- 更换行情根目录或增加 research source 时，只重建后端 catalog/manifest，不改核心前端。

---

## 6. 三类核心功能的最终设计

## 6.1 市场路径（Market Explorer）

### 目标

检查当前真实 bar 路径、成交活动、持仓字段、连续合约切换和单根 bar 的来源，不模拟盘口。

### 页面布局

#### 顶部过滤栏

- 数据族：主要合约 / 全部合约 / 指数；
- 交易所；
- 品种；
- 资产：
  - continuous future；
  - single futures contract；
  - cash index；
- frequency；
- 时间范围；
- “加载”按钮；
- catalog revision、数据状态和 warning 徽标。

过滤器逐级从 Catalog API 获取合法选项，不能由前端维护静态品种表。

#### 主图

- OHLC candlestick；
- volume 子图；
- raw amount/money 子图，可关闭；
- raw position 或 open_interest 子图，可关闭；
- 可选 close line，标签必须写 `close`；
- zoom、pan、reset、tooltip；
- 默认限制返回 bar 数，过宽范围提示缩小查询。

#### 时间轴

- 默认使用真实解析 timestamp，保留实际时间间隔。
- 可以提供“压缩非交易时段”显示模式，但必须标记为 visual compression。
- 在 trading_date/session 尚未确认时，不显示“上午/下午/夜盘”标签。
- 不在缺失时段用直线制造不存在的价格路径。

#### 连续合约标记

主要合约文件中的 row-level `symbol` 变化应显示为 contract-change marker。

仅陈述“观察到 symbol 改变”；在主力规则和复权语义未确认前：

- 不称为官方换月规则；
- 不计算 roll adjustment；
- 不隐藏切换跳变；
- 不把连续序列和单合约合并。

#### Bar Inspector

点击 candle 后显示：

- raw datetime；
- timestamp parse 状态；
- OHLC；
- volume；
- raw `amount` 或 `money`；
- raw `position` 或 `open_interest`；
- row-level symbol 或 path-derived contract；
- source schema；
- source identity；
- 前后 N 根 bar；
- warnings：timezone、timestamp semantics、trading_date、session、字段语义 pending。

不显示 bid/ask、mid、spread、depth、imbalance 或 microprice。

### 页面固定语义提示

```text
OHLC 是时间 bar 内的价格摘要，不包含 bar 内完整路径顺序。
close 不是 mid，high/low 不是 bid/ask。
volume 不是订单簿深度，无法区分成交、撤单和挂单变化。
自然日不一定等于期货 trading_date。
主要合约 symbol 变化可被观察，但选主和复权规则尚未确认。
```

## 6.2 数据语义（Data Atlas）

### 目标

让用户理解“有哪些数据、如何定位、字段是什么、哪些语义已确认、哪些能力不存在”。

### 页面布局

#### 左侧 Catalog Tree

```text
数据族
  └─ frequency
      └─ exchange
          └─ product
              └─ continuous / contract / index
```

Tree 支持搜索、展开、数量统计和状态徽标。隐藏 checkpoint 和 suspected alias 默认不显示，可在“异常路径”筛选中查看。

#### 中部 Asset / Schema 面板

- 资产身份；
- canonical relative path；
- family/frequency/exchange/product/contract；
- asset kind；
- schema ID；
- exact header fingerprint；
- field-set fingerprint；
- 文件大小和 mtime；
- 首尾 raw timestamp；
- capability；
- alias、parse warning、stale 等状态。

前端不显示行情绝对根路径。

#### Schema Compare

允许选择两个 asset/schema 比较：

- 共有字段；
- 仅左侧/仅右侧字段；
- 同义候选：amount vs money、position vs open_interest；
- 列顺序差异；
- row symbol vs path-derived symbol；
- semantic status。

比较只展示，不自动声明同义或执行字段合并。

#### Field Inspector

每个字段显示：

- raw field name；
- normalized display name；
- 来源 schema；
- 样本推断 dtype；
- economic identity；
- identity status：confirmed / pending / unsupported；
- 可用的展示或聚合语义；
- 示例值；
- 缺失规则；
- 为什么重要；
- 不可推断事项；
- 后续需确认的问题。

#### Capability Matrix

显示：

- available：OHLC、volume 等；
- partial：OI、symbol；
- pending：timezone、session、timestamp semantics、amount/position；
- unsupported：L1/L2、snapshot、order flow；
- no data：research outputs。

### 聚合说明

Recipe 默认读取已有频率，不在页面临时重采样。

语义说明可以记录：

- price：open=first、high=max、low=min、close=last；
- volume/notional：只有确认其为区间 flow 后才可 sum；
- OI/state：通常取 last，但当前 `position` 语义待确认；
- categorical symbol：不能平均；
- Level2 state：未来只能 as-of/last/median/duration，不可当成交量相加。

这些规则属于说明和未来 adapter contract，不授权 Recipe 在当前阶段计算新频率。

## 6.3 研究审计（Research Audit）

### 目标

展示并核验外部研究项目已经产出的结果。Recipe 不规定因子算法，也不生成结果。

### 无研究输出时

页面必须正常打开并显示：

```text
No research outputs configured.
Recipe has market data, but no factor/backtest run is registered.
Add a valid research manifest and refresh the research catalog.
```

同时显示：

- 当前期望的 manifest schema version；
- research source 配置位置；
- contract 文档入口；
- `no_data` 状态；
- 不显示零 PnL、空 shortlist 排名或虚假示例。

### 有研究输出时

#### 选择器

- research source；
- project；
- run；
- data split；
- factor；
- policy；
- data revision。

所有选择项来自 manifest 和 metadata。

#### 数据隔离徽标

页面始终显示复合身份：

```text
source_id / project_id / run_id / data_revision /
factor_id@factor_version / policy_id@policy_version
```

同名 display name 不构成同一 factor。任何 join 都使用复合 ID。

#### PnL 区域

- 只在真实 daily PnL 存在时显示；
- 支持 gross、fees、net 和 cumulative；
- 若 cumulative 由真实 daily net PnL 前端累加，标记 `derived_for_display`；
- policy 图例动态生成；
- 缺少某 policy 曲线显示 `null`/`—`；
- 不以零线代替缺失数据。

#### Summary 与 Breakdown

- 核心 summary cards；
- long/short；
- exit reason；
- split；
- 其他上游定义 dimension；
- 每个 breakdown 显示样本数、win rate、net PnL、平均持仓等实际存在字段；
- 缺失 metric 不补零。

Recipe 可以做展示一致性检查，例如：

- trade net PnL 求和是否与 summary 接近；
- daily PnL 求和是否与 summary 接近；
- trade 数是否一致；
- ID、split、policy 是否引用存在。

这些是 audit checks，不是重新回测；差异只报告，不静默覆盖上游结果。

#### Signals / Predictions / Decisions 时间线

若对应文件存在：

- 以 `event_id`/`decision_id` 对齐；
- 显示 `anchor_time`、`emitted_at`、`information_cutoff`、`predicted_at`、`decision_time`；
- formation 或 post-processing metadata 存在时，显示 `formation_start`、`formation_end`、`parent_event_ids` 和 `postprocess_id`；
- 未配置 post-processing 是合法状态；不能把缺少 `postprocess_id` 解释为数据错误，也不能假定所有项目都做 clustering；
- feature、label 和 execution 各自显示 `reference_time_kind` 与解析后的 `reference_time`，允许值为 `anchor_time`、`emitted_at` 或项目声明的 custom reference；
- retrospective 结果不得描述为 anchor 时已实时可交易；
- 实时 Decision 应满足 `decision_time >= emitted_at`；
- 缺失生命周期字段时显示 schema warning。

#### 方向坐标审计

Recipe 只展示并验证上游声明，不执行方向转换：

- 每个可能带方向符号的 feature/label 字段都从字段 schema 读取 `coordinate_state`：`unsigned`、`raw_signed` 或 `event_aligned`；
- 已转换记录必须同时带 `event_id` 和 `direction_transform_id`；
- 若转换记录声明 `raw_signed -> event_aligned` 以外的状态变化，标记 contract error；
- 对 `event_aligned` 二次转换、对 `unsigned` 转换、`direction=null` 时转换，均标记 contract error；
- Recipe 不按字段名猜坐标，不静默乘 direction，也不在不同 artifact join 时自动统一方向；
- 缺少方向 schema 时显示 `pending_schema`，不能把数值默认解释为已按事件方向对齐。

#### Trade Audit

- 分页 trade table；
- entry/exit、side、quantity、price source、gross、fees、net、exit reason；
- 执行假设卡从 policy/manifest 读取；
- 若 fill model 是 bar proxy，必须明确；
- 当前行情无 bid/ask，不能把外部未声明结果展示为盘口可执行。

#### Entry Example

- 只解释入场；
- 需要上游提供 entry reason、score、trigger 和 market reference；
- 可加载精确匹配的行情 revision/asset/frequency；
- 不使用未来 exit、PnL、stop/take-profit 结果解释入场；
- 行情 revision 不匹配时显示 `market_reference_mismatch`，不强行拼图。

#### Shortlist 与 Matrix

- shortlist 是可选上游文件，不固定数量或 RSI；
- Matrix 列来自 factor/policy 实际并集；
- 未评估组合显示 `null`/`—`，不显示 0；
- 点击 shortlist 行只改变当前 run/factor/policy 选择，不执行研究。

---

## 7. Catalog 设计

### 7.1 Catalog 的职责

Catalog 只存元数据，不复制 31.4 GiB CSV 内容：

- 文件发现；
- 路径解析；
- canonical/alias；
- asset identity；
- schema/header；
- capabilities；
- 文件签名；
- 首尾 raw timestamp；
- 状态和 warning。

### 7.2 本地存储

使用：

```text
recipe/var/catalog.sqlite
```

该文件是可删除、可重建的本地缓存，不是行情事实源。不得把它放回行情目录。

建议表：

#### `catalog_meta`

- `schema_version`
- `catalog_revision`
- `built_at`
- `market_root_signature`
- `scan_mode`
- `file_count`
- `warning_count`

#### `files`

- `file_id`
- `relative_path`
- `family`
- `frequency`
- `exchange_raw`
- `exchange_canonical`
- `product_raw`
- `product_canonical`
- `contract_raw`
- `contract_canonical`
- `asset_kind`
- `size_bytes`
- `mtime_ns`
- `header_text`
- `header_fingerprint`
- `field_set_fingerprint`
- `first_raw_datetime`
- `last_raw_datetime`
- `status`
- `canonical_file_id`
- `warning_json`

#### `assets`

- `asset_id`
- `family`
- `frequency`
- `exchange`
- `product`
- `contract`
- `asset_kind`
- `canonical_file_id`
- `schema_id`
- `capability_json`
- `semantic_status_json`

#### `schemas`

- `schema_id`
- `ordered_fields_json`
- `field_set_json`
- `sample_dtype_json`
- `source_count`
- `status`

#### `field_semantics`

- `schema_id`
- `raw_field`
- `display_name`
- `economic_identity`
- `semantic_status`
- `aggregation_note`
- `missing_note`
- `warning`

### 7.3 Stable identity

建议 opaque ID 由规范化业务键和 schema version 确定性生成：

```text
asset_id = hash(
  family,
  frequency,
  exchange,
  product,
  contract_or_continuous,
  asset_kind
)
```

不能使用 catalog row number。

### 7.4 Path parser

Path parser 必须：

1. 区分主要合约、全部合约和指数；
2. 区分分钟路径和高周期路径；
3. 保存 raw identity 和 canonical identity；
4. 保留 CZCE 等不同合约编码长度，不擅自补世纪；
5. 排除隐藏目录和 `.DS_Store`；
6. 检测额外层级；
7. 把 134 个 IC nested 文件标记 suspected alias；
8. 对未知路径输出 `unclassified`，不猜测。

### 7.5 Schema fingerprint

同时保存：

- order-sensitive `header_fingerprint`；
- order-insensitive `field_set_fingerprint`。

这样可以区分全部合约日线与周/月/季度的列顺序差异，同时识别它们字段集合相同。

### 7.6 增量刷新

Catalog refresh 是显式维护操作：

1. 完整枚举相对路径；
2. 比较 `(relative_path, size_bytes, mtime_ns)`；
3. 未变化文件复用旧 catalog；
4. 新增/变化文件读取表头和首尾边界；
5. 消失文件标记 missing，确认后再从 catalog 移除；
6. 重算 alias 和 asset identity；
7. 原子替换 catalog revision。

禁止：

- 每次服务启动完整打开 86,397 个 CSV；
- 每个 API 请求重扫目录；
- 模块 import 时加载 catalog 或行情全部内容；
- 以 root directory mtime 代替递归变化检查。

若 catalog 不存在，服务仍可启动，但 Catalog/Market 页面显示 `catalog_unavailable` 和构建命令。

---

## 8. Market CSV Adapter

### 8.1 输入

Adapter 只接受 Catalog 已解析且 canonical 的 `asset_id`。API 不接受用户传入绝对路径或任意相对路径。

### 8.2 规范化 BarRecord

```text
asset_id
source_file_id
family
asset_kind
frequency
exchange
product
contract
source_symbol
symbol_source: row | path | configured
raw_datetime
timestamp
timezone
timestamp_semantics
trading_date
session_id
open
high
low
close
volume
activity_value
activity_raw_field: amount | money | null
position_value
position_raw_field: position | open_interest | null
semantic_status
warnings
```

### 8.3 字段映射规则

- 所有读取按字段名。
- `amount` 和 `money` 都可放入 `activity_value`，但保留 `activity_raw_field`，并在单位未确认时标记 pending。
- `position` 不自动重命名为 open interest。
- 明确 `open_interest` 可以展示为供应商字段，但不自动与 `position` 比较或合并。
- 全部合约分钟 symbol 从路径推导，并标记 `symbol_source=path`。
- 主要合约 symbol 从行读取。
- 指数 identity 从后端配置和文件身份得到。

### 8.4 datetime

Adapter 至少支持样本中观察到的：

- `YYYY-MM-DD HH:MM:SS`
- `YYYY-MM-DD`
- `YYYY/M/D`

必须：

- 保留 raw datetime；
- 解析失败返回行级 error 或跳过策略报告；
- timezone 未配置时返回 `null`；
- bar start/end 未确认时返回 `timestamp_semantics=pending`；
- trading_date/session 未配置时返回 `null`；
- 不按自然日期静默生成 trading_date。

### 8.5 读取策略

- 使用 lazy CSV scan；
- 只读取请求所需字段；
- 每次查询只解析一个 canonical 文件；
- 必须有 `start/end` 或受限默认窗口；
- 必须有最大 bar 数；
- 超限返回可操作错误，要求缩小范围；
- 不跨多个合约自动拼接；
- 不把主力连续和单合约自动 union；
- 默认不重采样。

CSV 没有时间索引，predicate 可能仍需要扫描选中文件。若性能验收失败，再在独立 Phase 评估日级 byte-offset index 或 canonical Parquet cache；不能预先把全库转换为另一份 31 GiB 数据。

### 8.6 数据质量

Adapter 可以报告但不修复：

- parse errors；
- non-finite 数；
- OHLC 基本关系异常；
- timestamp duplicate / non-monotonic；
- symbol switch；
- requested field missing。

Recipe 不是清洗平台。异常必须通过 warnings/API 状态暴露。

---

## 9. 后端 API

统一前缀：

```text
/api/v1
```

### 9.1 通用响应

成功响应：

```json
{
  "data": {},
  "meta": {
    "catalog_revision": "…",
    "request_id": "…"
  },
  "warnings": [],
  "status": "ok"
}
```

空/降级响应：

```json
{
  "data": null,
  "meta": {},
  "warnings": [
    {
      "code": "research_no_data",
      "message": "No research outputs configured."
    }
  ],
  "status": "no_data"
}
```

要求：

- UTF-8 JSON；
- 所有 NaN、Infinity、-Infinity 转为 `null` 并附 warning；
- 日期使用明确字符串，timezone 未知时不能加伪 offset；
- 列表 API 使用 cursor 或明确分页；
- 不返回绝对行情路径；
- 参数有长度、范围和枚举校验。

### 9.2 Health 与状态

```text
GET /api/v1/health
GET /api/v1/status
```

状态包括：

- service；
- catalog；
- market root；
- research sources；
- cache；
- current revisions；
- warnings。

### 9.3 Catalog API

```text
GET /api/v1/catalog/summary
GET /api/v1/catalog/assets
GET /api/v1/catalog/assets/{asset_id}
GET /api/v1/catalog/schemas
GET /api/v1/catalog/schemas/{schema_id}
GET /api/v1/catalog/fields/{schema_id}
GET /api/v1/catalog/anomalies
```

`assets` 支持：

- family；
- frequency；
- exchange；
- product；
- asset_kind；
- status；
- search；
- cursor；
- page_size。

### 9.4 Market API

```text
GET /api/v1/market/bars
GET /api/v1/market/context
```

`bars` 参数：

```text
asset_id
start
end
fields
limit
```

`context` 参数：

```text
asset_id
timestamp
before
after
```

API 返回：

- bars；
- field map；
- source identity；
- semantic status；
- time warnings；
- truncation/limit metadata。

### 9.5 Research API

```text
GET /api/v1/research/status
GET /api/v1/research/runs
GET /api/v1/research/runs/{run_id}
GET /api/v1/research/runs/{run_id}/factors
GET /api/v1/research/runs/{run_id}/policies
GET /api/v1/research/runs/{run_id}/pnl
GET /api/v1/research/runs/{run_id}/summary
GET /api/v1/research/runs/{run_id}/breakdowns
GET /api/v1/research/runs/{run_id}/trades
GET /api/v1/research/runs/{run_id}/timeline
GET /api/v1/research/runs/{run_id}/entry-examples
GET /api/v1/research/runs/{run_id}/shortlist
GET /api/v1/research/runs/{run_id}/audit
```

所有子端点按需读取，不能把全部 trades、curves 和 examples 塞进单个巨大响应。

### 9.6 Refresh

建议维护入口：

```text
python -m recipe.catalog refresh
python -m recipe.research_catalog refresh
```

可选本地管理 API：

```text
POST /api/v1/admin/catalog/refresh
POST /api/v1/admin/research/refresh
```

默认只监听 localhost；若允许非本地访问，管理 API 默认关闭。Recipe 不因此建设账户系统。

### 9.7 HTTP 状态

| 情况 | HTTP | Recipe status |
| --- | ---: | --- |
| 正常 | 200 | ok |
| 合法但无数据 | 200 | no_data |
| 字段不支持 | 200 或 422 | unsupported |
| 语义待确认但可展示 raw | 200 | pending |
| 参数非法 | 422 | error |
| asset/run 不存在 | 404 | error |
| catalog 尚未构建 | 503 | catalog_unavailable |
| 请求范围过大 | 413 或 422 | range_too_large |
| 文件变化导致 catalog stale | 409 | stale |

---

## 10. 缓存、刷新与性能

### 10.1 Catalog 缓存

- SQLite 是持久元数据缓存。
- 启动只读取 catalog meta，不打开全部 CSV。
- 显式 refresh 才做递归目录检查。
- refresh 使用新临时 SQLite 后原子替换，避免半成品 catalog。

### 10.2 查询缓存

使用有界内存 LRU：

```text
cache key =
  asset_id +
  file(size, mtime_ns) +
  query(start, end, fields, limit) +
  adapter_schema_version
```

要求：

- 有最大条目和最大字节；
- 文件签名变化立即失效；
- 不把旧 DataFrame 永久保存在模块全局；
- 不缓存 error/no-data 为永久状态；
- API 可返回 ETag；
- 浏览器刷新可以复用未变化响应，但不能掩盖 catalog revision 变化。

### 10.3 Research 缓存

cache key 包含：

```text
research_source_id
run_id
manifest signature
requested artifact signature
query params
```

更换真实研究输出后：

1. refresh research catalog；
2. 浏览器重新请求；
3. 不需要修改前端；
4. 只有服务代码变化才重启。

### 10.4 性能预算原则

- 浏览器只接收当前视图所需数据；
- trade table 分页；
- Catalog Tree 分层请求或分页；
- PnL/summary 不与全部 trades 同响应；
- 默认单图 bar 上限在实现 Phase 通过性能测试确定；
- 不在启动时读取 31.4 GiB 逻辑数据；
- 不承诺 CSV 时间过滤具备索引级速度。

---

## 11. 数据缺失、空状态与降级

| 场景 | API 状态 | 页面行为 |
| --- | --- | --- |
| Catalog 未构建 | catalog_unavailable | 三页可打开；显示构建命令 |
| 行情根目录不存在 | unavailable | 市场页无图；数据页显示配置错误 |
| asset 无指定字段 | unsupported | 隐藏对应子图并解释缺失 |
| timezone/session pending | pending | 展示 raw timestamp，不生成 session |
| position 语义 pending | pending | 以 raw_position 展示 |
| alias path | warning | 默认隐藏 alias，仅异常页显示 |
| CSV parse error | error/partial | 返回已加载数据和明确错误范围，或失败，不静默丢弃 |
| no research source | no_data | 研究页显示 contract-aware 空状态 |
| manifest 存在但 artifact 缺失 | partial | 只显示可用模块，缺失模块明确标记 |
| daily PnL 缺失 | no_data | 不画零线 |
| factor 无某 policy | no_data | Matrix 显示 `—` |
| entry market revision 不匹配 | mismatch | 不叠加行情，显示原因 |
| non-finite JSON | warning | 输出 `null`，记录字段和行数 |

前端必须把 `no_data`、`unsupported`、`pending`、`unavailable` 和 `error` 视觉区分，不能统一显示为“加载失败”。

---

## 12. 因子与回测输出契约

## 12.1 Research Source

后端配置零个或多个只读 research root。每个 source 有：

```text
research_source_id
display_name
root_path
source_kind
enabled
```

绝对 root 不返回前端。

### 12.2 Run 目录

建议每个 run：

```text
<RESEARCH_ROOT>/<project_id>/<run_id>/
  manifest.json
  factors.parquet|csv                 # factor metadata
  feature_schema.json                 # 可选，字段级坐标/类型声明
  label_schema.json                   # 可选，字段级坐标/类型声明
  policies.parquet|csv
  events.parquet|csv                 # 可选
  signals.parquet|csv                # 可选
  predictions.parquet|csv            # 可选
  decisions.parquet|csv              # 可选
  trades.parquet|csv                  # 可选
  daily_pnl.parquet|csv               # 可选
  summary.parquet|csv                 # 可选
  breakdowns.parquet|csv              # 可选
  entry_examples.parquet|csv          # 可选
  shortlist.parquet|csv               # 可选
```

Recipe 不要求所有文件存在；manifest 必须声明 availability。

### 12.3 `manifest.json`

最小字段：

```json
{
  "schema_version": "recipe-research-v1",
  "research_source_id": "configured-by-backend",
  "project_id": "pathpulse",
  "run_id": "unique-run-id",
  "run_version": "semantic-version-or-revision",
  "created_at": "ISO-8601",
  "data_revision": "upstream-data-revision",
  "market_reference": {
    "source_id": "market-source",
    "asset_ids": ["opaque-asset-id"],
    "frequency": "1min",
    "timezone": null,
    "timestamp_semantics": "pending"
  },
  "splits": ["dev", "holdout"],
  "artifacts": {
    "factors": {"path": "factors.parquet", "status": "available"},
    "trades": {"path": "trades.parquet", "status": "available"},
    "daily_pnl": {"path": null, "status": "no_data"}
  },
  "execution_assumptions": {
    "price_source": "next_bar_open_proxy",
    "fee_model_id": "project-defined",
    "slippage_model_id": "project-defined"
  }
}
```

Recipe 验证 manifest，不替上游补字段或创建结果。

### 12.4 身份与命名空间

唯一引用至少包含：

```text
research_source_id
project_id
run_id
run_version
data_revision
factor_id + factor_version
policy_id + policy_version
```

禁止：

- 按 display name 合并因子；
- 把不同 run 的同名 policy concat；
- 自动把 current/legacy 当作同一数据；
- 复用旧 RSI ID 作为默认值。

### 12.5 Factor metadata

最小字段：

```text
factor_id
factor_version
display_name
category
description
formula_text
input_fields
lookback
trigger
confirmation_window
reference_time_kind
output_schema_ref
availability
```

`formula_text` 只展示，不执行。

若存在可展示的 feature/label values，其字段 schema 至少逐字段声明：

```text
field_name
value_type
nullable
coordinate_state       # unsigned | raw_signed | event_aligned
description
```

值记录通过 `event_id` 连接；由方向转换产生的记录还必须提供
`direction_transform_id`。Recipe 不根据 display name、字段名或正负值猜测
`coordinate_state`。

### 12.6 Policy metadata

最小字段：

```text
policy_id
policy_version
display_name
decision_rule_text
execution_rule_text
entry_price_source
exit_price_source
fee_model_id
slippage_model_id
max_hold
stop
target
session_rule
availability
```

### 12.7 Events / Signals / Predictions / Decisions

建议字段：

```text
event_id
asset_id
anchor_time
emitted_at
information_cutoff
formation_start
formation_end
direction
parent_event_ids
postprocess_id
factor_id
factor_version
signal_value
score
trigger
model_id
predicted_at
prediction
probabilities
decision_id
decision_time
action
policy_id
policy_version
reference_time_kind
reference_time
split
```

每个文件只保留适用字段。Recipe 校验：

- stable ID；
- 引用存在；
- `formation_start`、`formation_end`、`parent_event_ids` 和 `postprocess_id` 为可选；
- 无 post-processing 是合法 passthrough，不要求 clustering；
- `emitted_at >= information_cutoff`；
- 实时 `decision_time >= emitted_at`；
- feature、label、execution 各自声明并保存实际 `reference_time_kind`/`reference_time`；
- probabilities 为有限数或 null；
- 不把 retrospective anchor result 表述为 anchor 时可交易。

### 12.8 Trades

最小字段：

```text
trade_id
decision_id
event_id
asset_id
policy_id
policy_version
split
side
quantity
entry_time
entry_price
entry_price_source
exit_time
exit_price
exit_price_source
exit_reason
gross_pnl
fees
slippage_cost
net_pnl
holding_seconds
```

### 12.9 Daily PnL

```text
run_id
factor_id
factor_version
policy_id
policy_version
split
date
gross_pnl
fees
slippage_cost
net_pnl
cumulative_net_pnl   # 可选
```

若 cumulative 缺失，Recipe 可以从真实 `net_pnl` 为展示临时计算，但必须标记为 display-derived，不能回写上游文件。

### 12.10 Summary

采用 long-form：

```text
run_id
factor_id
factor_version
policy_id
policy_version
split
metric_name
metric_value
unit
scope
```

Recipe 可识别一组核心 metric，但必须保留额外 metric，不硬编码只有旧 Trade Audit 列。

### 12.11 Breakdowns

```text
dimension
dimension_value
n_trades
win_rate
gross_pnl
fees
net_pnl
avg_holding_seconds
```

### 12.12 Entry Examples

```text
example_id
event_id
decision_id
asset_id
market_data_revision
frequency
window_start
window_end
entry_time
side
score
trigger
reason_text
uses_future_exit
```

必须满足 `uses_future_exit=false`。Recipe 不从 trade exit 反向生成 reason。

### 12.13 Audit 输出

Recipe 的 audit result 是临时/缓存状态：

```text
check_id
severity
status
expected
observed
difference
source_artifact
```

它不修改研究结果。

---

## 13. 前端结构与交互原则

### 13.1 App Shell

- 单一 `index.html`；
- hash routes：`#/market`、`#/data`、`#/research`；
- 三项固定导航；
- 共享 API client、status banner、loading/error/empty components；
- 每个 view 独立 ES module；
- 不引入全局 mutable store；只保存最小 URL/query state。

### 13.2 视觉语言

- 研究工作台，不做营销首页；
- 中性深浅色变量、清晰网格、紧凑表格；
- confirmed/pending/unsupported/no-data/error 使用一致徽标；
- 数值 tooltip 带 raw field 和单位状态；
- 支持桌面和窄屏；
- 表格键盘可访问；
- 图表有文字摘要和空状态，不只依赖颜色。

### 13.3 图表

- K 线、volume、OI/PnL 使用 ECharts Canvas；
- DOM 负责 Catalog Tree、Field Inspector、表格和状态说明；
- 图表数据量由 API 限制；
- resize 使用 `ResizeObserver`；
- 页面切换时释放 chart instance；
- tooltip 不展示不存在字段；
- no-data 时不初始化假曲线。

### 13.4 URL 状态

可分享的选择写入 hash query：

```text
#/market?asset_id=...&start=...&end=...
#/research?run_id=...&factor_ref=...&policy_ref=...
```

URL 不包含绝对路径。

---

## 14. 建议的后续项目目录

本阶段不要创建。实施时按 Phase 渐进建立：

```text
recipe/
  pyproject.toml
  README.md
  config/
    recipe.example.toml
  src/
    recipe/
      __init__.py
      app.py
      settings.py
      catalog.py
      schemas.py
      adapters/
        market_csv.py
        research_output.py
      services/
        market.py
        semantics.py
        research.py
      api/
        health.py
        catalog.py
        market.py
        research.py
  static/
    index.html
    css/
      app.css
    js/
      app.js
      router.js
      api.js
      state.js
      views/
        market.js
        data_atlas.js
        research.js
      components/
        status.js
        chart.js
        table.js
    vendor/
      echarts/
  semantics/
    fields.yaml
  tests/
    test_catalog.py
    test_market_adapter.py
    test_api.py
    test_research_contract.py
    test_json_safety.py
  var/                    # gitignored runtime data
    catalog.sqlite
    cache/
```

原则：

- 不迁移旧可视化文件名；
- 不创建无用途的模块；
- `var/` 可删除重建；
- 行情和 research root 不位于 Recipe 项目内；
- `recipe.example.toml` 不包含本机绝对路径；
- 本机实际路径通过未提交配置或环境变量注入；
- 不建设插件系统或复杂前端构建链。

---

## 15. 分阶段实施计划

后续 Codex 可以只执行一个 Phase。未明确授权下一 Phase 时必须停止。

## Phase 0：规格与数据理解

- 依赖：无。
- 输入：
  - 旧 `可视化.md`
  - `current_state_audit.md`
  - 当前行情目录
  - architecture/legacy blueprint
- 输出：
  - `/Users/kangbohang/Desktop/start/salt01/recipe.md`
- 允许读取：
  - 上述资料和行情目录；
  - 与 Recipe 直接相关的只读说明。
- 允许写入：
  - 仅 `recipe.md`。
- 验收：
  - 三类业务明确；
  - 完整目录事实、抽样 schema 和旧迁移均记录；
  - 无网页、服务、回测或 Recipe 目录。
- 不处理：
  - 正式实现和全库 schema catalog。

## Phase 1：工程骨架与 Catalog

- 依赖：Phase 0 确认。
- 输入：
  - 本规格；
  - 行情根配置；
  - 目录路径模式。
- 输出：
  - 最小 Python 工程；
  - settings；
  - SQLite catalog builder；
  - health/catalog API；
  - path parser 和 schema fingerprint；
  - Catalog/Data Atlas 的基本空壳。
- 允许读取：
  - 行情目录元数据和 CSV 表头/边界；
  - 本规格。
- 允许写入：
  - `recipe/`；
  - `recipe/var/catalog.sqlite`；
  - 测试临时目录。
- 验收：
  - 86,397 CSV 被 catalog 或明确标记 unreadable/unclassified；
  - checkpoint 排除；
  - 134 nested IC alias 不重复显示；
  - 五个已知代表 schema 被识别；
  - 未知 schema 不崩溃；
  - catalog refresh 可增量执行；
  - 启动不打开全部 CSV；
  - API 不返回绝对根路径。
- 不处理：
  - K 线、研究输出、全量数据清洗。

## Phase 2：Market Adapter 与按需 API

- 依赖：Phase 1。
- 输入：
  - canonical catalog asset；
  - 代表 CSV；
  - datetime/field rules。
- 输出：
  - Market CSV adapter；
  - bars/context API；
  - finite JSON sanitizer；
  - 查询 LRU/ETag。
- 允许读取：
  - 用户请求选择的 canonical CSV；
  - catalog。
- 允许写入：
  - Recipe 代码、测试和 runtime cache；
  - 不写行情目录。
- 验收：
  - 三数据族均能返回规范化 bars；
  - 按字段名读取；
  - amount/money 和 position/OI 保留 raw identity；
  - datetime 三种已知格式可处理；
  - timezone/session pending 不被猜测；
  - range/limit 生效；
  - JSON 无 NaN/Infinity；
  - 单次请求不扫描其他资产。
- 不处理：
  - resample、factor、signal、PnL。

## Phase 3：市场路径视图

- 依赖：Phase 2。
- 输入：
  - Catalog API；
  - Market API。
- 输出：
  - Market Explorer；
  - K 线、volume、position/OI 子图；
  - filters；
  - Bar Inspector；
  - continuous symbol change markers。
- 允许读取：
  - API；
  - 前端静态资源。
- 允许写入：
  - Recipe 前端和测试。
- 验收：
  - family/exchange/product/asset/frequency 逐级选择；
  - 主力、单合约、指数身份不混；
  - zoom/pan/tooltip/candle select 可用；
  - close 不标 mid；
  - 无 bid/ask/L2 伪图；
  - pending time/session 明确；
  - 移动端基本可用；
  - 过宽查询有明确提示。
- 不处理：
  - snapshot detail、因子叠加、交易执行。

## Phase 4：数据语义视图

- 依赖：Phase 1；部分功能依赖 Phase 2。
- 输入：
  - catalog/schema/field semantics。
- 输出：
  - Catalog Tree；
  - Schema Compare；
  - Field Inspector；
  - Capability Matrix；
  - anomaly 视图。
- 允许读取：
  - catalog 和 semantics 配置。
- 允许写入：
  - Recipe 前端、semantics 配置和测试。
- 验收：
  - 五类已知代表 schema 可查看；
  - 列位置差异可见；
  - amount/money、position/OI 只显示候选关系；
  - path-derived symbol 标明来源；
  - alias/checkpoint/unclassified 可审计；
  - unavailable/unsupported/pending 区分。
- 不处理：
  - 生产数据修复和供应商语义猜测。

## Phase 5：研究审计框架与空状态

- 依赖：Phase 1 的 API 骨架。
- 输入：
  - 本文 research contract；
  - 默认空 research source。
- 输出：
  - manifest validator；
  - research catalog；
  - Research Audit 页面；
  - no-data/partial/unsupported 状态；
  - 各 research API 空实现和 contract tests。
- 允许读取：
  - 配置的 research root；
  - 不读取未配置的历史输出。
- 允许写入：
  - Recipe 代码、research catalog/cache 和测试。
- 验收：
  - 没有研究数据时三页正常运行；
  - 不生成 factor、shortlist、curve、trade 或零 PnL；
  - malformed manifest 明确报错；
  - source/project/run/factor/policy identity 不混；
  - 前端模块按 artifact availability 降级；
  - Event 生命周期、reference time 和可选 post-processing 违反契约时可定位；
  - 方向坐标 schema 或转换记录不合法时报告错误，Recipe 自身不执行方向统一。
- 不处理：
  - 创建任何真实研究结果。

## Phase 6：接入首个真实研究输出

- 依赖：Phase 5；Entry Example 依赖 Phase 2。
- 输入：
  - 用户指定的真实 research root；
  - 有效 manifest 和 artifact；
  - 对应 market reference。
- 输出：
  - PnL、summary、breakdown、trades、timeline、entry example、shortlist 中实际可用模块；
  - audit checks。
- 允许读取：
  - 用户指定 research run；
  - manifest 精确引用的行情。
- 允许写入：
  - Recipe cache、测试和必要 adapter；
  - 不修改研究输出。
- 验收：
  - 真实输出逐项显示；
  - 缺失 artifact 不补零；
  - summary/trade/daily PnL 一致性差异可见；
  - Entry Example 不使用 future exit；
  - market revision 不匹配时拒绝叠加；
  - 不同 run/version 不交叉。
- 不处理：
  - 调整因子、policy 或回测。

## Phase 7：性能与交付硬化

- 依赖：Phase 3–6 的实际需求。
- 输入：
  - 性能测试；
  - 真实浏览范围；
  - 最大 trade/run 规模。
- 输出：
  - 查询上限；
  - cache budget；
  - 必要时单文件时间索引方案；
  - README、启动/停止、刷新、smoke test。
- 允许读取：
  - 配置数据和测试样本。
- 允许写入：
  - Recipe 工程和 runtime cache。
- 验收：
  - 启动不做全库内容扫描；
  - 大响应被分页/限制；
  - catalog refresh 可恢复；
  - 端口/PID 操作安全；
  - Python、JavaScript、API、浏览器 smoke 和响应式检查通过。
- 不处理：
  - 微服务、数据库集群、消息队列或自动扩容。

---

## 16. 测试与总体验收

### 16.1 Catalog 测试

- 三种数据族和各路径模板；
- 分钟与高周期路径；
- 主要合约/全部合约/指数身份；
- 134 IC nested alias；
- checkpoint 排除；
- raw/canonical symbol 大小写；
- unknown path；
- header order fingerprint 与 field set fingerprint；
- 增量刷新和 atomic revision。

### 16.2 Adapter 测试

- 五类代表 schema；
- 按字段名而非位置；
- path-derived symbol；
- amount/money raw identity；
- position/open_interest 不混；
- 三种 datetime 文本；
- night timestamp 不等于自动 trading_date；
- non-finite 转 null；
- OHLC warning；
- range/limit；
- 不访问未选中资产。

### 16.3 API 测试

- health/status；
- Catalog pagination/filter；
- bars/context；
- no-data；
- unsupported/pending；
- 404/409/413/422/503；
- UTF-8 和 finite JSON；
- 不泄露绝对 root；
- stale signature invalidation。

### 16.4 Frontend 测试

- 三个固定导航；
- URL state；
- filters 级联；
- K 线 zoom/pan/select；
- Bar Inspector；
- Data Atlas schema diff；
- 研究页 no-data；
- partial artifact；
- Matrix null；
- 桌面/移动布局；
- keyboard/tooltip/empty state；
- chart dispose 和 resize。

### 16.5 Research Contract 测试

- manifest version；
- namespaced identity；
- artifact availability；
- missing file；
- malformed schema；
- factor/policy reference；
- Event formation/post-processing 可选字段与 parent 引用；
- 未配置 post-processing 时合法通过；
- decision time vs emitted；
- feature/label/execution reference time 声明；
- 字段级 `unsigned`/`raw_signed`/`event_aligned` schema；
- direction transform 只接受 `raw_signed -> event_aligned`，并要求 `event_id` 与 `direction_transform_id`；
- 二次转换、unsigned 转换和空 direction 转换报告 contract error；
- artifact join 不自动执行方向统一；
- trade/daily/summary audit；
- no zero fill；
- Entry Example `uses_future_exit=false`；
- market revision mismatch。

### 16.6 最终业务验收清单

- [ ] 只有市场路径、数据语义、研究审计三类功能
- [ ] 旧可视化每项核心需求有迁移去向
- [ ] 当前页面以真实 bar 数据为基础
- [ ] close 未冒充 mid
- [ ] high/low 未冒充 bid/ask
- [ ] volume 未冒充 depth
- [ ] 没有 snapshot/L2 伪造
- [ ] 主要合约、单合约和指数身份分离
- [ ] 五类代表 schema 有 adapter
- [ ] 未知 schema 有状态而不是崩溃
- [ ] 8.6 万文件不在启动或请求中全量打开
- [ ] 前端无行情绝对路径
- [ ] API 不返回 NaN/Infinity
- [ ] no-data 研究页可正常使用
- [ ] 没有虚假 factor、trade、shortlist 或 PnL
- [ ] 研究版本和来源不可按同名误合并
- [ ] 更换数据只刷新 catalog/manifest，不重写前端核心
- [ ] 每个 Phase 可独立执行和验收

---

## 17. 当前待确认问题

以下事项保持 `pending`，不能由后续 Codex猜测：

1. `datetime` 是 bar start、bar end 还是标签时间。
2. 所有数据的 timezone 是否一致，以及是否为 Asia/Shanghai。
3. 各交易所 session 和夜盘 trading_date 归属的权威日历。
4. `position` 是否等于期末 open interest。
5. `amount` 和 `money` 的单位、缩放和区间/累计语义。
6. 主要合约的选主、换月和复权规则。
7. tick size、multiplier 和历史生效 metadata 的来源。
8. 134 个 nested IC 文件是否可永久视为 alias；当前只确认同名、大小、mtime 和部分边缘内容。
9. Recipe 首个真实 research source、项目和 run 在哪里。
10. 首个 research output 使用 CSV 还是 Parquet，以及是否能提供 manifest。
11. summary metrics 是完全由上游提供，还是允许 Recipe 只做哪些确定性 audit recomputation。
12. shortlist 是否会作为正式 artifact；没有时应一直隐藏。
13. 服务仅本机使用，还是需要局域网/反向代理访问。
14. Catalog/research refresh 只使用维护命令，还是需要本地管理按钮。
15. 性能测试后是否需要为少数大型 continuous CSV 建立日级索引。

---

## 18. 明确禁止实现

- 使用分钟 OHLC 伪造 Level2、snapshot、bid/ask 或 mid；
- 根据 volume 猜 depth、imbalance 或订单流；
- 计算因子、标签、信号、模型或策略；
- 执行回测或生成 PnL；
- 生成演示零曲线、虚假 shortlist 或假 trade；
- 用未来退出解释入场；
- 按 display name 合并 factor/policy；
- 混合主要合约、单合约和指数；
- 自动认定 amount=money 或 position=open_interest；
- 自动认定 natural date=trading_date；
- 自动认定 timezone 和 bar timestamp 语义；
- 自动复权或拼接合约；
- 在前端写死行情绝对路径、端口或旧 ID；
- 启动时全量加载 CSV；
- 请求时递归重扫 8.6 万文件；
- 修改、移动、删除行情或研究输出；
- 创建账户系统、插件系统、微服务、消息队列或数据库集群；
- 为形式完整创建大量空模块；
- 未经用户确认直接进入下一 Phase。

---

## 19. Phase 0 完成条件

本规格完成后必须停止，不创建 Recipe 工程。

Phase 0 的唯一交付物是：

```text
/Users/kangbohang/Desktop/start/salt01/recipe.md
```

后续只有在用户明确确认并指定 Phase 后，才允许创建：

```text
/Users/kangbohang/Desktop/start/salt01/recipe
```
