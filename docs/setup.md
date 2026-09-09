# 当前开发环境：安装与验证

> 这份文件只说明当前这版代码在本地怎样安装和检查。它不是未来前端、可视化、后端或研究路线图，也不是必须长期继承的工程规范。项目结构改变后，这份文件可以随时重写或删除；平时对话不需要反复参考，只有环境安装、VSCode 导入或验证命令出问题时才需要看它。

当前机器已有 Python 3.12、uv 和 `.venv`。本项目不需要服务器、域名或额外桌面软件。

## 新环境

在项目根目录执行：

```bash
uv sync --no-dev
export SALT_DATA_ROOT=/Users/kangbohang/Developer/salt-data
.venv/bin/python scripts/phase1_demo.py
```

`uv sync --no-dev` 只安装本轮基础包及运行依赖；Notebook 和额外研究库保留为可选 dependency groups，不默认安装。workspace 中的本地包通过 editable install 连接，源码不需要修改 `sys.path`。`root=` 优先于环境变量；当前源码 checkout 未设置时可定位相邻 salt-data。

开发验证可以安装工作区全部包（含已有 Recipe/vollab 的测试依赖）：

```bash
uv sync --all-packages
.venv/bin/python -m pytest -q
.venv/bin/python NaCl/scripts/build_registry.py --check
.venv/bin/python SaltCore/scripts/verify_core.py --output docs/phase1-market-verification.json
```

不依赖 salt-data 的纯离线测试：

```bash
.venv/bin/python -m pytest -q SaltCore/tests/test_market_api.py NaCl/tests SALTlab/Factorlab/tests
```

首次下载依赖需要网络。若尚未安装 Python 3.12 或 uv，先在本机安装对应工具；这属于新机器设置，不代表本项目已经完成部署。

## VSCode

选择 `${workspaceFolder}/.venv/bin/python`。本地包采用 editable 安装，修改源码后即可重新运行。若导入报错，先检查解释器和 `uv sync`；不要在业务脚本中加入 `sys.path` 注入来绕过环境问题。

## 数据或文档变化

行情报告是一次小窗口验收快照，可显式重跑；文件指纹由相对路径、大小、mtime 组成，并非全量文件内容哈希。Universe 是已经审阅的排名前十快照，排名 Markdown 改变不会悄悄改变实验 Universe，更新时需明确刷新及审阅。

Card 修改后按 NaCl README 重新构建并检查，网站/backend 的运行流程始终只读 JSON。Factorlab 的首次 Idea 选择和政策冻结是后续研究任务，不需要先购置或部署外部服务。
