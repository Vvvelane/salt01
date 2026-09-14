import type { Bar } from '../types';

export type Domain = { start: number; end: number };
export function boundDomain(start: number, end: number, count: number, minimum = 14): Domain {
  const span = Math.min(count, Math.max(minimum, end - start));
  const boundedStart = Math.max(0, Math.min(Math.max(0, count - span), start));
  return { start: boundedStart, end: Math.min(count, boundedStart + span) };
}

/** Aggregate only the drawing; the cursor and drilldown still address original bars. */
export function candleBuckets(bars: Bar[], start: number, end: number, capacity = 600) {
  const stride = Math.max(1, Math.ceil((end - start) / capacity));
  const buckets: { bar: Bar; index: number; count: number }[] = [];
  for (let offset = start; offset < end; offset += stride) {
    const group = bars.slice(offset, Math.min(end, offset + stride));
    const first = group[0], last = group[group.length - 1];
    if (group.length === 1) buckets.push({ bar: first, index: offset - start, count: 1 });
    else buckets.push({ index: offset - start + (group.length - 1) / 2, count: group.length,
      bar: { ...last, ts: first.ts, open: first.open,
        high: group.reduce<number | null>((max, bar) => bar.high == null ? max : max == null ? bar.high : Math.max(max, bar.high), null),
        low: group.reduce<number | null>((min, bar) => bar.low == null ? min : min == null ? bar.low : Math.min(min, bar.low), null),
        volume: group.reduce((total, bar) => total + (bar.volume ?? 0), 0),
      },
    });
  }
  return buckets;
}
