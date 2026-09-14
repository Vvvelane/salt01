import type { BarsResponse, Registry, Universe, ResearchCatalog, ResearchResults, Replay, DatabaseOverview, DatabaseFiles, DatabaseObservation } from './types';

// Set only by the Cloudflare Pages build (see Recipe/README.md). Local dev and
// the local `uvicorn` build both stay dynamic and hit /api as before.
export const STATIC_MODE = import.meta.env?.VITE_STATIC === 'true';

export type Manifest = { commit: string; generated_at: string; strategies: string[] };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  const body = await response.json();
  if (!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : 'Request failed');
  return body as T;
}
const get = <T>(path: string, signal?: AbortSignal) => request<T>(path, { signal });
const send = <T>(path: string, method: 'POST' | 'DELETE', body?: unknown) =>
  request<T>(path, body ? { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) } : { method });
export type BarQuery = { product: string; freq: '1min' | 'daily'; contract?: string; anchor?: string; before?: string; after?: string; limit?: number };
export const api = {
  manifest: (signal?: AbortSignal) => get<Manifest>('/data/manifest.json', signal),
  databaseOverview: (signal?: AbortSignal) =>
    STATIC_MODE ? get<DatabaseOverview>('/data/database/overview.json', signal) : get<DatabaseOverview>('/api/database/overview', signal),
  databaseFiles: (domain: string, offset: number, signal?: AbortSignal) =>
    get<DatabaseFiles>(`/api/database/files?${new URLSearchParams({ domain, offset: String(offset), limit: '60' })}`, signal),
  startDatabaseObservation: (relativePath: string) => send<DatabaseObservation>('/api/database/observations', 'POST', { relative_path: relativePath }),
  databaseObservation: (id: string, signal?: AbortSignal) => get<DatabaseObservation>(`/api/database/observations/${encodeURIComponent(id)}`, signal),
  cancelDatabaseObservation: (id: string) => send<DatabaseObservation>(`/api/database/observations/${encodeURIComponent(id)}`, 'DELETE'),
  universe: () => get<Universe>('/api/universe'),
  cards: () => (STATIC_MODE ? get<Registry>('/data/cards.json') : get<Registry>('/api/cards')),
  research: () => (STATIC_MODE ? get<ResearchCatalog>('/data/research.json') : get<ResearchCatalog>('/api/research')),
  replay: (strategy: string, signal?: AbortSignal) =>
    STATIC_MODE
      ? get<Replay>(`/data/replay/${encodeURIComponent(strategy)}.json`, signal)
      : get<Replay>(`/api/replay?strategy=${encodeURIComponent(strategy)}`, signal),
  results: (strategy: string, signal?: AbortSignal) =>
    STATIC_MODE
      ? get<ResearchResults>(`/data/results/${encodeURIComponent(strategy)}.json`, signal)
      : get<ResearchResults>(`/api/results?strategy=${encodeURIComponent(strategy)}`, signal),
  contracts: (product: string, signal?: AbortSignal) => get<{ contracts: { contract: string; start: string; end: string }[] }>(`/api/contracts?product=${encodeURIComponent(product)}`, signal),
  bars: (params: BarQuery, signal?: AbortSignal) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => { if (value) query.set(key, String(value)); });
    return get<BarsResponse>(`/api/bars?${query}`, signal);
  },
};
