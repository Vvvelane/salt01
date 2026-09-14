import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from '../api';
import { useLanguage } from '../i18n';
import { OhlcChart } from '../components/OhlcChart';
import type { Bar, BarsResponse, Product, Universe } from '../types';
import '../research.css';

type Selection = { product: Product; contract?: string };
const keyOf = (s: Selection) => `${s.product.id}/${s.contract ?? 'MAIN'}`;

function MarketPane({ selection, onRemove }: { selection: Selection; onRemove: () => void }) {
  const { t } = useLanguage();
  const [daily, setDaily] = useState<BarsResponse>();
  const [minute, setMinute] = useState<BarsResponse>();
  const [anchor, setAnchor] = useState('');
  const [expanded, setExpanded] = useState(false);
  const [busy, setBusy] = useState(false);
  const [retry, setRetry] = useState(0);
  const pane = useRef<HTMLElement>(null);
  const [error, setError] = useState('');
  const inspected = useRef<Bar | undefined>(undefined);
  const request = useRef<AbortController | null>(null);
  const fetching = useRef(false);
  const minuteRef = useRef(minute); minuteRef.current = minute;
  const { product, contract } = selection;
  useEffect(() => {
    const controller = new AbortController(); setError('');
    api.bars({ product: product.id, contract, freq: 'daily' }, controller.signal).then(setDaily).catch((e) => { if (!controller.signal.aborted) setError(String(e)); });
    return () => { controller.abort(); request.current?.abort(); };
  }, [product.id, contract, retry]);
  useEffect(() => {
    if (!expanded) return;
    const old = document.body.style.overflow; document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = old; };
  }, [expanded]);
  useEffect(() => { if (!anchor && daily) pane.current?.querySelector<HTMLElement>('.ohlc-interactive')?.focus({ preventScroll: true }); }, [anchor]);
  const back = () => { request.current?.abort(); fetching.current = false; setBusy(false); setMinute(undefined); setAnchor(''); setError(''); };
  const drill = (bar?: Bar) => {
    if (!bar) return;
    request.current?.abort(); const controller = new AbortController(); request.current = controller;
    const date = `${bar.ts.slice(0, 10)}T09:00:00`;
    setAnchor(date); setBusy(true); setError(''); fetching.current = true;
    api.bars({ product: product.id, contract, freq: '1min', anchor: date }, controller.signal).then(setMinute)
      .catch((e) => { if (!controller.signal.aborted) setError(String(e)); })
      .finally(() => { if (!controller.signal.aborted) { setBusy(false); fetching.current = false; } });
  };
  const loadEdge = useCallback((edge: 'before' | 'after') => {
    const current = minuteRef.current;
    if (!current || fetching.current || !(edge === 'before' ? current.has_before : current.has_after) || !current.rows.length) return;
    const controller = new AbortController(); request.current = controller; fetching.current = true; setBusy(true);
    const boundary = edge === 'before' ? current.rows[0].ts : current.rows.at(-1)!.ts;
    api.bars({ product: product.id, contract, freq: '1min', [edge]: boundary }, controller.signal).then((page) => {
      setMinute((old) => {
        if (!old) return old;
        const rows = [...new Map([...old.rows, ...page.rows].map((bar) => [bar.ts, bar])).values()].sort((a, b) => a.ts.localeCompare(b.ts));
        return { ...old, rows, [edge === 'before' ? 'has_before' : 'has_after']: edge === 'before' ? page.has_before : page.has_after };
      });
    }).catch((e) => { if (!controller.signal.aborted) setError(String(e)); })
      .finally(() => { if (!controller.signal.aborted) { fetching.current = false; setBusy(false); } });
  }, [product.id, contract]);
  const controls = <><b>{contract ?? `${product.code} · ${t('主连', 'Continuous')}`}</b><span>{t(product.name, product.code)}</span>
    <button className={!anchor ? 'active' : ''} onClick={back}>Daily</button>
    <button className={anchor ? 'active' : ''} onClick={() => { if (!anchor) drill(inspected.current ?? daily?.rows.at(-1)); }}>1min</button>
    {anchor && <button onClick={back}>Esc · Daily ↩</button>}
    {busy && <span className="subtle">{t('读取中…', 'Loading…')}</span>}
    <button onClick={() => setExpanded(!expanded)} aria-label={t('放大图表', 'Expand chart')}>{expanded ? '↙' : '↗'}</button>
    <button onClick={onRemove} aria-label={t('移除合约', 'Remove contract')}>×</button></>;
  return <section ref={pane} className={`market-pane${expanded ? ' chart-fullscreen' : ''}`} onKeyDown={(e) => { if (e.key === 'Escape') { e.stopPropagation(); if (anchor) back(); else setExpanded(false); } }}>
    {error && <div className="error-banner">{error}<button onClick={() => { setError(''); if (anchor) drill(inspected.current ?? daily?.rows.at(-1)); else setRetry((r) => r + 1); }}>{t('重试', 'Retry')}</button></div>}
    {/* Keep daily mounted while drilling, preserving its exact zoom and cursor. */}
    <div hidden={Boolean(minute)}>{daily ? <OhlcChart bars={daily.rows} daily active={!minute} expanded={expanded} controls={controls} onBarClick={drill} onInspect={(bar) => { inspected.current = bar; }} /> : <div className="chart-empty">{t('读取完整历史…', 'Loading full history…')}<button onClick={onRemove}>×</button></div>}</div>
    {minute && <OhlcChart key={anchor} bars={minute.rows} daily={false} anchor={anchor} onEdge={loadEdge} controls={controls} expanded={expanded} />}
  </section>;
}

export function MarketInspector({ initialProductId }: { initialProductId?: string }) {
  const { t } = useLanguage();
  const [universe, setUniverse] = useState<Universe>();
  const [productId, setProductId] = useState('');
  const [contracts, setContracts] = useState<{ contract: string; start: string; end: string }[]>([]);
  const [selected, setSelected] = useState<Selection[]>([]);
  const [loadingContracts, setLoadingContracts] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => { api.universe().then((data) => {
    setUniverse(data);
    const products = data.exchanges.flatMap((exchange) => exchange.products);
    const initial = products.find((item) => item.id === initialProductId) ?? products.find((item) => item.id === 'SHFE.AU') ?? products[0];
    if (initial) { setProductId(initial.id); setSelected([{ product: initial }]); }
  }).catch((e) => setError(String(e))); }, [initialProductId]);
  useEffect(() => {
    if (!productId) return;
    const controller = new AbortController(); setContracts([]); setLoadingContracts(true); setError('');
    api.contracts(productId, controller.signal).then((data) => setContracts(data.contracts)).catch((e) => { if (!controller.signal.aborted) setError(String(e)); }).finally(() => { if (!controller.signal.aborted) setLoadingContracts(false); });
    return () => controller.abort();
  }, [productId]);
  const product = universe?.exchanges.flatMap((e) => e.products).find((p) => p.id === productId);
  const toggle = (contract?: string) => {
    if (!product) return;
    const value = { product, contract }, key = keyOf(value);
    setSelected((old) => old.some((s) => keyOf(s) === key) ? old.filter((s) => keyOf(s) !== key) : [...old, value]);
  };
  return <div className="market-workspace">
    <header className="market-selector">
      <span className="kicker">MARKET DATA</span>
      <select aria-label={t('品种', 'Product')} value={productId} onChange={(e) => setProductId(e.target.value)}>{universe?.exchanges.map((exchange) => <optgroup label={exchange.id} key={exchange.id}>{exchange.products.map((p) => <option key={p.id} value={p.id}>{p.code} · {t(p.name, p.code)}</option>)}</optgroup>)}</select>
      <details className="contract-picker"><summary>{t('主连 / 合约多选', 'Continuous / contracts')} <span>⌄</span></summary>
        <div className="contract-options">
          {[{ contract: undefined, start: '', end: '' }, ...contracts].map((item) => <label key={item.contract ?? 'MAIN'}><input type="checkbox" checked={selected.some((s) => s.product.id === productId && s.contract === item.contract)} onChange={() => toggle(item.contract)}/><b>{item.contract ?? t('品种主连', 'Continuous contract')}</b>{item.start && <small>{item.start.slice(0, 10)} — {item.end.slice(0, 10)}</small>}</label>)}
          {loadingContracts && <small>{t('正在读取可用合约…', 'Loading available contracts…')}</small>}
        </div>
      </details>
      <span className="subtle">{t('全部历史 · 点击日线进入分钟', 'Full history · Click a daily bar for minutes')}</span>
    </header>
    {error && <div className="error-banner">{error}</div>}
      <div className="selected-contracts">{selected.map((s) => <button key={keyOf(s)} onClick={() => setSelected((old) => old.filter((v) => keyOf(v) !== keyOf(s)))}>{s.contract ?? `${s.product.code} ${t('主连', 'Continuous')}`} ×</button>)}</div>
    {!!selected.length && <div className="market-charts panel" aria-label={t('已选行情对比面板', 'Selected market comparison panel')}>{selected.map((s) => <MarketPane key={keyOf(s)} selection={s} onRemove={() => setSelected((old) => old.filter((v) => keyOf(v) !== keyOf(s)))}/>)}</div>}
    {!selected.length && <div className="chart-empty">{t('选择品种与合约开始浏览', 'Choose products and contracts to begin')}</div>}
  </div>;
}
