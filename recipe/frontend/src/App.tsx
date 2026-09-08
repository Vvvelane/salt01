import { useEffect, useState } from 'react';
import { Atlas } from './views/Atlas';
import { Research } from './views/Research';
import { Workbench } from './views/Workbench';

type Route = 'workbench' | 'atlas' | 'research';
function route(): Route { const value = window.location.hash.replace('#/', ''); return value === 'atlas' || value === 'research' ? value : 'workbench'; }

export function App() {
  const [current, setCurrent] = useState<Route>(route());
  useEffect(() => { const listener = () => setCurrent(route()); window.addEventListener('hashchange', listener); return () => window.removeEventListener('hashchange', listener); }, []);
  const links: [Route, string][] = [['workbench', '品种工作台'], ['atlas', '数据目录'], ['research', 'Research']];
  return <div className="shell"><header className="app-header"><div><div className="eyebrow">SALT01 · RECIPE</div><div className="brand">量化数据工作台</div></div><span className="readonly">READ ONLY</span></header><nav className="nav">{links.map(([value, label]) => <a key={value} href={`#/${value}`} className={current === value ? 'active' : ''}>{label}</a>)}</nav><main>{current === 'workbench' && <Workbench />}{current === 'atlas' && <Atlas />}{current === 'research' && <Research />}</main><footer>Recipe 只读消费 DuckDB Catalog · 不修改原始行情</footer></div>;
}
