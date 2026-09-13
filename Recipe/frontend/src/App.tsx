import { useState } from 'react';
import { Cards } from './views/Cards';
import { Factors } from './views/Factors';
import { Market } from './views/Market';
import { Tree } from './views/Tree';

type Page = 'market' | 'tree' | 'cards' | 'factors';

export function App() {
  const [page, setPage] = useState<Page>('market');
  const [focusCard, setFocusCard] = useState<string | null>(null);
  function openCard(factorId: string) {
    setFocusCard(factorId);
    setPage('cards');
  }
  return (
    <div className="app-shell">
      <header className="topbar">
        <button className="brand" onClick={() => setPage('market')}>
          <span className="brand-mark">S</span>
          <span><b>SALT</b><small>RESEARCH TERMINAL</small></span>
        </button>
        <nav aria-label="主导航">
          <button className={page === 'market' ? 'active' : ''} onClick={() => setPage('market')}>Market Data</button>
          <button className={page === 'tree' ? 'active' : ''} onClick={() => setPage('tree')}>Factor Tree</button>
          <button className={page === 'cards' ? 'active' : ''} onClick={() => setPage('cards')}>NaCl Registry</button>
          <button className={page === 'factors' ? 'active' : ''} onClick={() => setPage('factors')}>Factor Results</button>
        </nav>
        <div className="phase-badge"><span /> Phase 1 · Local</div>
      </header>
      <main>
        {page === 'market' && <Market />}
        {page === 'tree' && <Tree onOpenCard={openCard} />}
        {page === 'cards' && <Cards focusId={focusCard} />}
        {page === 'factors' && <Factors />}
      </main>
    </div>
  );
}
