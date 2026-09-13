import type { BarsResponse, FactorCatalog, FactorResults, Registry, Universe } from './types';

async function get<T>(path: string): Promise<T> {
  const response = await fetch(path);
  const body = await response.json();
  if (!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : '请求失败');
  return body as T;
}

export const api = {
  universe: () => get<Universe>('/api/universe'),
  cards: () => get<Registry>('/api/cards'),
  factors: () => get<FactorCatalog>('/api/factors'),
  factorResults: (params: { strategy: string; products: string[]; start?: string; end?: string }) => {
    const query = new URLSearchParams({
      strategy: params.strategy,
      products: params.products.join(','),
    });
    if (params.start) query.set('start', params.start);
    if (params.end) query.set('end', params.end);
    return get<FactorResults>(`/api/factor-results?${query}`);
  },
  bars: (params: {
    product: string;
    start: string;
    end: string;
    freq: '1min' | 'daily';
    contract?: string;
  }) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value) query.set(key, value);
    });
    return get<BarsResponse>(`/api/bars?${query}`);
  },
};
