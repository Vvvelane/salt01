import { FormEvent, useEffect, useState } from 'react';
import { api } from '../api';
import { DataTable } from '../components/DataTable';
import { OhlcChart } from '../components/OhlcChart';
import { Message, Status } from '../components/Status';
import type { Bar, DatasetAvailability, Exchange, Product } from '../types';

function dateValue(value: Date) { return value.toISOString().slice(0, 10); }
function initialRange() { const end = new Date(); const start = new Date(end); start.setDate(start.getDate() - 90); return { start: dateValue(start), end: dateValue(end) }; }

export function Workbench() {
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [exchange, setExchange] = useState('');
  const [productId, setProductId] = useState('');
  const [mode, setMode] = useState('main');
  const [contracts, setContracts] = useState('');
  const [range, setRange] = useState(initialRange());
  const [bars, setBars] = useState<Bar[]>([]);
  const [availability, setAvailability] = useState<DatasetAvailability[]>([]);
  const [revision, setRevision] = useState('');
  const [selected, setSelected] = useState<Bar | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => { Promise.all([api.health(), api.exchanges()]).then(([health, exchangeData]) => { if (health.status !== 'ok') throw new Error(health.warnings[0]?.message || 'DuckDB Catalog 不可用'); setRevision(health.meta.catalog_revision || 'unknown'); setExchanges(exchangeData.data); setExchange(exchangeData.data[0]?.exchange_id || ''); }).catch((reason) => setError(String(reason.message || reason))); }, []);
  useEffect(() => { if (!exchange) return; api.products(exchange).then((response) => { setProducts(response.data); setProductId(response.data[0]?.product_id || ''); }).catch((reason) => setError(reason.message)); }, [exchange]);
  useEffect(() => { if (productId) void loadDaily(); }, [productId]);

  async function loadDaily(event?: FormEvent) {
    event?.preventDefault();
    if (!productId) return;
    setLoading(true); setError('');
    try {
      const [daily, detail] = await Promise.all([api.daily({ product_id: productId, mode, start: range.start, end: range.end, contracts }), api.availability(productId)]);
      setBars(daily.data.bars || []); setAvailability(detail.data.datasets || []); setRevision(daily.meta.catalog_revision || revision); setSelected(null);
    } catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); } finally { setLoading(false); }
  }

  const product = products.find((item) => item.product_id === productId);
  return <div className="page">
    <div className="page-heading"><div><div className="eyebrow">PRODUCT DATA WORKBENCH</div><h1>品种数据工作台</h1><p>读取已发布 DuckDB Catalog，按需查询日线行情。不扫描行情目录，不计算质量结论。</p></div><Status kind={error ? 'error' : 'ok'}>{error ? '请求异常' : '只读索引已连接'}</Status></div>
    {error && <Message kind="error">{error}</Message>}
    <section className="panel"><form className="filters" onSubmit={loadDaily}>
      <label>交易所<select value={exchange} onChange={(event) => setExchange(event.target.value)}>{exchanges.map((item) => <option key={item.exchange_id} value={item.exchange_id}>{item.exchange_code} · {item.exchange_name}</option>)}</select></label>
      <label>品种<select value={productId} onChange={(event) => setProductId(event.target.value)}>{products.map((item) => <option key={item.product_id} value={item.product_id}>{item.product_code} · {item.product_name}{item.status === 'retired' ? ' · 已退市' : ''}</option>)}</select></label>
      <label>模式<select value={mode} onChange={(event) => setMode(event.target.value)}><option value="main">主要连续</option><option value="single">单合约</option><option value="overlay">多合约叠加</option></select></label>
      <label>开始<input type="date" value={range.start} onChange={(event) => setRange({ ...range, start: event.target.value })} /></label>
      <label>结束<input type="date" value={range.end} onChange={(event) => setRange({ ...range, end: event.target.value })} /></label>
      <label className="wide">合约（单合约/叠加）<input value={contracts} onChange={(event) => setContracts(event.target.value)} placeholder="例如 RB2609,RB2701" /></label>
      <button type="submit" disabled={loading}>{loading ? '读取中…' : '加载 Daily'}</button>
    </form><div className="revision">Catalog revision: {revision || '连接中…'}</div></section>
    <section className="two-column"><div className="panel"><div className="panel-title"><h2>Daily OHLCV</h2><span className="hint">点击 K 线查看原始 Bar</span></div><OhlcChart bars={bars} onSelect={setSelected} /><div className="chart-summary">{bars.length} bars · {bars[0]?.timestamp || '—'} → {bars.at(-1)?.timestamp || '—'}</div></div><aside className="panel"><h2>Bar Inspector</h2><DataTable rows={selected ? [selected as unknown as Record<string, unknown>] : []} empty="点击一根 K 线查看时间、OHLC、成交量和合约代码" /></aside></section>
    <section className="two-column"><div className="panel"><h2>品种概览</h2><DataTable rows={product ? [{ exchange: product.exchange_name || product.exchange_id, product: `${product.product_code} ${product.product_name}`, status: product.status, datasets: availability.filter((item) => item.status === 'available').map((item) => item.dataset_key).join(', ') || '—' }] : []} /></div><div className="panel"><h2>当前边界</h2><ul className="plain-list"><li><Status kind="ok">已发布</Status> 1min trading_date/session 下钻</li><li><Status>占位</Status> Research 输出</li><li><Status kind="ok">已移除</Status> 质量检查结果和质量计算层</li><li><Status>索引驱动</Status> session 由 `v_session_rules`、交易日由 `v_trading_calendar` 解析</li></ul></div></section>
  </div>;
}
