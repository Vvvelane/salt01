import { api } from '../api.js';
import { renderTable } from '../components/table.js';
import { showMessage, statusBadge } from '../components/status.js';

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[char]));
let state = { assets: [], schemas: [], selectedAsset: null, selectedSchema: null, leftSchema: '', rightSchema: '', anomalies: [] };

export async function renderDataAtlas(root) {
  root.innerHTML = `<div class="view-head"><div><p class="eyebrow">DATA ATLAS</p><h2>数据语义</h2><p class="muted">Catalog Tree、schema/field identity、能力边界和异常路径。</p></div><div id="atlas-status"></div></div><div class="atlas-grid"><aside class="panel catalog-tree"><div class="panel-title"><h3>Catalog Tree</h3><span id="asset-count"></span></div><input id="atlas-search" placeholder="搜索品种 / 合约 / 交易所" aria-label="搜索 Catalog"><div id="tree-content"></div></aside><main><section class="panel" id="asset-panel"><p class="muted">从左侧选择 canonical asset。</p></section><section class="panel" id="schema-panel"><h3>Schema Compare</h3><div id="schema-controls"></div><div id="schema-diff"></div></section><section class="panel" id="field-panel"><h3>Field Inspector</h3><div id="field-content"><p class="muted">选择 schema 查看字段语义。</p></div></section><section class="panel" id="capability-panel"><div class="panel-title"><h3>Capability Matrix</h3>${statusBadge('pending','pending 不猜测')}</div><div id="capability-content"></div></section><section class="panel"><h3>异常路径</h3><div id="anomaly-content"></div></section></main></div>`;
  try {
    const [summary, assets, schemas, anomalies] = await Promise.all([api.catalogSummary(), api.assets({ page_size: 200 }), api.schemas(), api.catalogOptions({}), fetch('/api/v1/catalog/anomalies').then(response => response.json())]);
    if (summary.status !== 'ok') { document.querySelector('#atlas-status').innerHTML = showMessage('Catalog 尚未构建。', 'catalog-unavailable'); return; }
    state = { assets: assets.data || [], schemas: schemas.data || [], selectedAsset: null, selectedSchema: null, leftSchema: '', rightSchema: '', anomalies: anomalies.data || [] };
    document.querySelector('#asset-count').textContent = `${summary.data.file_count} files`;
    renderTree(); renderSchemaControls(); renderAnomalies();
    document.querySelector('#atlas-search').addEventListener('input', renderTree);
  } catch (error) { document.querySelector('#atlas-status').innerHTML = showMessage(error.message, 'error'); }
}

function renderTree() {
  const term = document.querySelector('#atlas-search').value.toLowerCase(); const groups = {};
  state.assets.filter(asset => `${asset.exchange} ${asset.product} ${asset.contract} ${asset.family}`.toLowerCase().includes(term)).forEach(asset => { const key = `${asset.family} / ${asset.frequency} / ${asset.exchange}`; (groups[key] ||= []).push(asset); });
  document.querySelector('#tree-content').innerHTML = Object.entries(groups).slice(0, 80).map(([key, assets]) => `<details open><summary>${esc(key)} <span class="muted">(${assets.length})</span></summary><div class="tree-leaves">${assets.slice(0, 40).map(asset => `<button class="tree-item" data-asset="${asset.asset_id}">${esc(asset.product)} · ${esc(asset.contract)} ${statusBadge('confirmed', asset.asset_kind)}</button>`).join('')}${assets.length > 40 ? '<span class="muted">更多结果请缩小搜索</span>' : ''}</div></details>`).join('') || '<p class="muted">没有匹配的 asset。</p>';
  document.querySelectorAll('[data-asset]').forEach(button => button.addEventListener('click', () => selectAsset(button.dataset.asset)));
}

async function selectAsset(assetId) {
  try { const response = await api.asset(assetId); state.selectedAsset = response.data; state.selectedSchema = state.schemas.find(schema => schema.schema_id === state.selectedAsset.schema_id) || null; renderAsset(); renderCapabilities(); if (state.selectedSchema) renderFields(state.selectedSchema); } catch (error) { document.querySelector('#asset-panel').innerHTML = showMessage(error.message, 'error'); }
}

function renderAsset() {
  const asset = state.selectedAsset; const file = asset.file || {}; document.querySelector('#asset-panel').innerHTML = `<div class="panel-title"><h3>Asset</h3>${statusBadge(asset.asset_kind === 'contract' ? 'confirmed' : 'pending', asset.asset_kind)}</div>${renderTable(Object.entries({asset_id:asset.asset_id,family:asset.family,frequency:asset.frequency,exchange:asset.exchange,product:asset.product,contract:asset.contract,canonical_relative_path:file.relative_path,schema_id:asset.schema_id || 'schema_deferred',header_fingerprint:file.header_fingerprint || 'deferred',field_set_fingerprint:file.field_set_fingerprint || 'deferred',size_bytes:file.size_bytes,first_raw_datetime:file.first_raw_datetime,last_raw_datetime:file.last_raw_datetime,source_symbol:asset.asset_kind === 'contract' ? 'path-derived or row' : 'row/path'}, ([key,value]) => ({key,value})), [['key','属性'],['value','值']])}`;
}

function renderSchemaControls() { document.querySelector('#schema-controls').innerHTML = `<label>左 schema <select id="schema-left"><option value="">选择</option>${state.schemas.map(schema => `<option value="${schema.schema_id}">${schema.label} · ${schema.schema_id.slice(0,8)}</option>`).join('')}</select></label> <label>右 schema <select id="schema-right"><option value="">选择</option>${state.schemas.map(schema => `<option value="${schema.schema_id}">${schema.label} · ${schema.schema_id.slice(0,8)}</option>`).join('')}</select></label>`; document.querySelector('#schema-left').addEventListener('change', event => { state.leftSchema = event.target.value; renderDiff(); }); document.querySelector('#schema-right').addEventListener('change', event => { state.rightSchema = event.target.value; renderDiff(); }); }

function renderDiff() { const left = state.schemas.find(schema => schema.schema_id === state.leftSchema), right = state.schemas.find(schema => schema.schema_id === state.rightSchema); if (!left || !right) { document.querySelector('#schema-diff').innerHTML = '<p class="muted">选择两个 schema 比较列集合、列顺序和同义候选。</p>'; return; } const leftSet = new Set(left.ordered_fields), rightSet = new Set(right.ordered_fields); document.querySelector('#schema-diff').innerHTML = renderTable([{key:'共有字段',value:[...leftSet].filter(field => rightSet.has(field)).join(', ') || '—'},{key:'仅左侧',value:[...leftSet].filter(field => !rightSet.has(field)).join(', ') || '—'},{key:'仅右侧',value:[...rightSet].filter(field => !leftSet.has(field)).join(', ') || '—'},{key:'列顺序',value:JSON.stringify(left.ordered_fields) === JSON.stringify(right.ordered_fields) ? 'same' : 'different'},{key:'同义候选',value:'amount ↔ money；position ↔ open_interest（只提示，不合并）'},{key:'identity source',value:'row symbol vs path-derived contract'}], [['key','比较项'],['value','结果']]); }

function renderFields(schema) { document.querySelector('#field-content').innerHTML = renderTable(schema.fields || [], [['raw_field','raw field'],['display_name','display'],['semantic_status','status'],['economic_identity','identity'],['aggregation_note','aggregation'],['warning','warning']], 'This schema has deferred field semantics.'); document.querySelector('#field-panel h3').textContent = `Field Inspector · ${schema.label}`; }
function renderCapabilities() { const capabilities = state.selectedAsset?.capability || {}; document.querySelector('#capability-content').innerHTML = renderTable(Object.entries(capabilities).map(([key,value]) => ({key,value})), [['key','capability'],['value','status']]); }
function renderAnomalies() { const rows = state.anomalies.slice(0, 100).map(item => ({relative_path:item.relative_path,status:item.status,warnings:item.warnings?.join(', ') || '—'})); document.querySelector('#anomaly-content').innerHTML = renderTable(rows, [['relative_path','relative path'],['status','status'],['warnings','warnings']], 'No anomaly records in current page.'); }

