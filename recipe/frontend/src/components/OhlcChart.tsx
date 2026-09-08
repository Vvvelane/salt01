import { useMemo } from 'react';
import type { Bar } from '../types';

type Props = { bars: Bar[]; onSelect: (bar: Bar) => void };

export function OhlcChart({ bars, onSelect }: Props) {
  const visible = bars.slice(-360);
  const geometry = useMemo(() => {
    const values = visible.flatMap((bar) => [bar.low, bar.high]).filter((value): value is number => Number.isFinite(value));
    const min = Math.min(...values, 0);
    const max = Math.max(...values, 1);
    return { min, range: max - min || 1 };
  }, [visible]);

  if (!visible.length) return <div className="chart-empty">当前区间没有行情数据。</div>;
  const width = Math.max(900, visible.length * 7);
  const height = 380;
  const priceHeight = 280;
  const x = (index: number) => 12 + index * ((width - 24) / visible.length) + 3;
  const y = (value: number | null, heightLimit = priceHeight) => 12 + (1 - ((value ?? geometry.min) - geometry.min) / geometry.range) * (heightLimit - 24);
  const maxVolume = Math.max(...visible.map((bar) => Number(bar.volume) || 0), 1);

  return (
    <div className="chart-scroll">
      <svg className="ohlc-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Daily OHLC chart">
        <line x1="0" y1={priceHeight} x2={width} y2={priceHeight} className="chart-axis" />
        {visible.map((bar, index) => {
          const open = y(bar.open);
          const close = y(bar.close);
          const high = y(bar.high);
          const low = y(bar.low);
          const up = Number(bar.close) >= Number(bar.open);
          const previous = visible[index - 1];
          const roll = Boolean(previous?.contract_code && bar.contract_code && previous.contract_code !== bar.contract_code);
          const barWidth = Math.max(2, (width - 24) / visible.length * 0.62);
          return (
            <g key={`${bar.timestamp}-${index}`} onClick={() => onSelect(bar)} className="chart-bar">
              {roll && <rect x={x(index) - 2} y="0" width="4" height={priceHeight} className="roll-marker" />}
              <line x1={x(index)} y1={high} x2={x(index)} y2={low} className={up ? 'candle-up' : 'candle-down'} />
              <rect x={x(index) - barWidth / 2} y={Math.min(open, close)} width={barWidth} height={Math.max(2, Math.abs(close - open))} className={up ? 'candle-up-fill' : 'candle-down-fill'} />
              <rect x={x(index) - barWidth / 2} y={height - 12 - (Number(bar.volume) || 0) / maxVolume * 75} width={barWidth} height={(Number(bar.volume) || 0) / maxVolume * 75} className="volume-bar" />
            </g>
          );
        })}
      </svg>
    </div>
  );
}
