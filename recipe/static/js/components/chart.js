// A small dependency-free Canvas renderer keeps the chart usable when the
// optional vendored ECharts bundle is not present. The data contract is the
// same: this is OHLC, not L2, bid/ask, mid, or snapshot data.
export class MarketChart {
  constructor(canvas, onSelect) {
    this.canvas = canvas; this.ctx = canvas.getContext('2d'); this.onSelect = onSelect;
    this.bars = []; this.offset = 0; this.zoom = 1; this.hover = null;
    canvas.addEventListener('mousemove', event => this.move(event));
    canvas.addEventListener('click', () => this.hover && this.onSelect(this.bars[this.hover.index]));
    canvas.addEventListener('wheel', event => { event.preventDefault(); this.zoom = Math.max(1, Math.min(8, this.zoom * (event.deltaY < 0 ? 1.15 : .87))); this.draw(); }, { passive: false });
    canvas.addEventListener('pointerdown', event => { this.drag = event.clientX; canvas.setPointerCapture(event.pointerId); });
    canvas.addEventListener('pointermove', event => { if (this.drag !== undefined) { this.offset += event.clientX - this.drag; this.drag = event.clientX; this.draw(); } });
    canvas.addEventListener('pointerup', () => { this.drag = undefined; });
    this.resizeObserver = new ResizeObserver(() => this.resize()); this.resizeObserver.observe(canvas.parentElement || canvas);
    this.resize();
  }
  setData(bars) { this.bars = bars || []; this.draw(); }
  resize() { const ratio = devicePixelRatio || 1; const rect = this.canvas.getBoundingClientRect(); this.canvas.width = Math.max(1, rect.width * ratio); this.canvas.height = Math.max(1, rect.height * ratio); this.ctx.setTransform(ratio, 0, 0, ratio, 0, 0); this.draw(); }
  visible() { const width = this.canvas.clientWidth || 800; const count = Math.max(1, Math.floor(width / 12 / this.zoom)); const end = this.bars.length; const start = Math.max(0, end - count + Math.round(this.offset / 12)); return this.bars.slice(start, Math.min(end, start + count)); }
  move(event) { const rect = this.canvas.getBoundingClientRect(); const visible = this.visible(); const index = Math.floor((event.clientX - rect.left) / Math.max(1, rect.width / Math.max(1, visible.length))); this.hover = visible[index] ? { index: this.bars.indexOf(visible[index]), x: event.clientX - rect.left, y: event.clientY - rect.top } : null; this.draw(); }
  draw() {
    const ctx = this.ctx, width = this.canvas.clientWidth || 800, height = this.canvas.clientHeight || 360; ctx.clearRect(0, 0, width, height); ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, width, height);
    const bars = this.visible(); if (!bars.length) { ctx.fillStyle = '#65727e'; ctx.fillText('No bars in selected range', 16, 28); return; }
    const prices = bars.flatMap(bar => [Number(bar.low), Number(bar.high)]).filter(Number.isFinite); const min = Math.min(...prices), max = Math.max(...prices), range = max - min || 1; const chartHeight = height * .72; const gap = width / bars.length; const candleWidth = Math.max(2, gap * .55);
    const y = value => chartHeight - ((Number(value) - min) / range) * (chartHeight - 18) + 8;
    bars.forEach((bar, i) => { const x = i * gap + gap / 2; const open = y(bar.open), close = y(bar.close), high = y(bar.high), low = y(bar.low); const up = Number(bar.close) >= Number(bar.open); ctx.strokeStyle = up ? '#13795b' : '#c2414d'; ctx.fillStyle = ctx.strokeStyle; ctx.beginPath(); ctx.moveTo(x, high); ctx.lineTo(x, low); ctx.stroke(); ctx.fillRect(x - candleWidth / 2, Math.min(open, close), candleWidth, Math.max(1, Math.abs(close - open))); if (this.bars.indexOf(bar) !== -1 && this.bars.indexOf(bar) > 0 && bar.source_symbol !== this.bars[this.bars.indexOf(bar)-1].source_symbol) { ctx.fillStyle = '#d97706'; ctx.fillRect(x - 2, 0, 4, chartHeight); } });
    ctx.strokeStyle = '#d9e0e6'; ctx.beginPath(); ctx.moveTo(0, chartHeight); ctx.lineTo(width, chartHeight); ctx.stroke(); const maxVolume = Math.max(...bars.map(bar => Number(bar.volume) || 0), 1); bars.forEach((bar, i) => { ctx.fillStyle = '#9bb7c9'; const barHeight = ((Number(bar.volume) || 0) / maxVolume) * (height - chartHeight - 18); ctx.fillRect(i * gap + 1, height - barHeight, Math.max(1, gap - 2), barHeight); });
    if (this.hover && this.hover.index !== undefined) { const bar = this.bars[this.hover.index]; const local = bars.indexOf(bar); if (local >= 0) { const x = local * gap + gap / 2; ctx.strokeStyle = '#4d6475'; ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, height); ctx.stroke(); ctx.fillStyle = '#17212b'; ctx.fillText(`${bar.raw_datetime}  O ${bar.open} H ${bar.high} L ${bar.low} C ${bar.close}`, Math.min(x + 6, width - 270), 16); } }
  }
  dispose() { this.resizeObserver?.disconnect(); this.canvas.replaceWith(this.canvas.cloneNode(true)); }
}

