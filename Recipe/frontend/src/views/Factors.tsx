import { useEffect, useMemo, useState } from 'react';
import { api } from '../api';
import { PnlChart } from '../components/PnlChart';
import type { FactorCatalog, FactorResults, PnlCurve } from '../types';

type ViewMode = 'total' | 'multi' | 'single';

function money(value: number) {
  return new Intl.NumberFormat('zh-CN', { maximumFractionDigits: 0 }).format(value);
}

export function Factors() {
  const [catalog, setCatalog] = useState<FactorCatalog | null>(null);
  const [strategy, setStrategy] = useState('');
  const [selected, setSelected] = useState<string[]>([]);
  const [single, setSingle] = useState('');
  const [mode, setMode] = useState<ViewMode>('total');
  const [start, setStart] = useState('2016-09-08');
  const [end, setEnd] = useState('2026-09-07');
  const [results, setResults] = useState<FactorResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api.factors().then((value) => {
      setCatalog(value);
      const first = value.strategies[0];
      setStrategy(first?.strategy_id ?? '');
      setSelected(first?.available_products ?? []);
      setSingle(first?.available_products[0] ?? '');
    }).catch((reason) => setError(String(reason)));
  }, []);

  const active = catalog?.strategies.find((item) => item.strategy_id === strategy);
  const available = active?.available_products ?? [];
  const products = catalog?.products.filter((item) => available.includes(item.product_id)) ?? [];

  async function load() {
    if (!strategy || !selected.length) return;
    setLoading(true); setError('');
    try { setResults(await api.factorResults({ strategy, products: selected, start, end })); }
    catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); }
    finally { setLoading(false); }
  }

  useEffect(() => {
    if (strategy && selected.length) void load();
  // The explicit query button controls date edits; strategy and selection still update immediately.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [strategy, selected.join(',')]);

  const shown: PnlCurve[] = useMemo(() => {
    if (!results) return [];
    if (mode === 'total') return [results.total_curve];
    if (mode === 'single') return results.curves.filter((curve) => curve.product_id === single);
    return results.curves;
  }, [results, mode, single]);
  const maxAnnual = Math.max(1, ...(results?.annual.map((item) => Math.abs(item.net_pnl)) ?? [1]));

  return (
    <div className="factor-page">
      <aside className="factor-sidebar">
        <div className="sidebar-heading"><span>V3 RESEARCH</span><b>{catalog?.version ?? '—'}</b></div>
        <label className="control-label">STRATEGY<select value={strategy} onChange={(event) => {
          const next = event.target.value;
          const choices = catalog?.strategies.find((item) => item.strategy_id === next)?.available_products ?? [];
          setStrategy(next); setSelected(choices); setSingle(choices[0] ?? '');
        }}>{catalog?.strategies.map((item) => <option key={item.strategy_id} value={item.strategy_id}>{item.factor_id} · {item.name}</option>)}</select></label>
        <div className="product-picker-title"><span>PRODUCTS</span><button onClick={() => setSelected(selected.length === available.length ? [] : available)}>{selected.length === available.length ? '清空' : '全选'}</button></div>
        <div className="factor-products">{products.map((product) => <label key={product.product_id} className={selected.includes(product.product_id) ? 'checked' : ''}>
          <input type="checkbox" checked={selected.includes(product.product_id)} onChange={() => setSelected((current) => current.includes(product.product_id) ? current.filter((id) => id !== product.product_id) : [...current, product.product_id])} />
          <b>{product.product_id}</b><span>{product.name}</span>
        </label>)}</div>
        <p className="source-note">曲线来自各 factor 的 runs/v3_10y；页面不执行回测。</p>
      </aside>

      <section className="factor-workspace">
        <div className="page-heading">
          <div><span className="kicker">FACTORLAB / FIXED V3</span><h1>{active?.name ?? 'Factor Results'}</h1><p>{strategy} · 每品种独立一手账户 · PnL 从 0 开始</p></div>
          <div className="connection"><span /> PRECOMPUTED RESULTS</div>
        </div>

        <div className="factor-query panel">
          <label><span>START</span><input type="date" value={start} onChange={(event) => setStart(event.target.value)} /></label>
          <label><span>END</span><input type="date" value={end} onChange={(event) => setEnd(event.target.value)} /></label>
          <button className="primary" disabled={loading || !selected.length} onClick={() => void load()}>{loading ? '读取中…' : '更新区间'}</button>
        </div>
        {error && <div className="error-banner">{error}</div>}
        {results && <>
          {results.incomplete_ten_year_products.length > 0 && <div className="coverage-note">数据历史不足十年：{results.incomplete_ten_year_products.join('、')}。图中保留真实可用区间。</div>}
          <div className="metric-row factor-metrics">
            <div className="metric"><span>NET PNL</span><strong>{money(results.metrics.net_pnl)}</strong><small>所选品种一手金额合计</small></div>
            <div className="metric negative"><span>MAX DRAWDOWN</span><strong>{money(results.metrics.max_drawdown)}</strong><small>所选区间累计曲线</small></div>
            <div className="metric"><span>TRADES</span><strong>{results.metrics.trades}</strong><small>完整往返</small></div>
            <div className="metric"><span>WIN RATE</span><strong>{results.metrics.win_rate == null ? '—' : `${(results.metrics.win_rate * 100).toFixed(1)}%`}</strong><small>{results.range.start} → {results.range.end}</small></div>
          </div>

          <div className="panel pnl-panel">
            <div className="panel-heading"><div><span className="kicker">CUMULATIVE NET PNL</span><h2>十年损益路径</h2></div><div className="mode-tabs">{(['total', 'multi', 'single'] as ViewMode[]).map((item) => <button key={item} className={mode === item ? 'active' : ''} onClick={() => setMode(item)}>{item === 'total' ? '总品种' : item === 'multi' ? '多品种' : '单品种'}</button>)}</div></div>
            {mode === 'single' && <select className="single-product" value={single} onChange={(event) => setSingle(event.target.value)}>{selected.map((id) => <option key={id}>{id}</option>)}</select>}
            <PnlChart curves={shown} />
          </div>

          <div className="factor-lower-grid">
            <div className="panel annual-panel"><div className="panel-heading"><div><span className="kicker">YEAR BY YEAR</span><h2>年度演化</h2></div></div><div className="annual-bars">{results.annual.map((item) => <div key={item.year}><span>{item.year}</span><div className="annual-track"><i className={item.net_pnl >= 0 ? 'positive' : 'negative'} style={{ width: `${Math.max(2, Math.abs(item.net_pnl) / maxAnnual * 100)}%` }} /></div><b>{money(item.net_pnl)}</b></div>)}</div></div>
            <div className="panel trade-panel"><div className="panel-heading"><div><span className="kicker">TRADE LEDGER</span><h2>最近成交</h2></div><small>{results.trades_returned} / {results.metrics.trades}</small></div><div className="trade-scroll"><table><thead><tr><th>日期</th><th>品种</th><th>方向</th><th>退出</th><th>净PnL</th></tr></thead><tbody>{results.trades.slice(0, 80).map((trade) => <tr key={String(trade.trade_id)}><td>{String(trade.trading_date)}</td><td>{String(trade.product_id)}</td><td>{String(trade.side)}</td><td>{String(trade.exit_reason)}</td><td className={Number(trade.net_pnl) < 0 ? 'loss' : 'gain'}>{money(Number(trade.net_pnl))}</td></tr>)}</tbody></table></div></div>
          </div>
        </>}
      </section>
    </div>
  );
}
