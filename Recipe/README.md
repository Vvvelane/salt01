# Recipe

SALT 本地研究终端，现有三个入口：

- **Database Management**：数据档案库直接读取 salt-data 当前 Manifest、Catalog 与已发布批次。九个数据域以旋转封存舱呈现，仅行情舱处于接入高亮状态；发布摘要收进版本提示。行情详情合并品种覆盖矩阵与 Market Inspector，所选主连／合约同时显示在一个对比面板中。单文件 SHA-256 核验结果只保存在 Recipe 的忽略缓存 `.cache/database/`，不会修改 salt-data。
- **Factor Tree**：58 张 NaCl 卡片，共享“家族 → 表达 → idea”结构的卡牌藏馆与自上而下星图。只有**仍在 Factorlab 注册且有 completed 运行快照和结果文件**的 idea 发光；其余卡片保留完整正文。角色和身后的光圈作为同一个漂浮组。卡片弹窗内可直接进入对应注册配置的结果。
- **Factor Results**：合并原 Cross Section。拨转、加速或停止研究卡片；选择后可阅读经济 / 持仓 / 制度 / 执行层说明、查看真实成交样本回放，再进入完整回测。顶部切换已注册配置，数学与规则说明使用已保存的运行参数；当前配置发生变化会提示。详情默认展示完整运行、全部品种的累计结果，图内切换总体 / 全部合约、选择显示曲线、缩放 / 平移 / 放大；年度演化、最近 500 笔分钟精度成交与特有诊断在下方。

语言开关覆盖界面与研究正文。系统减少动态效果设置会停止默认旋转和装饰动画。
页面只消费已完成研究与本地数据，不执行回测、参数搜索、下单或实时订阅。

## 计算口径

- 单品种结果是独立一手的货币损益合计，不是账户收益率。年度零轴居中，净损益向左 / 右延伸；可选虚线为 `net + fees`，滑点已在成交价里，不在虚线中加回。
- FCM 保持固定十商品组合，使用分数权重标准化收益。年度对照为扣成本前 / 后逐日复合收益，成本包括手续费和滑点；累计成本率是每日成本率的和，不是复利拖累。
- FCM 分合约曲线由保存的持仓权重、估值及平仓成交价还原每日净贡献，并乘以前一日组合净值进行收益归因。后端逐日对账；失败则停止提供归因。空仓 / 零值处断线，隐藏曲线不会重算组合，也不是该品种的独立回测。
- 明细时间直接来自 `entry_time` / `exit_time` 或 FCM `execution_time`，保留 Asia/Shanghai 本地分钟。`trading_date` 是记账交易日，不能替代实际成交时间。历史价格动画来自该合约的真实分钟 bar，信号只显示已保存的记录；长持有样本可能抽样并标注。
- `factor_architecture.md` 是架构来源，周转率推导阈值章节仍待定；页面区分架构目标与当前 v3 实现。`exit_layer` 尚未写入流水。FRV / FCM 信号用 close，但 FTR / FID 已用 open / high / low；执行已是 next-bar open。

## 数据与代码边界

```text
frontend → /api
           ├── database.py → salt-data manifests / read-only Catalog / hash observations
           ├── market.py   → SaltCore scan / bounded SQL windows
           ├── research.py → Factorlab config + completed artifacts
           └── app.py      → routes + NaCl registry + static frontend
```

API：`/api/health`、`/api/database/overview`、`/api/database/files`、`/api/database/observations`、`/api/universe`、`/api/contracts?product=SHFE.AU`、`/api/bars`、`/api/cards`、`/api/research`、`/api/results?strategy=...`、`/api/replay?strategy=...`；交互文档 `/api/docs`。

旧 `/api/factors`、`/api/factor-results`、`/api/baskets`、`/api/basket-results` 合并为 research / results 契约。仓库内前端已同步迁移。运行结果按文件时间和大小缓存，前端图表操作在本地完成。Recipe `config/phase1_universe.json` 中未测试的候选品种不会点亮 Factor Tree 或加入已完成策略；数据库页的行情选择独立读取 salt-data Catalog。

已知数据边界：未自行重建 / 复权主连；缺失分钟未补齐；没有 Level 2、真实 bar 内路径或实时 data feed；涨跌停表未进入执行检查；历史交易规则采用当前规则情景。FCM 隐含等权重置成本、预换月日程因果性、整数手数与资金约束仍有待完善。具体设定在页面左上角版本说明及各因子诊断中展示。

## 公开演示站点

`frontend/src/api.ts` 里的 `STATIC_MODE`（由构建时的环境变量 `VITE_STATIC=true` 打开）让前端改为读取预先导出的静态 JSON，而不是请求 `/api/...`。本地开发（`npm run dev`）和本地 `npm run build` 都不受影响，继续像以前一样打后端。只有 Cloudflare Pages 的构建命令会设置 `VITE_STATIC=true`。

更新公开站点上的数据：

```bash
uv run python Recipe/scripts/export_static.py   # 需要设置 SALT_DATA_ROOT
git add Recipe/frontend/public/data
git commit -m "..."
git push
```

导出脚本直接调用 `cards`/`catalog`/`result`/`replay`/`database.overview` 这几个已有的只读函数，写到 `frontend/public/data/`，不会重新计算或触发任何回测。Cloudflare Pages 构建时 `npm run build` 会把这些 JSON 原样拷进产物。

静态版本缺少两类依赖实时 salt-data 查询的功能，在公开站点上会显示为提示文案而不是报错：

- 数据档案库里的"文件与指纹"逐文件 SHA-256 核验（`POST /api/database/observations`）。
- Market Inspector 任意品种 / 任意时间窗口的分钟行情查询（`/api/bars`、`/api/contracts`、`/api/universe`）。

其余内容（数据域总览统计、因子结果、交易回放）都来自导出的快照，公开站点完全可用。

## 启动与校验

在仓库根目录完成环境安装后：

```bash
cd /Users/kangbohang/Developer/salt01/Recipe
npm run build
../.venv/bin/python -m recipe
```

打开 <http://127.0.0.1:8765>。重复执行启动命令会识别现有 Recipe，打印 PID 后退出成功，不再重复绑定端口。若端口属于其他服务则提示换端口，并保留原服务：

```bash
../.venv/bin/python -m recipe --port 8766
```

不必寻找旧终端。启动器只会在健康检查确认 8765 上是 Recipe 后才管理它：

```bash
# 查看唯一的服务和 PID
../.venv/bin/python -m recipe --status

# 关闭该 Recipe 服务
../.venv/bin/python -m recipe --stop

# 关闭旧服务并立刻启动一个新服务（后端改动后使用）
../.venv/bin/python -m recipe --restart
```

`--restart` 启动后会留在当前终端；用 Ctrl-C 可结束这个前台服务。前端修改仍需先重新 `npm run build`，浏览器再强制刷新。

```bash
npm run typecheck
npm run check:ui
../.venv/bin/python -m unittest discover -s tests -v
```
