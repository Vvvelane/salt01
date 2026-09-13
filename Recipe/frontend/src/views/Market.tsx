import { FormEvent, useEffect, useMemo, useState } from 'react';
import { api } from '../api';
import { OhlcChart } from '../components/OhlcChart';
import type { Bar, BarsResponse, Product, Universe } from '../types';

const DAILY_RANGE = { start: '2026-01-01', end: '2026-09-07' };
const MINUTE_RANGE = { start: '2026-09-01', end: '2026-09-07' };

function number(value: number | null | undefined, digits = 2) {
  return value == null ? '—' : value.toLocaleString('zh-CN', { maximumFractionDigits: digits });
}

export function Market() {
  const [universe, setUniverse] = useState<Universe | null>(null);
  const [product, setProduct] = useState<Product | null>(null);
  const [frequency, setFrequency] = useState<'1min' | 'daily'>('daily');
  const [range, setRange] = useState(DAILY_RANGE);
  const [mode, setMode] = useState<'product' | 'contract'>('product');
  const [contract, setContract] = useState('');
  const [result, setResult] = useState<BarsResponse | null>(null);
  const [selected, setSelected] = useState<Bar | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function loadBars(target: Product, start: string, end: string, freq: '1min' | 'daily', contractCode = '') {
    setLoading(true);
    setError('');
    try {
      const payload = await api.bars({ product: target.id, start, end, freq, contract: contractCode || undefined });
      setResult(payload);
      setSelected(payload.rows.at(-1) ?? null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    api.universe().then((data) => {
      setUniverse(data);
      const initial = data.exchanges.flatMap((exchange) => exchange.products).find((item) => item.id === 'SHFE.AU') ?? data.exchanges[0]?.products[0];
      if (initial) {
        setProduct(initial);
        void loadBars(initial, DAILY_RANGE.start, DAILY_RANGE.end, 'daily');
      }
    }).catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)));
  }, []);

  function submit(event: FormEvent) {
    event.preventDefault();
    if (product) void loadBars(product, range.start, range.end, frequency, mode === 'contract' ? contract : '');
  }

  function changeFrequency(value: '1min' | 'daily') {
    setFrequency(value);
    setRange(value === '1min' ? MINUTE_RANGE : DAILY_RANGE);
  }

  const summary = useMemo(() => {
    const rows = result?.rows ?? [];
    const first = rows.find((bar) => bar.close != null);
    const last = [...rows].reverse().find((bar) => bar.close != null);
    const change = first?.close && last?.close ? (last.close / first.close - 1) * 100 : null;
    const contracts = new Set(rows.map((bar) => bar.contract).filter(Boolean));
    return { first, last, change, contracts: contracts.size };
  }, [result]);

  return (
    <div className="page-grid market-page">
      <aside className="sidebar">
        <div className="sidebar-heading"><span>PHASE 1 UNIVERSE</span><b>24</b></div>
        {universe?.exchanges.map((exchange) => (
          <section className="exchange-group" key={exchange.id}>
            <div className="exchange-title"><span>{exchange.name}</span><small>{exchange.id}</small></div>
            <div className="product-grid">
              {exchange.products.map((item) => (
                <button key={item.id} className={product?.id === item.id ? 'selected' : ''} onClick={() => { setProduct(item); setResult(null); setSelected(null); }}>
                  <b>{item.code}</b><span>{item.name}</span>
                </button>
              ))}
            </div>
          </section>
        ))}
        <p className="source-note">清单只保存品种选择，来源为 salt-data 中的重点品种分组文档。</p>
      </aside>

      <section className="workspace">
        <div className="page-heading">
          <div><span className="kicker">MARKET DATA / SALTCORE</span><h1>{product ? `${product.code} · ${product.name}` : '行情读取'}</h1><p>统一读取 1min 与 daily OHLCVA，图表使用真实本地数据。</p></div>
          <div className={`connection ${error ? 'error' : ''}`}><span />{error ? '读取失败' : loading ? '正在读取' : 'SaltCore Ready'}</div>
        </div>

        <form className="query-bar" onSubmit={submit}>
          <label><span>频率</span><select value={frequency} onChange={(event) => changeFrequency(event.target.value as '1min' | 'daily')}><option value="daily">Daily</option><option value="1min">1 minute</option></select></label>
          <label><span>读取对象</span><select value={mode} onChange={(event) => setMode(event.target.value as 'product' | 'contract')}><option value="product">品种主连</option><option value="contract">具体合约</option></select></label>
          {mode === 'contract' && <label className="contract-input"><span>合约代码</span><input value={contract} onChange={(event) => setContract(event.target.value.toUpperCase())} placeholder={`${product?.code ?? 'AU'}2612`} required /></label>}
          <label><span>开始</span><input type="date" value={range.start} onChange={(event) => setRange({ ...range, start: event.target.value })} /></label>
          <label><span>结束</span><input type="date" value={range.end} onChange={(event) => setRange({ ...range, end: event.target.value })} /></label>
          <button className="primary" disabled={!product || loading}>{loading ? 'LOADING' : 'RUN QUERY'}</button>
        </form>

        {error && <div className="error-banner">{error}</div>}

        <div className="metric-row">
          <div className="metric"><span>RETURNED BARS</span><strong>{result?.returned.toLocaleString() ?? '—'}</strong><small>{result?.truncated ? `共 ${result.row_count.toLocaleString()} 行，显示尾部` : '当前查询范围'}</small></div>
          <div className="metric"><span>LAST CLOSE</span><strong>{number(summary.last?.close)}</strong><small>{summary.last?.ts.slice(0, 10) ?? '等待查询'}</small></div>
          <div className={`metric ${summary.change != null && summary.change < 0 ? 'negative' : ''}`}><span>RANGE CHANGE</span><strong>{summary.change == null ? '—' : `${summary.change >= 0 ? '+' : ''}${summary.change.toFixed(2)}%`}</strong><small>按返回区间首尾收盘</small></div>
          <div className="metric"><span>CONTRACTS</span><strong>{result ? summary.contracts || '—' : '—'}</strong><small>{result?.contract ?? '主连行内身份'}</small></div>
        </div>

        <div className="panel chart-panel">
          <div className="panel-heading"><div><span className="kicker">PRICE / VOLUME</span><h2>{result ? `${result.product.id} · ${result.freq}` : '等待行情'}</h2></div><span className="muted">最多绘制末尾 240 根 · 点击 K 线检查</span></div>
          <OhlcChart bars={result?.rows ?? []} selected={selected} onSelect={setSelected} />
        </div>

        <div className="lower-grid">
          <div className="panel inspector">
            <div className="panel-heading"><div><span className="kicker">BAR INSPECTOR</span><h2>{selected?.ts.replace('T', ' ').slice(0, 19) ?? '选择一根 K 线'}</h2></div><span className="contract-chip">{selected?.contract ?? 'MAIN'}</span></div>
            <dl>
              <div><dt>OPEN</dt><dd>{number(selected?.open)}</dd></div><div><dt>HIGH</dt><dd>{number(selected?.high)}</dd></div>
              <div><dt>LOW</dt><dd>{number(selected?.low)}</dd></div><div><dt>CLOSE</dt><dd>{number(selected?.close)}</dd></div>
              <div><dt>VOLUME</dt><dd>{number(selected?.volume, 0)}</dd></div><div><dt>OPEN INTEREST</dt><dd>{number(selected?.open_interest, 0)}</dd></div>
              <div><dt>AMOUNT</dt><dd>{number(selected?.amount, 0)}</dd></div><div><dt>PRODUCT</dt><dd>{selected?.product_id ?? '—'}</dd></div>
            </dl>
          </div>
          <div className="panel boundary-card"><span className="kicker">CURRENT BOUNDARY</span><h2>第一版只做读取与证明</h2><ul><li><b>真实数据</b><span>DuckDB 读取现有 Parquet</span></li><li><b>统一入口</b><span>Recipe 只调用 SaltCore</span></li><li><b>研究执行</b><span>本页面不计算 Factor 或回测</span></li></ul></div>
        </div>
      </section>
    </div>
  );
}
