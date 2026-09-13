import { useMemo, useState } from 'react';
import type { PnlCurve } from '../types';

const COLORS = ['#d7ff64', '#56d8c9', '#ff9b65', '#a78bfa', '#5fa8ff', '#ff7085', '#e7c86c', '#7bd88f'];
const WIDTH = 1100;
const HEIGHT = 390;
const PAD = { left: 76, right: 24, top: 24, bottom: 44 };

function money(value: number) {
  return new Intl.NumberFormat('zh-CN', { maximumFractionDigits: 0 }).format(value);
}

export function PnlChart({ curves }: { curves: PnlCurve[] }) {
  const [hoverDate, setHoverDate] = useState<string | null>(null);
  const model = useMemo(() => {
    const all = curves.flatMap((curve) => curve.points);
    if (!all.length) return null;
    const dates = [...new Set(all.map((point) => point.date))].sort();
    const dateIndex = new Map(dates.map((date, index) => [date, index]));
    const values = all.map((point) => point.cumulative_net_pnl);
    let low = Math.min(0, ...values);
    let high = Math.max(0, ...values);
    if (low === high) { low -= 1; high += 1; }
    const x = (date: string) => PAD.left + ((dateIndex.get(date) ?? 0) / Math.max(1, dates.length - 1)) * (WIDTH - PAD.left - PAD.right);
    const y = (value: number) => PAD.top + ((high - value) / (high - low)) * (HEIGHT - PAD.top - PAD.bottom);
    const paths = curves.map((curve) => ({
      id: curve.product_id,
      d: curve.points.map((point, index) => `${index ? 'L' : 'M'}${x(point.date).toFixed(2)},${y(point.cumulative_net_pnl).toFixed(2)}`).join(' '),
      values: new Map(curve.points.map((point) => [point.date, point.cumulative_net_pnl])),
    }));
    return { dates, low, high, x, y, paths };
  }, [curves]);

  if (!model) return <div className="chart-empty">所选区间没有 PnL 数据</div>;
  const hoverX = hoverDate ? model.x(hoverDate) : null;
  const hoverValues = hoverDate
    ? model.paths.map((path, index) => ({ id: path.id, value: path.values.get(hoverDate), color: COLORS[index % COLORS.length] })).filter((item) => item.value !== undefined)
    : [];

  return (
    <div className="pnl-chart" onMouseLeave={() => setHoverDate(null)}>
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label="累计净损益曲线"
        onMouseMove={(event) => {
          const rect = event.currentTarget.getBoundingClientRect();
          const local = ((event.clientX - rect.left) / rect.width) * WIDTH;
          const ratio = Math.max(0, Math.min(1, (local - PAD.left) / (WIDTH - PAD.left - PAD.right)));
          setHoverDate(model.dates[Math.round(ratio * (model.dates.length - 1))]);
        }}>
        {[0, 1, 2, 3, 4].map((step) => {
          const value = model.high - ((model.high - model.low) * step) / 4;
          const y = model.y(value);
          return <g key={step}><line className="grid-line" x1={PAD.left} x2={WIDTH - PAD.right} y1={y} y2={y} /><text className="axis-label" x={PAD.left - 10} y={y + 4} textAnchor="end">{money(value)}</text></g>;
        })}
        <line className="zero-line" x1={PAD.left} x2={WIDTH - PAD.right} y1={model.y(0)} y2={model.y(0)} />
        {model.paths.map((path, index) => <path key={path.id} d={path.d} fill="none" stroke={COLORS[index % COLORS.length]} strokeWidth={curves.length === 1 ? 2.4 : 1.5} opacity={curves.length > 8 ? .7 : .9} />)}
        <text className="axis-label" x={PAD.left} y={HEIGHT - 13}>{model.dates[0]}</text>
        <text className="axis-label" x={WIDTH - PAD.right} y={HEIGHT - 13} textAnchor="end">{model.dates.at(-1)}</text>
        {hoverDate && hoverX !== null && <g><line className="hover-line" x1={hoverX} x2={hoverX} y1={PAD.top} y2={HEIGHT - PAD.bottom} /><circle cx={hoverX} cy={model.y(hoverValues[0]?.value ?? 0)} r="4" fill={hoverValues[0]?.color} /></g>}
      </svg>
      {hoverDate && <div className="chart-tooltip"><b>{hoverDate}</b>{hoverValues.slice(0, 8).map((item) => <span key={item.id}><i style={{ background: item.color }} />{item.id}<strong>{money(item.value ?? 0)}</strong></span>)}</div>}
      <div className="chart-legend">{model.paths.map((path, index) => <span key={path.id}><i style={{ background: COLORS[index % COLORS.length] }} />{path.id}</span>)}</div>
    </div>
  );
}
