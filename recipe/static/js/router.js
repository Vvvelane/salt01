export function currentRoute() { return location.hash.split('?')[0] || '#/market'; }
export function queryState() { return Object.fromEntries(new URLSearchParams(location.hash.split('?')[1] || '')); }
export function setQuery(patch) { const next = new URLSearchParams(queryState()); Object.entries(patch).forEach(([key, value]) => value ? next.set(key, value) : next.delete(key)); location.hash = `${currentRoute()}?${next}`; }

