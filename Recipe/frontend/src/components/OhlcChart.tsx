import { useMemo } from 'react';
import type { Bar } from '../types';

type Props = { bars: Bar[]; selected: Bar | null; onSelect: (bar: Bar) => void };

function shortDate(value: string) {
  return value.slice(5, 10).replace('-', '/');
}

export function OhlcChart({ bars, selected, onSelect }: Props) {
  const visible = bars.slice(-240);
  const geometry = useMemo(() => {
    const prices = visible.flatMap((bar) => [bar.low, bar.high]).filter((value): value is number => value !== null && Number.isFinite(value));
    const min = prices.length ? Math.min(...prices) : 0;
    const max = prices.length ? Math.max(...prices) : 1;
    const pad = (max - min || 1) * 0.08;
    return { min: min - pad, max: max + pad, range: max - min + pad * 2 || 1 };
  }, [visible]);

  if (!visible.length) return <div className="chart-empty">这个时间范围没有数据</div>;

  const width = 1100;
  const height = 430;
  const plotTop = 24;
  const plotBottom = 322;
  const volumeTop = 348;
  const volumeBottom = 408;
  const left = 60;
  const right = 18;
  const step = (width - left - right) / visible.length;
  const candleWidth = Math.max(1.5, Math.min(7, step * 0.64));
  const x = (index: number) => left + (index + 0.5) * step;
  const y = (value: number | null) => plotTop + (geometry.max - (value ?? geometry.min)) / geometry.range * (plotBottom - plotTop);
  const maxVolume = Math.max(...visible.map((bar) => bar.volume ?? 0), 1);
  const ticks = Array.from({ length: 5 }, (_, index) => geometry.max - index * geometry.range / 4);
  const dateTicks = [0, Math.floor((visible.length - 1) / 2), visible.length - 1];

  return (
    <div className="chart-wrap">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="OHLCV chart">
        {ticks.map((value) => {
          const position = y(value);
          return <g key={value}><line x1={left} y1={position} x2={width - right} y2={position} className="grid-line" /><text x={left - 10} y={position + 4} className="axis-label" textAnchor="end">{value.toFixed(2)}</text></g>;
        })}
        {visible.map((bar, index) => {
          const up = (bar.close ?? 0) >= (bar.open ?? 0);
          const isSelected = selected?.ts === bar.ts && selected?.contract === bar.contract;
          const open = y(bar.open);
          const close = y(bar.close);
          const high = y(bar.high);
          const low = y(bar.low);
          const volumeHeight = ((bar.volume ?? 0) / maxVolume) * (volumeBottom - volumeTop);
          return (
            <g key={`${bar.ts}-${bar.contract ?? index}`} className={`candle ${isSelected ? 'selected' : ''}`} onClick={() => onSelect(bar)}>
              <title>{`${bar.ts}\nO ${bar.open}  H ${bar.high}  L ${bar.low}  C ${bar.close}\nV ${bar.volume ?? '—'}  ${bar.contract ?? ''}`}</title>
              <line x1={x(index)} y1={high} x2={x(index)} y2={low} className={up ? 'up' : 'down'} />
              <rect x={x(index) - candleWidth / 2} y={Math.min(open, close)} width={candleWidth} height={Math.max(1.5, Math.abs(close - open))} className={up ? 'up-fill' : 'down-fill'} />
              <rect x={x(index) - candleWidth / 2} y={volumeBottom - volumeHeight} width={candleWidth} height={Math.max(1, volumeHeight)} className={up ? 'volume-up' : 'volume-down'} />
            </g>
          );
        })}
        <line x1={left} y1={volumeBottom} x2={width - right} y2={volumeBottom} className="axis-line" />
        {dateTicks.map((index) => <text key={index} x={x(index)} y={height - 5} className="axis-label" textAnchor={index === 0 ? 'start' : index === visible.length - 1 ? 'end' : 'middle'}>{shortDate(visible[index].ts)}</text>)}
        <text x={left} y={volumeTop - 7} className="axis-caption">VOLUME</text>
      </svg>
    </div>
  );
}
