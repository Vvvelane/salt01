import { useEffect, useId, useMemo, useRef, useState, type ReactNode } from 'react';
import type { Curve } from '../types';
import { useLanguage } from '../i18n';

export const COLORS = ['#d7ff64', '#59dfcf', '#e4ad7c', '#aea4f1', '#6ab5e1', '#d88398', '#d8c480', '#81bc9b', '#c1d499', '#75c9d3', '#cfb4a1'];
export const formatValue = (value: number | null | undefined, percent = false, digits = 0) => value == null ? '—' : percent ? `${(value * 100).toLocaleString('en-US', { maximumFractionDigits: 2 })}%` : value.toLocaleString('en-US', { maximumFractionDigits: digits });
export function linePath(points: { x: number; y: number | null }[]): string {
  let move = true, path = '';
  for (const p of points) {
    if (p.y === null || !Number.isFinite(p.y)) { move = true; continue; }
    path += `${move ? 'M' : 'L'}${p.x.toFixed(2)},${p.y.toFixed(2)}`; move = false;
  }
  return path;
}

export function PerformanceChart({ curves, percent, allDates, onHide, controls }: { curves: Curve[]; percent: boolean; allDates: string[]; onHide: (id: string) => void; controls?: ReactNode }) {
  const { t } = useLanguage();
  const [domain, setDomain] = useState<[number, number]>([0, allDates.length - 1]);
  const [cursor, setCursor] = useState<number | null>(null);
  const [expanded, setExpanded] = useState(false);
  const surface = useRef<HTMLDivElement>(null);
  const svg = useRef<SVGSVGElement>(null);
  const clip = useId();
  const dragging = useRef<{ x: number; start: number; end: number; moved: boolean } | null>(null);
  const moved = useRef(false);
  const indices = useMemo(() => new Map(allDates.map((date, i) => [date, i])), [allDates]);
  const lookup = useMemo(() => curves.map((curve) => new Map(curve.points.map((point) => [point.date, point.value]))), [curves]);
  const [left, right] = domain;
  const width = 1200, height = expanded ? 600 : 420, L = 85, R = 25, T = 28, B = height - 45, plot = width - L - R;
  const values = useMemo(() => curves.flatMap((c) => c.points.filter((p) => { const i = indices.get(p.date); return i !== undefined && i >= left && i <= right && p.value !== null; }).map((p) => p.value!)), [curves, indices, left, right]);
  const low = Math.min(0, ...values), high = Math.max(0, ...values), pad = Math.max((high - low) * .08, percent ? .001 : 1);
  const yMin = low - pad, yMax = high + pad;
  const x = (i: number) => L + (i - left) / Math.max(1, right - left) * plot;
  const y = (v: number) => B - (v - yMin) / (yMax - yMin) * (B - T);
  const paths = useMemo(() => curves.map((curve) => linePath(curve.points.map((p) => ({ x: x(indices.get(p.date) ?? -1), y: p.value === null ? null : y(p.value) })))), [curves, indices, left, right, yMin, yMax, height]);
  const bound = (start: number, end: number) => {
    const span = Math.min(allDates.length - 1, Math.max(14, end - start));
    const a = Math.max(0, Math.min(allDates.length - 1 - span, start)); return [a, a + span] as [number, number];
  };
  const zoom = (factor: number, anchor = .5) => { const span = (right - left) * factor; const a = left + ((right - left) - span) * anchor; setDomain(bound(a, a + span)); };
  const position = (clientX: number, clientY: number) => {
    const matrix = svg.current?.getScreenCTM(); return matrix ? new DOMPoint(clientX, clientY).matrixTransform(matrix.inverse()) : null;
  };
  const wheel = useRef<(e: WheelEvent) => void>(() => {});
  wheel.current = (event) => {
    const p = position(event.clientX, event.clientY); if (!p) return;
    if (Math.abs(event.deltaX) > Math.abs(event.deltaY) * .6 && !event.ctrlKey) {
      const shift = event.deltaX / Math.max(1, surface.current!.clientWidth) * (right - left); setDomain(bound(left + shift, right + shift));
    } else zoom(Math.exp(Math.max(-1, Math.min(1, event.deltaY * .003))), Math.max(0, Math.min(1, (p.x - L) / plot)));
  };
  useEffect(() => {
    const node = surface.current!; const handler = (event: WheelEvent) => { event.preventDefault(); wheel.current(event); };
    node.addEventListener('wheel', handler, { passive: false }); return () => node.removeEventListener('wheel', handler);
  }, []);
  useEffect(() => {
    if (!expanded) return;
    const old = document.body.style.overflow; document.body.style.overflow = 'hidden';
    const key = (e: KeyboardEvent) => { if (e.key === 'Escape') setExpanded(false); };
    window.addEventListener('keydown', key);
    return () => { document.body.style.overflow = old; window.removeEventListener('keydown', key); };
  }, [expanded]);
  const tickIndices = Array.from({ length: 5 }, (_, i) => Math.round(left + (right - left) * i / 4));
  return <div className={`performance-chart${expanded ? ' chart-fullscreen' : ''}`}>
    <div className="performance-tools">{controls}<div className="chart-actions"><button onClick={() => zoom(.7)} aria-label={t('放大', 'Zoom in')}>+</button><button onClick={() => zoom(1.4)} aria-label={t('缩小', 'Zoom out')}>−</button><button onClick={() => setDomain([0, allDates.length - 1])}>↺</button><button onClick={() => setExpanded(!expanded)}>{expanded ? t('关闭', 'Close') : '↗'}</button></div></div>
    <div className="performance-surface" ref={surface} onPointerDown={(event) => {
      if (event.button !== 0) return;
      dragging.current = { x: event.clientX, start: left, end: right, moved: false }; moved.current = false;
    }} onPointerMove={(event) => {
      const p = position(event.clientX, event.clientY); if (!p) return;
      const drag = dragging.current;
      if (drag && Math.abs(event.clientX - drag.x) > 4) {
        drag.moved = true; moved.current = true; event.currentTarget.setPointerCapture(event.pointerId);
        const shift = -(event.clientX - drag.x) / Math.max(1, surface.current!.clientWidth) * (drag.end - drag.start);
        setDomain(bound(drag.start + shift, drag.end + shift)); setCursor(null);
      } else if (!drag) setCursor(Math.max(0, Math.min(allDates.length - 1, Math.round(left + (p.x - L) / plot * (right - left)))));
    }} onPointerUp={() => { dragging.current = null; }} onPointerCancel={() => { dragging.current = null; }} onPointerLeave={() => { if (!dragging.current) setCursor(null); }}>
      <svg ref={svg} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={t('可缩放的累计净损益图', 'Interactive cumulative net performance')}>
        <defs><clipPath id={clip}><rect x={L} y={T} width={plot} height={B - T}/></clipPath></defs>
        {Array.from({ length: 5 }, (_, i) => yMin + (yMax - yMin) * i / 4).map((v, i) => <g key={i}><line x1={L} x2={width - R} y1={y(v)} y2={y(v)} className="grid-line"/><text className="axis-label" x={L - 12} y={y(v) + 4} textAnchor="end">{formatValue(v, percent)}</text></g>)}
        <line x1={L} x2={width - R} y1={y(0)} y2={y(0)} stroke="#819286" strokeDasharray="3 6" opacity=".6"/>
        <g clipPath={`url(#${clip})`}>{curves.map((curve, index) => {
          const path = paths[index];
          return <g key={curve.id}><path d={path} fill="none" stroke={COLORS[index % COLORS.length]} strokeWidth={curves.length === 1 ? 1.65 : 1.1} vectorEffect="non-scaling-stroke"/><path className="curve-hit" d={path} fill="none" stroke="transparent" strokeWidth="10" onClick={() => { if (!moved.current) onHide(curve.id); }}><title>{curve.id}</title></path></g>;
        })}</g>
        {tickIndices.map((i, n) => <text key={n} className="axis-label" x={x(i)} y={height - 16} textAnchor={n === 0 ? 'start' : n === 4 ? 'end' : 'middle'}>{allDates[i]}</text>)}
        {cursor !== null && <g><line x1={x(cursor)} x2={x(cursor)} y1={T} y2={B} stroke="#83978d" strokeDasharray="3 4"/>{curves.map((c, i) => { const v = lookup[i].get(allDates[cursor]); return v == null ? null : <circle key={c.id} cx={x(cursor)} cy={y(v)} r="3" fill={COLORS[i % COLORS.length]}/>; })}</g>}
        {!curves.length && <text x="600" y="210" textAnchor="middle" className="axis-label">{t('从上方选择显示曲线', 'Choose curves above')}</text>}
      </svg>
      {cursor !== null && <div className="performance-tooltip"><b>{allDates[cursor]}</b>{curves.map((c, i) => <div key={c.id}><span style={{ color: COLORS[i % COLORS.length] }}>{c.id}</span><strong>{formatValue(lookup[i].get(allDates[cursor]), percent)}</strong></div>)}</div>}
    </div>
    <div className="performance-legend">{curves.map((c, i) => <button key={c.id} onClick={() => onHide(c.id)}><i style={{ background: COLORS[i % COLORS.length] }}/>{c.id}</button>)}<small>{t('拖动平移 · 滚动缩放 · 点击曲线隐藏', 'Drag to pan · Scroll to zoom · Click a curve to hide')}</small></div>
  </div>;
}
