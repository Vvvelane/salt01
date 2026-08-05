const json = async (url, options = {}) => {
  const response = await fetch(url, options);
  const body = await response.json();
  if (!response.ok) throw Object.assign(new Error(body.detail?.message || body.detail || 'Request failed'), { status: response.status, body });
  return body;
};

export const api = {
  health: () => json('/api/v1/health'),
  status: () => json('/api/v1/status'),
  catalogSummary: () => json('/api/v1/catalog/summary'),
  catalogOptions: (params = {}) => json(`/api/v1/catalog/options?${new URLSearchParams(Object.entries(params).filter(([, value]) => value))}`),
  assets: (params = {}) => json(`/api/v1/catalog/assets?${new URLSearchParams(Object.entries(params).filter(([, value]) => value))}`),
  asset: (assetId) => json(`/api/v1/catalog/assets/${encodeURIComponent(assetId)}`),
  schemas: () => json('/api/v1/catalog/schemas'),
  bars: (params) => json(`/api/v1/market/bars?${new URLSearchParams(Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== ''))}`),
  context: (params) => json(`/api/v1/market/context?${new URLSearchParams(Object.entries(params))}`),
  researchStatus: () => json('/api/v1/research/status'),
  researchRuns: () => json('/api/v1/research/runs'),
};
