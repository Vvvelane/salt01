# Run artifacts

本阶段没有实际 backtest run。未来每次运行创建独立 `<run_id>/`，不得覆盖旧结果。

manifest 应记录：状态（包括 failed）、代码版本/dirty 标记、Card registry hash、配置及 hash、数据文件清单与指纹、样本窗口、时区、政策版本、随机种子、软件版本。成功产物按阶段区分 features、labels、signals、orders、fills、ledger、reconciliation、evaluation。

机器生成文件默认 gitignore。少量经审阅的展示数据未来单独导出，不将全量本地研究记录直接发布。
