import { api } from '../api.js';
import { MarketChart } from '../components/chart.js';
import { renderTable } from '../components/table.js';
import { showMessage, statusBadge } from '../components/status.js';
import { queryState, setQuery } from '../router.js';

const labels = { family: '数据族', exchange: '交易所', product: '品种', asset_kind: '资产', frequency: '频率' };
let chart;
let lastData;

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[char]));
const select = (key, values, value) => `<label>${labels[key]}<select data-filter="${key}"><option value="">全部</option>${values.map(item => `<option value="${esc(item)}" ${item === value ? 'selected' : ''}>${esc(item)}</option>`).join('')}</select></label>`;

async function optionsFor(filters) { const response = await api.catalogOptions(filters); return response.data || {}; }
async function loadAssets(filters) { const response = await api.assets({ ...filters, page_size: 200 }); return response.data || []; }

export async function renderMarket(root) {
  root.innerHTML = `<div class="view-head"><div><p class="eyebrow">MARKET EXPLORER</p><h2>市场路径</h2><p class="muted">浏览真实 OHLCV/OI bar；不模拟盘口或 snapshot。</p></div><div id="market-status"></div></div><section class="panel"><form id="market-filters" class="filters"></form><div class="actions"><button type="submit" form="market-filters">加载</button><button type="button" id="reset-market" class="quiet">重置</button><span id="catalog-revision" class="muted"></span></div></section><section class="market-grid"><div class="panel chart-panel"><div class="panel-title"><h3>OHLC bar path</h3><span class="badge">close ≠ mid</span></div><div class="chart-legend"><span>蜡烛：OHLC</span><span>下方：volume</span><span>橙色：symbol change observed</span></div><div class="chart-box"><canvas id="market-chart" aria-label="OHLC candle chart"></canvas></div><p id="chart-summary" class="sr-only" aria-live="polite"></p></div><aside class="panel inspector"><h3>Bar Inspector</h3><div id="bar-inspector"><p class="muted">点击一根 candle 查看 raw datetime、字段和来源。</p></div></aside></section><section class="panel"><div class="panel-title"><h3>语义边界</h3>${statusBadge('pending','time/session pending')}</div><div class="notice-grid"><p>OHLC 是时间 bar 摘要，不包含 bar 内完整路径顺序。</p><p>volume 不是订单簿深度；close 不是 mid；high/low 不是 bid/ask。</p><p>自然日不自动等同 trading_date；主要合约 symbol 变化不等于官方换月。</p></div></section>`;
  const status = document.querySelector('#market-status');
  try {
    const [summary, options] = await Promise.all([api.catalogSummary(), optionsFor({})]);
    if (summary.status !== 'ok') { status.innerHTML = showMessage('Catalog 尚未构建：运行 python -m recipe.catalog refresh。', 'catalog-unavailable'); return; }
    document.querySelector('#catalog-revision').textContent = `catalog ${summary.data.catalog_revision}`;
    const state = queryState(); const filters = { family: state.family || '', exchange: state.exchange || '', product: state.product || '', asset_kind: state.asset_kind || '', frequency: state.frequency || '' };
    await drawFilters(options, filters);
    document.querySelector('#market-filters').addEventListener('change', async event => { if (!event.target.matches('[data-filter]')) return; const key = event.target.dataset.filter; const next = { ...filters, [key]: event.target.value }; for (const downstream of ['exchange','product','asset_kind','frequency']) if (['family','exchange','product'].indexOf(key) < ['family','exchange','product'].indexOf(downstream) && key !== downstream) next[downstream] = ''; Object.assign(filters, next); setQuery(filters); await drawFilters(await optionsFor(filters), filters); });
    document.querySelector('#market-filters').addEventListener('submit', event => { event.preventDefault(); loadMarket(filters); });
    document.querySelector('#reset-market').addEventListener('click', () => { location.hash = '#/market'; });
    await loadMarket(filters);
  } catch (error) { status.innerHTML = showMessage(error.message, 'error'); }
}

async function drawFilters(options, filters) {
  const assets = await loadAssets(filters); const form = document.querySelector('#market-filters');
  form.innerHTML = `${['family','exchange','product','asset_kind','frequency'].map(key => select(key, options[key] || [], filters[key])).join('')}<label>资产<select data-filter="asset_id"><option value="">选择资产</option>${assets.map(asset => `<option value="${esc(asset.asset_id)}">${esc(asset.exchange)} · ${esc(asset.product)} · ${esc(asset.contract)} · ${esc(asset.frequency)}</option>`).join('')}</select></label><label>开始<input name="start" value="${esc(queryState().start || '')}" placeholder="YYYY-MM-DD HH:MM:SS"></label><label>结束<input name="end" value="${esc(queryState().end || '')}" placeholder="YYYY-MM-DD HH:MM:SS"></label><label class="check"><input type="checkbox" name="activity" checked> activity raw</label><label class="check"><input type="checkbox" name="position" checked> position/OI raw</label>`;
  form.querySelector('[data-filter="asset_id"]').value = queryState().asset_id || '';
  form.querySelector('[data-filter="asset_id"]').addEventListener('change', event => { setQuery({ asset_id: event.target.value }); });
}

async function loadMarket(filters) {
  const form = document.querySelector('#market-filters'); const assetId = form.querySelector('[data-filter="asset_id"]').value || queryState().asset_id; const start = form.querySelector('[name="start"]').value; const end = form.querySelector('[name="end"]').value; if (!assetId || !start || !end) { document.querySelector('#bar-inspector').innerHTML = showMessage('请选择 canonical asset，并提供 start/end。', 'pending'); return; }
  try { const fields = ['open','high','low','close','volume']; if (form.querySelector('[name="activity"]').checked) fields.push('amount','money'); if (form.querySelector('[name="position"]').checked) fields.push('position','open_interest'); const data = await api.bars({ asset_id: assetId, start, end, fields: fields.join(','), limit: 1000 }); lastData = data.data; if (!chart) chart = new MarketChart(document.querySelector('#market-chart'), inspectBar); chart.setData(lastData.bars); document.querySelector('#chart-summary').textContent = `${lastData.bars.length} bars; ${lastData.bars[0]?.timestamp || ''} to ${lastData.bars.at(-1)?.timestamp || ''}`; document.querySelector('#bar-inspector').innerHTML = showMessage('点击 candle 查看详情。', 'ok'); } catch (error) { document.querySelector('#bar-inspector').innerHTML = showMessage(error.body?.detail?.message || error.message, error.status === 413 ? 'range-too-large' : 'error'); }
}

function inspectBar(bar) { if (!bar) return; const rows = [['raw_datetime',bar.raw_datetime],['timestamp',bar.timestamp],['open',bar.open],['high',bar.high],['low',bar.low],['close',bar.close],['volume',bar.volume],['activity',`${bar.activity_raw_field || '—'}: ${bar.activity_value ?? '—'}`],['position',`${bar.position_raw_field || '—'}: ${bar.position_value ?? '—'}`],['symbol',`${bar.source_symbol} (${bar.symbol_source})`],['timezone',bar.timezone ?? 'null'],['session_id',bar.session_id ?? 'null']].map(([key,value]) => ({key,value})); document.querySelector('#bar-inspector').innerHTML = renderTable(rows, [['key','字段'],['value','值']]); }

