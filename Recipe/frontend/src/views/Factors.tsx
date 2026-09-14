import { useEffect, useMemo, useState } from 'react';
import { api } from '../api';
import { useLanguage } from '../i18n';
import type { ResearchCatalog, ResearchResults, Strategy } from '../types';
import { FactorCollection } from '../components/FactorCollection';
import { FactorIntro, minuteTime } from '../components/FactorIntro';
import { ResearchAlert, StrategyRules } from '../components/ResearchRules';
import { PerformanceChart, formatValue } from '../components/PerformanceChart';
import '../research.css';

function Annual({ result }: { result: ResearchResults }) {
  const { t } = useLanguage();
  const [costs, setCosts] = useState(true);
  const percent = result.strategy.unit === 'return';
  const max = Math.max(1e-6, ...result.annual.flatMap((a) => [Math.abs(a.net), costs ? Math.abs(a.gross) : 0]));
  const center = 610, x = (v: number) => center + v / max * 475;
  return <section className="result-section annual-section"><header><div><span className="kicker">YEAR BY YEAR</span><h2>{t('年度演化', 'Annual performance')}</h2></div><label className="cost-toggle"><input type="checkbox" checked={costs} onChange={(e) => setCosts(e.target.checked)}/>{percent ? t('显示成本前收益', 'Show pre-cost returns') : t('显示手续费前损益', 'Show pre-fee PnL')}</label></header>
    <svg className="annual-chart" viewBox={`0 0 1200 ${result.annual.length * 36 + 38}`} role="img" aria-label={t('以零为中心的年度净损益及扣费前对照', 'Zero-centered annual net and pre-cost performance')}>
      <text x="135" y="15" className="axis-label">−</text><text x={center} y="15" textAnchor="middle" className="axis-label">0</text><text x="1085" y="15" textAnchor="end" className="axis-label">+</text>
      <line x1={center} x2={center} y1="24" y2={result.annual.length * 36 + 25} stroke="#617970"/>
      {result.annual.map((a, i) => { const y = 37 + i * 36; return <g key={a.year}><title>{`${a.year}: ${formatValue(a.net, percent)} → ${formatValue(a.gross, percent)}`}</title><text x="16" y={y + 4} className="axis-label">{a.year}</text><line x1="135" x2="1085" y1={y} y2={y} stroke="#23342f"/>
        <rect x={Math.min(center, x(a.net))} y={y - 6} width={Math.max(1, Math.abs(x(a.net) - center))} height="12" rx="1" fill={a.net < 0 ? '#d77f93' : '#b7d795'}/>
        {costs && <g fill="none" stroke="#dccf9f" strokeWidth="1.2"><path d={`M${x(a.net)},${y}H${x(a.gross)}`} strokeDasharray="3 3"/><path d={`M${center},${y - 10}H${x(a.gross)}V${y + 10}H${center}`} strokeDasharray="4 4"/></g>}
        <text x="1185" y={y + 4} textAnchor="end" className="annual-value">{formatValue(a.net, percent)}</text></g>; })}
    </svg><p className="subtle">{percent ? t('实线为复合净收益，虚线为逐日成本扣除前的复合收益（手续费 + 滑点）。两者差是复利成本拖累。', 'Solid: compounded net return. Dashed: compounded return before daily fees and slippage. Their difference is compounded cost drag.') : t('实线为净损益；虚线为净损益 + 手续费。滑点已体现在成交价中，虚线不将滑点加回。', 'Solid: net PnL. Dashed: net PnL + fees. Slippage is embedded in fill prices and is not added back.')}</p>
  </section>;
}

function Diagnostics({ result }: { result: ResearchResults }) {
  const { t } = useLanguage();
  const s = result.strategy, d = result.diagnostics;
  const issue: Record<string, [string, string]> = {
    FTR001: ['动量的窗口长度与核形状影响不同：这里仅展示已注册的矩形位移 / 交易日锚点。跳空尺度校准不是在线更新；所有汇总均为独立一手 PnL。', 'Horizon and kernel shape affect momentum differently. These runs cover registered rectangular displacement / trading-date anchors. Gap calibration is fixed, not updated online. Totals sum independent one-lot PnL.'],
    FRV001: ['5 日尺度仍逐分钟扫描，尺度窗口不是自动平仓规则；已另设持有期限。跨主连锚点不比较。原始未复权序列与跳空仍需进一步审计。', 'The 5-day signal is evaluated each minute. Signal horizon does not itself trigger an exit; a separate holding rule does. Cross-contract anchors are rejected. Unadjusted series and gap effects still need further auditing.'],
    FID004: ['开盘区间与初始止损依赖 high / low；回撤退出依赖持仓历史，经济与持仓层无法完全拆开。同一 bar 入场和止损可以具有相同分钟时间，OHLC 不提供内部先后顺序。', 'Opening ranges and initial stops use highs / lows. Giveback exits depend on held-position history, coupling economic and position layers. Entry and stop can share a minute timestamp; OHLC does not supply their intrabar order.'],
    FCM001: ['固定 10 商品研究池；±1 两条腿、总敞口 2，分数权重，无整数手数与资金约束。仅成员变化 / 换月显式记单，隐含的每日等权调整未完全计入成本。预换月平仓使用已发布主连日程，因果可得性仍需审计。', 'Fixed 10-commodity universe; ±1 legs, gross exposure 2, fractional weights without capital or integer sizing. Orders explicitly record membership / roll changes; implicit daily equal-weight resets are not fully costed. Pre-roll exits use the published main schedule, whose causal availability still needs auditing.'],
  };
  return <section className="result-section diagnostics"><header><div><span className="kicker">{s.factor_id} / RESEARCH NOTES</span><h2>{t('实现、问题与后续工作', 'Implementation, issues & next steps')}</h2></div></header><p>{t(...(issue[s.factor_id] ?? ['', '']))}</p>
    {!!d.incomplete_products?.length && <p>{t('未覆盖完整十年：', 'Less than ten years of coverage: ')}{d.incomplete_products.join(' · ')}</p>}
    {d.exit_reasons && <div className="exit-counts">{Object.entries(d.exit_reasons).map(([reason, count]) => <span key={reason}>{reason}<b>{count.toLocaleString()}</b></span>)}</div>}
    {s.unit === 'return' && <><div className="diagnostic-counts"><span>{t('无法执行的调仓日', 'Unexecutable rebalance dates')}<b>{d.failed_rebalances}</b></span><span>{t('研究池不足日', 'Insufficient-universe dates')}<b>{d.insufficient_universe_days}</b></span><span>{t('换月前平仓单', 'Pre-roll close orders')}<b>{d.pre_main_roll_closes}</b></span></div>
      <h3>{t('最新截面排名', 'Latest cross-sectional ranks')} <small>{d.rankings?.[0]?.trading_date}</small></h3>
      <div className="table-scroll"><table><thead><tr>{['Product', 'Contract', 'Score', 'Rank', 'g', 'Target'].map((h) => <th key={h}>{h}</th>)}</tr></thead><tbody>{d.rankings?.map((r) => <tr key={String(r.product_id)}><td>{r.product_id}</td><td>{r.contract ?? '—'}</td><td>{formatValue(r.score == null ? null : Number(r.score), false, 3)}</td><td>{r.rank}</td><td>{formatValue(r.g == null ? null : Number(r.g), false, 2)}</td><td>{formatValue(r.target_weight == null ? null : Number(r.target_weight), true)}</td></tr>)}</tbody></table></div>
      <p className="subtle">{t('排名是收盘目标，持仓是实际执行后的快照；终止日已清仓时，两者可以不同。', 'Ranks describe close-time targets; positions describe actual post-execution holdings. They may differ after terminal liquidation.')}</p>
      <h3>{t('最新实际持仓', 'Latest actual holdings')}</h3>{d.positions?.length ? <div className="exit-counts">{d.positions.map((r) => <span key={String(r.product_id)}>{r.product_id} · {r.contract}<b>{formatValue(Number(r.weight), true)}</b></span>)}</div> : <p className="subtle">{t('最新持仓快照为空仓。', 'The latest position snapshot is flat.')}</p>}
    </>}
  </section>;
}

export function ResultDetail({ result, catalog, onSelect, onBack, onIntro }: { result: ResearchResults; catalog: ResearchCatalog; onSelect: (id: string) => void; onBack: () => void; onIntro: () => void }) {
  const { t } = useLanguage();
  const [mode, setMode] = useState<'total' | 'all'>('total');
  const [selected, setSelected] = useState<string[]>(result.curves.map((c) => c.id));
  const percent = result.strategy.unit === 'return';
  const curves = useMemo(() => mode === 'total' ? [result.total] : result.curves.filter((c) => selected.includes(c.id)), [mode, selected, result]);
  const dates = useMemo(() => result.total.points.map((p) => p.date), [result]);
  const toggle = (id: string) => { if (id === 'TOTAL') return; setMode('all'); setSelected((old) => old.includes(id) ? old.filter((x) => x !== id) : [...old, id]); };
  const s = result.strategy, m = result.metrics;
  return <div className="result-detail"><header className="result-topline"><button className="quiet-button" onClick={onBack}>← {t('卡片库', 'Collection')}</button><ResearchAlert/><button className="quiet-button" onClick={onIntro}>▷ {t('模型与交易回放', 'Model & trade replay')}</button></header>
    <header className="result-heading"><div><span className="kicker">{s.factor_id} / COMPLETED RUN</span><h1>{t(s.name)}</h1><small>{s.strategy_id} · {minuteTime(s.generated_at)} UTC</small></div><label className="variant-select"><small>{t('注册配置', 'Registered configuration')}</small><select value={s.strategy_id} onChange={(e) => onSelect(e.target.value)}>{catalog.strategies.filter((item) => item.ready).map((item) => <option key={item.strategy_id} value={item.strategy_id}>{item.factor_id} · {t(item.name)}</option>)}</select></label></header>
    {s.config_changed && <p className="error-banner">{t('当前配置与该次运行不同。这里展示已完成回测保存的参数；更改配置不会重算此曲线。', 'Current configuration differs from this run. The displayed parameters come from its saved snapshot; configuration edits do not recompute these curves.')}</p>}
    <StrategyRules strategy={s}/>
    <section className="result-section performance-panel"><header><div><span className="kicker">{percent ? 'CUMULATIVE NET RETURN' : 'CUMULATIVE NET PNL'}</span><h2>{t('十年损益路径', 'Ten-year performance')}</h2></div><span className="subtle">{dates[0]} — {dates.at(-1)} · {percent ? t('标准化收益', 'Normalized return') : t('货币损益 · 独立一手汇总', 'Currency PnL · sum of independent one-lot runs')}</span></header>
      <PerformanceChart curves={curves} percent={percent} allDates={dates} onHide={toggle} controls={<><div className="chart-mode"><button className={mode === 'total' ? 'active' : ''} onClick={() => setMode('total')}>{t('总体', 'Total')}</button><button className={mode === 'all' ? 'active' : ''} onClick={() => { setMode('all'); setSelected(result.curves.map((c) => c.id)); }}>{t('全部合约', 'All constituents')}</button></div><details className="curve-picker"><summary>{t('显示品种', 'Visible products')} · {selected.length} ⌄</summary><div className="curve-options">{result.curves.map((c) => <label key={c.id}><input type="checkbox" checked={selected.includes(c.id)} onChange={() => toggle(c.id)}/><b>{c.id}</b><span>{t(catalog.products.find((p) => p.product_id === c.id)?.name)}</span></label>)}</div></details></>}/>
      {percent && mode === 'all' && <p className="subtle">{t('曲线为固定组合的累计净收益贡献，以前一日组合净值连接；空仓或零值处断线。隐藏曲线只改变显示，组合权重和总体收益保持原回测口径。', 'Curves attribute cumulative net return using prior-day portfolio wealth; flat / zero sections are gaps. Hiding a curve changes visibility only, preserving the saved basket weights and total.')}{result.diagnostics.attribution_reconciled === false && <strong>{t(' 分合约对账失败，已停止展示。', ' Constituent reconciliation failed; attribution is withheld.')}</strong>}</p>}
      <div className="compact-metrics">{[[percent ? 'NET RETURN' : 'NET PNL', formatValue(m.net, percent)], ['MAX DRAWDOWN', formatValue(m.drawdown, percent)], [percent ? 'ORDERS' : 'TRADES', m.trades.toLocaleString()], ['WIN RATE', formatValue(m.win_rate, true)], [percent ? t('累计成本率', 'SUM OF COST RATES') : t('总手续费', 'TOTAL FEES'), formatValue(m.fees, percent, 2)]].map(([label, value], i) => <div key={label}><span>{label}</span><strong className={i < 2 && (i === 1 || m.net < 0) ? 'negative' : ''}>{value}</strong></div>)}</div>
    </section>
    <Annual result={result}/>
    <section className="result-section trade-section"><header><div><span className="kicker">TRADE LEDGER</span><h2>{t('最近成交', 'Recent trades')}</h2></div><span className="subtle">{result.trades.length} / {m.trades.toLocaleString()} · Asia/Shanghai</span></header>
      <div className="trade-costs"><span>{percent ? t('每单平均成本率（费用 + 滑点）', 'Average cost rate / order (fees + slippage)') : t('平均手续费 / 完整往返', 'Average fee / completed round trip')} <b>{formatValue(m.average_fee, percent, 2)}</b></span><details><summary>{t('滑点 / 单边成交（当前配置）', 'Slippage / fill (current configuration)')} ⌄</summary><div className="exit-counts">{Object.entries(result.slippage).map(([id, ticks]) => <span key={id}>{id}<b>{ticks} ticks</b></span>)}</div></details></div>
      <div className="table-scroll trade-scroll"><table><thead><tr>{(percent ? [t('成交时间', 'Fill time'), t('信号交易日', 'Signal trading date'), t('品种 / 合约', 'Product / contract'), t('操作', 'Action'), t('原因', 'Reason'), t('权重变化', 'Weight change'), t('成本率', 'Cost rate')] : [t('入场时间', 'Entry time'), t('出场时间', 'Exit time'), t('品种 / 合约', 'Product / contract'), t('方向', 'Side'), t('退出原因', 'Exit reason'), t('手续费', 'Fees'), 'Net PnL']).map((h) => <th key={h}>{h}</th>)}</tr></thead><tbody>{result.trades.map((trade, i) => <tr key={`${trade.trade_id ?? trade.execution_time}-${trade.product_id}-${i}`}><td>{minuteTime(trade.entry_time ?? trade.execution_time)}</td><td>{percent ? trade.signal_date : minuteTime(trade.exit_time)}</td><td>{trade.product_id}<small>{trade.contract}</small></td><td>{percent ? `${trade.action} · ${trade.side}` : trade.side}</td><td>{trade.exit_reason ?? trade.reason}</td><td>{percent ? formatValue(Number(trade.weight_change), true) : formatValue(Number(trade.total_fee), false, 2)}</td><td className={Number(trade.net_pnl) < 0 ? 'negative' : 'positive'}>{formatValue(Number(trade.net_pnl ?? trade.cost_return), percent, percent ? 4 : 0)}</td></tr>)}</tbody></table></div>
      <p className="subtle">{t('时间取自成交文件，精确到分钟；日度 PnL 按交易日汇总，夜盘自然日期可能不同。相同分钟不代表已知秒级先后。', 'Timestamps come from saved executions, to the minute. Daily PnL uses trading dates, which can differ from night-session calendar dates. Equal minutes do not establish tick-level ordering.')}</p>
    </section>
    <Diagnostics result={result}/>
  </div>;
}

export function Factors({ initialStrategy }: { initialStrategy?: string }) {
  const { t } = useLanguage();
  const [catalog, setCatalog] = useState<ResearchCatalog>();
  const [strategyId, setStrategyId] = useState(initialStrategy ?? '');
  const [intro, setIntro] = useState(Boolean(initialStrategy));
  const [result, setResult] = useState<ResearchResults>();
  const [error, setError] = useState('');
  const [retry, setRetry] = useState(0);
  useEffect(() => { let cancelled = false; api.research().then((data) => { if (!cancelled) setCatalog(data); }).catch((e) => { if (!cancelled) setError(String(e)); }); return () => { cancelled = true; }; }, [retry]);
  useEffect(() => {
    if (!strategyId) return;
    const controller = new AbortController(); setResult(undefined); setError('');
    api.results(strategyId, controller.signal).then(setResult).catch((e) => { if (!controller.signal.aborted) setError(String(e)); });
    return () => controller.abort();
  }, [strategyId, retry]);
  const select = (id: string, explain: boolean) => { setStrategyId(id); setIntro(explain); window.scrollTo({ top: 0 }); };
  const back = () => { setStrategyId(''); setIntro(false); setError(''); };
  const strategy: Strategy | undefined = catalog?.strategies.find((s) => s.strategy_id === strategyId);
  if (error) return <div className="workspace"><div className="error-banner">{error}</div><button onClick={() => setRetry((r) => r + 1)}>{t('重试', 'Retry')}</button><button onClick={back}>{t('返回', 'Back')}</button></div>;
  if (!catalog) return <div className="room-loading">{t('读取已完成研究…', 'Loading completed research…')}</div>;
  if (!strategyId) return <FactorCollection strategies={catalog.strategies} onSelect={(id) => select(id, true)}/>;
  if (intro && strategy) return <FactorIntro key={strategyId} strategy={strategy} onEnter={() => { setIntro(false); window.scrollTo({ top: 0 }); }} onBack={back}/>;
  if (!result) return <div className="room-loading">{t('读取完整回测…', 'Loading full run…')}</div>;
  return <ResultDetail key={strategyId} result={result} catalog={catalog} onSelect={(id) => select(id, false)} onBack={back} onIntro={() => { setIntro(true); window.scrollTo({ top: 0 }); }}/>;
}
