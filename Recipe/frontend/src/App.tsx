import { useState } from 'react';
import { Factors } from './views/Factors';
import { Database } from './views/Database';
import { Tree } from './views/Tree';
import { useLanguage } from './i18n';

type Page = 'database' | 'tree' | 'factors';

export function App() {
  const { language, toggleLanguage, t } = useLanguage();
  const [page, setPage] = useState<Page>('database');
  const [resultStrategy, setResultStrategy] = useState<string>();
  const openResults = (strategy?: string) => { setResultStrategy(strategy); setPage('factors'); };
  return (
    <div className="app-shell">
      <header className="topbar">
        <button className="brand" onClick={() => setPage('database')}>
          <span className="brand-mark">S</span>
          <span><b>SALT</b><small>RESEARCH TERMINAL</small></span>
        </button>
        <nav aria-label={t('主导航')}>
          <button className={page === 'database' ? 'active' : ''} onClick={() => setPage('database')}>{t('数据档案库', 'Database Management')}</button>
          <button className={page === 'tree' ? 'active' : ''} onClick={() => setPage('tree')}>{t('因子树', 'Factor Tree')}</button>
          <button className={page === 'factors' ? 'active' : ''} onClick={() => openResults()}>{t('因子结果', 'Factor Results')}</button>
        </nav>
        <div className="topbar-actions"><div className="phase-badge"><span /> Phase 1 · Local</div><button className="language-toggle" onClick={toggleLanguage} aria-label={language === 'en' ? 'Switch to normal mode' : '切换为全英文'} aria-pressed={language === 'en'}>{language === 'en' ? 'Normal mode' : 'English'}</button></div>
      </header>
      <main>
        {page === 'database' && <Database />}
        {page === 'tree' && <Tree onResults={openResults} />}
        {page === 'factors' && <Factors key={resultStrategy ?? "collection"} initialStrategy={resultStrategy} />}
      </main>
    </div>
  );
}
