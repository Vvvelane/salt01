import type { ApiEnvelope, DatasetAvailability, DailyPayload, Exchange, Field, IntradayPayload, Product } from './types';

async function request<T>(url: string): Promise<ApiEnvelope<T>> {
  const response = await fetch(url);
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.detail?.message || body.detail || `Request failed: ${response.status}`);
  }
  return body as ApiEnvelope<T>;
}

export const api = {
  health: () => request<{ service: string; index: string; missing_views: string[] }>('/api/v2/health'),
  exchanges: () => request<Exchange[]>('/api/v2/catalog/exchanges'),
  products: (exchange?: string) => request<Product[]>(`/api/v2/catalog/products${exchange ? `?exchange=${encodeURIComponent(exchange)}` : ''}`),
  availability: (productId: string) => request<{ product: Product; datasets: DatasetAvailability[] }>(`/api/v2/products/${encodeURIComponent(productId)}/availability`),
  fields: (datasetKey?: string) => request<Field[]>(`/api/v2/catalog/fields${datasetKey ? `?dataset_key=${encodeURIComponent(datasetKey)}` : ''}`),
  daily: (params: { product_id: string; mode: string; start: string; end: string; contracts?: string }) => {
    const query = new URLSearchParams(params);
    return request<DailyPayload>(`/api/v2/market/daily?${query.toString()}`);
  },
  intraday: (params: { product_id: string; trading_date: string; mode?: string; contract?: string; limit?: number }) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => { if (value !== undefined && value !== '') query.set(key, String(value)); });
    return request<IntradayPayload>(`/api/v2/market/intraday?${query.toString()}`);
  },
};
