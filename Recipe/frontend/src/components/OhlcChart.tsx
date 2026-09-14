import { useId, useEffect, useLayoutEffect, useMemo, useRef, useState, type KeyboardEvent, type PointerEvent as ReactPointerEvent, type ReactNode } from 'react';
import type { Bar } from '../types';
import { useLanguage } from '../i18n';
import { boundDomain, candleBuckets, type Domain } from './chart-window';

type Props = { bars: Bar[]; daily: boolean; controls?: ReactNode; expanded?: boolean; active?: boolean; anchor?: string; onBarClick?: (bar: Bar) => void; onInspect?: (bar: Bar) => void; onEdge?: (edge: "before" | "after") => void };
type Cursor = { index: number; price: number | null };
const WIDTH = 1200;
const LEFT = 76;
const RIGHT = 22;
const MIN_BARS = 14;
const INITIAL_BARS = 240;
const initialDomain = (count: number) => boundDomain(Math.max(0, count - INITIAL_BARS), count, count);

export function OhlcChart({ bars, daily, controls, expanded = false, active = true, anchor, onBarClick, onInspect, onEdge }: Props) {
  const { t } = useLanguage();
  const clipId = useId();
  const [domain, setDomain] = useState<Domain>(() => { const index = anchor ? bars.findIndex((b) => b.ts >= anchor) : -1; return index >= 0 ? boundDomain(index - 50, index + 190, bars.length) : daily ? { start: 0, end: bars.length } : initialDomain(bars.length); });
  const [cursor, setCursor] = useState<Cursor | null>(null);
  const lastCursor = useRef<Cursor | null>(null);
  if (cursor) lastCursor.current = cursor;
  useEffect(() => { if (active && lastCursor.current) setCursor(lastCursor.current); }, [active]);
  const [dragging, setDragging] = useState(false);
  const surfaceRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const drag = useRef<{ pointer: number; startX: number; initial: Domain } | null>(null);
  const previousBars = useRef(bars);
  useLayoutEffect(() => {
    const previous = previousBars.current;
    if (previous === bars) return;
    const offset = previous.length ? bars.findIndex((bar) => bar.ts === previous[0].ts) : -1;
    if (offset >= 0) {
      setDomain((old) => ({ start: old.start + offset, end: old.end + offset }));
      setCursor((old) => old ? { ...old, index: old.index + offset } : null);
      if (drag.current) drag.current.initial = { start: drag.current.initial.start + offset, end: drag.current.initial.end + offset };
    } else { setDomain(initialDomain(bars.length)); setCursor(null); }
    previousBars.current = bars;
  }, [bars]);
  useEffect(() => { if (!daily) surfaceRef.current?.closest<HTMLElement>('.ohlc-interactive')?.focus({ preventScroll: true }); }, [daily]);

  const left = Math.floor(Math.max(0, Math.min(domain.start, Math.max(0, bars.length - MIN_BARS))));
  const right = Math.floor(Math.min(bars.length, Math.max(left + Math.min(MIN_BARS, bars.length), domain.end)));
  const span = right - left;
  const visible = useMemo(() => bars.slice(left, right), [bars, left, right]);
  const buckets = useMemo(() => candleBuckets(bars, left, right), [bars, left, right]);
  const height = expanded ? 560 : 470;
  const plotTop = 26;
  const plotBottom = height - 128;
  const volumeTop = plotBottom + 31;
  const volumeBottom = height - 71;
  const plotWidth = WIDTH - LEFT - RIGHT;
  const step = plotWidth / Math.max(1, visible.length);
  const x = (index: number) => LEFT + (index + 0.5) * step;

  // Zoom fits price; horizontal pan preserves the scale until the next zoom or explicit fit.
  const prices = useMemo(() => visible.flatMap((bar) => [bar.low, bar.high]).filter((value): value is number => value !== null && Number.isFinite(value)), [visible]);
  const dataLow = prices.length ? Math.min(...prices) : 0;
  const dataHigh = prices.length ? Math.max(...prices) : 1;
  const dataPad = Math.max((dataHigh - dataLow) * 0.08, Math.abs(dataHigh || 1) * 0.001);
  const priceScale = useRef({ span: -1, min: 0, max: 1 });
  if (priceScale.current.span !== span) priceScale.current = { span, min: dataLow - dataPad, max: dataHigh + dataPad };
  const yMin = priceScale.current.min;
  const yMax = priceScale.current.max;
  const yRange = Math.max(Number.EPSILON, yMax - yMin);
  const y = (value: number | null) => plotTop + (yMax - (value ?? yMin)) / yRange * (plotBottom - plotTop);
  const maxVolume = Math.max(1, ...buckets.map(({ bar }) => bar.volume ?? 0));
  const ticks = Array.from({ length: 6 }, (_, index) => yMax - index * yRange / 5);
  const dateIndices = [...new Set([0, Math.round((visible.length - 1) / 4), Math.round((visible.length - 1) / 2), Math.round((visible.length - 1) * 3 / 4), visible.length - 1])];
  const label = (ts: string) => daily ? ts.slice(0, 10) : ts.replace('T', ' ').slice(0, 16);

  function toSvg(clientX: number, clientY: number) {
    const svg = svgRef.current;
    const matrix = svg?.getScreenCTM();
    if (!svg || !matrix) return null;
    const point = new DOMPoint(clientX, clientY).matrixTransform(matrix.inverse());
    return { x: point.x, y: point.y, scale: matrix.a };
  }

  function zoomAround(factor: number, anchor: number) {
    const nextSpan = Math.round(Math.min(bars.length, Math.max(MIN_BARS, span * factor)));
    const start = Math.round(left + (span - nextSpan) * anchor);
    setDomain(boundDomain(start, start + nextSpan, bars.length));
  }

  // React registers wheel listeners as passive, so preventDefault there cannot stop the page
  // scrolling; register a native one once and route it to the latest render's handler.
  const wheelHandler = useRef<(event: WheelEvent) => void>(() => {});
  wheelHandler.current = (event: WheelEvent) => {
    const point = toSvg(event.clientX, event.clientY);
    if (!point) return;
    if (Math.abs(event.deltaX) > Math.abs(event.deltaY) * 0.6 && !event.ctrlKey && !event.metaKey) {
      const shift = Math.round(event.deltaX / (plotWidth * point.scale) * span);
      setDomain((current) => boundDomain(current.start + shift, current.end + shift, bars.length));
      return;
    }
    const anchor = Math.max(0, Math.min(1, (point.x - LEFT) / plotWidth));
    zoomAround(Math.exp(Math.max(-1.2, Math.min(1.2, event.deltaY * 0.003))), anchor);
  };
  useEffect(() => {
    const surface = surfaceRef.current;
    if (!surface) return;
    const onWheel = (event: WheelEvent) => { event.preventDefault(); wheelHandler.current(event); };
    surface.addEventListener('wheel', onWheel, { passive: false });
    return () => surface.removeEventListener('wheel', onWheel);
  }, [bars.length > 0]);

  function pointerDown(event: ReactPointerEvent<HTMLDivElement>) {
    if (event.button !== 0) return;
    drag.current = { pointer: event.pointerId, startX: event.clientX, initial: { start: left, end: right } };
    event.currentTarget.setPointerCapture(event.pointerId);
    setDragging(true);
  }
  function pointerMove(event: ReactPointerEvent<HTMLDivElement>) {
    const point = toSvg(event.clientX, event.clientY);
    if (!point) return;
    if (drag.current) {
      const initial = drag.current.initial;
      const shift = Math.round(-(event.clientX - drag.current.startX) / (plotWidth * point.scale) * (initial.end - initial.start));
      setDomain(boundDomain(initial.start + shift, initial.end + shift, bars.length));
      return;
    }
    const inside = point.x >= LEFT && point.x <= WIDTH - RIGHT && point.y >= plotTop && point.y <= volumeBottom;
    if (!inside) { setCursor(null); return; }
    const index = Math.max(0, Math.min(visible.length - 1, Math.floor((point.x - LEFT) / step)));
    const price = point.y <= plotBottom ? yMax - (point.y - plotTop) / (plotBottom - plotTop) * yRange : null;
    setCursor({ index: left + index, price });
  }
  function pointerUp(event: ReactPointerEvent<HTMLDivElement>) {
    if (drag.current?.pointer !== event.pointerId) return;
    const clicked = Math.abs(event.clientX - drag.current.startX) < 5 && event.type !== 'pointercancel';
    drag.current = null;
    setDragging(false);
    if (clicked) {
      const point = toSvg(event.clientX, event.clientY);
      if (point && point.x >= LEFT && point.x <= WIDTH - RIGHT && point.y >= plotTop && point.y <= plotBottom) {
        const index = Math.max(left, Math.min(right - 1, left + Math.floor((point.x - LEFT) / step)));
        setCursor({ index, price: null }); onBarClick?.(bars[index]);
      }
    }
  }
  function keyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === 'Escape') { setCursor(null); return; }
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    const current = cursor?.index ?? right - 1;
    const next = Math.max(0, Math.min(bars.length - 1, current + (event.key === 'ArrowLeft' ? -1 : 1)));
    if (next < left) setDomain(boundDomain(next, next + span, bars.length));
    if (next >= right) setDomain(boundDomain(next - span + 1, next + 1, bars.length));
    setCursor({ index: next, price: null });
  }

  useEffect(() => {
    if (left < 40) onEdge?.('before');
    if (right > bars.length - 40) onEdge?.('after');
  }, [left, right, bars.length, onEdge]);
  useEffect(() => { const bar = cursor ? bars[cursor.index] : undefined; if (bar) onInspect?.(bar); }, [cursor?.index, bars, onInspect]);
  const candleNodes = useMemo(() => buckets.map(({ bar, index, count }) => {
          const candleWidth = Math.max(.7, Math.min(9, step * count * .7));
          const validPrice = [bar.open, bar.close, bar.high, bar.low].every((v) => v !== null && Number.isFinite(v));
          const up = (bar.close ?? 0) >= (bar.open ?? 0);
          const open = y(bar.open); const close = y(bar.close);
          const volumeHeight = ((bar.volume ?? 0) / maxVolume) * (volumeBottom - volumeTop);
          return <g key={`${bar.ts}-${bar.contract ?? index}`}>
            {validPrice && <><line x1={x(index)} y1={y(bar.high)} x2={x(index)} y2={y(bar.low)} className={up ? 'up' : 'down'} />
            <rect x={x(index) - candleWidth / 2} y={Math.min(open, close)} width={candleWidth} height={Math.max(1.5, Math.abs(close - open))} className={up ? 'up-fill' : 'down-fill'} /></>}
            <rect x={x(index) - candleWidth / 2} y={volumeBottom - volumeHeight} width={candleWidth} height={Math.max(1, volumeHeight)} className={up ? 'volume-up' : 'volume-down'} />
          </g>;
        }), [buckets, step, yMin, yMax, height, maxVolume]);
  if (!bars.length || !visible.length) {
    return <div className="ohlc-interactive"><div className="ohlc-toolbar"><div className="ohlc-toolbar-left">{controls}</div></div><div className="chart-empty">{t('这个时间范围没有数据')}</div></div>;
  }
  const cursorLocal = cursor && cursor.index >= left && cursor.index < right ? cursor.index - left : null;
  const inspected = cursor ? bars[cursor.index] : bars.at(-1);
  return <div className={`ohlc-interactive${dragging ? ' is-dragging' : ''}`} onKeyDown={keyDown} tabIndex={0} role="group" aria-label={t('OHLCV price and volume chart')}>
    <div className="ohlc-toolbar">
      <div className="ohlc-toolbar-left">{controls}<span className="ohlc-hint" title={t('宽视野合并绘制，游标读取原始 bar。横移固定价格轴，缩放重新适配。', 'Wide views group candles; the cursor reads the original bar. Panning locks the price axis; zooming refits it.')}>{t('拖拽平移 · 滚轮缩放 · ← → 移动游标', 'Drag to pan · Scroll to zoom · ← → move cursor')}</span></div>
      <div>
        <button type="button" aria-label={t('缩小')} onClick={() => zoomAround(1.4, 0.5)}>−</button>
        <button type="button" aria-label={t('放大')} onClick={() => zoomAround(0.72, 0.5)}>+</button>
        <button type="button" onClick={() => { priceScale.current.span = -1; setDomain({ start: 0, end: bars.length }); setCursor(null); }}>{daily ? t('全部历史', 'Full history') : t('已载入区间', 'Loaded range')}</button>
      </div>
    </div>
    <div ref={surfaceRef} className="chart-wrap" onPointerDown={pointerDown} onPointerMove={pointerMove} onPointerUp={pointerUp} onPointerCancel={pointerUp} onPointerLeave={() => { if (!drag.current && active) setCursor(null); }}>
      <svg ref={svgRef} viewBox={`0 0 ${WIDTH} ${height}`} role="img" aria-label={t('OHLCV price and volume chart')}>
        {ticks.map((value) => { const position = y(value); return <g key={value}><line x1={LEFT} y1={position} x2={WIDTH - RIGHT} y2={position} className="grid-line" /><text x={LEFT - 10} y={position + 4} className="axis-label" textAnchor="end">{value.toLocaleString('en-US', { maximumFractionDigits: 2 })}</text></g>; })}
        <defs><clipPath id={clipId}><rect x={LEFT} y={plotTop} width={plotWidth} height={volumeBottom - plotTop}/></clipPath></defs>
        <g clipPath={`url(#${clipId})`}>
        {candleNodes}
        </g><line x1={LEFT} y1={volumeBottom} x2={WIDTH - RIGHT} y2={volumeBottom} className="axis-line" />
        {dateIndices.map((index) => <text key={`${index}-${visible[index]?.ts}`} x={x(index)} y={height - 27} className="axis-label" textAnchor={index === 0 ? 'start' : index === visible.length - 1 ? 'end' : 'middle'}>{label(visible[index].ts)}</text>)}
        <text x={LEFT} y={volumeTop - 9} className="axis-caption">VOLUME</text>
        <text className="axis-caption" x={WIDTH - RIGHT} y={plotTop - 8} textAnchor="end">PRICE</text>
        {cursorLocal !== null && !dragging && <g className="crosshair">
          <line x1={x(cursorLocal)} x2={x(cursorLocal)} y1={plotTop} y2={volumeBottom} />
          {cursor?.price != null && <>
            <line x1={LEFT} x2={WIDTH - RIGHT} y1={y(cursor.price)} y2={y(cursor.price)} />
            <rect x={2} y={y(cursor.price) - 10} width={LEFT - 6} height={20} rx={2} />
            <text x={LEFT - 10} y={y(cursor.price) + 4} textAnchor="end">{cursor.price.toLocaleString('en-US', { maximumFractionDigits: 2 })}</text>
          </>}
        </g>}
      </svg>
    </div>
    <div className="ohlc-hover-readout" aria-live="polite">{inspected && <><b>{label(inspected.ts)}</b><span>O <strong>{inspected.open ?? '—'}</strong></span><span>H <strong>{inspected.high ?? '—'}</strong></span><span>L <strong>{inspected.low ?? '—'}</strong></span><span>C <strong>{inspected.close ?? '—'}</strong></span><span>V <strong>{inspected.volume?.toLocaleString() ?? '—'}</strong></span><span>OI <strong>{inspected.open_interest?.toLocaleString() ?? '—'}</strong></span><span>{t('AMOUNT')} <strong>{inspected.amount?.toLocaleString() ?? '—'}</strong></span>{inspected.contract && <span>{inspected.contract}</span>}</>}</div>
  </div>;
}
