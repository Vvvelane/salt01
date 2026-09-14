import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { CSSProperties } from 'react';
import { api } from '../api';
import { useLanguage } from '../i18n';
import { shortName, TYPE_LABEL } from '../structure';
import type { Registry } from '../types';
import { Decks, originOf, Sigil } from '../components/idea-room/Decks';
import type { CardOrigin } from '../components/idea-room/Decks';
import { Keeper } from '../components/idea-room/Keeper';
import { NeuralGraph } from '../components/idea-room/NeuralGraph';
import { IdeaDialog } from '../components/idea-room/IdeaDialog';
import { buildIdeaModel } from '../components/idea-room/model';
import '../components/idea-room/idea-room.css';

export function Tree({ onResults }: { onResults: (strategy: string) => void }) {
  const { t, language } = useLanguage();
  const [registry, setRegistry] = useState<Registry | null>(null);
  const [error, setError] = useState('');
  const [request, setRequest] = useState(0);
  const [network, setNetwork] = useState(false);
  const [activeFamily, setActiveFamily] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [history, setHistory] = useState<string[]>([]);
  const [origin, setOrigin] = useState<CardOrigin>();
  const roomRef = useRef<HTMLElement>(null);
  const model = useMemo(() => registry ? buildIdeaModel(registry) : null, [registry]);
  useEffect(() => {
    let cancelled = false; setError('');
    api.cards().then((data) => { if (!cancelled) setRegistry(data); }).catch((reason) => { if (!cancelled) setError(String(reason)); });
    return () => { cancelled = true; };
  }, [request]);
  useEffect(() => {
    const element = roomRef.current;
    if (!element) return;
    const resize = () => element.style.setProperty('--room-height', `${Math.max(430, window.innerHeight - element.getBoundingClientRect().top)}px`);
    resize(); window.addEventListener('resize', resize);
    const header = document.querySelector('.topbar');
    const observer = new ResizeObserver(resize);
    if (header) observer.observe(header);
    return () => { window.removeEventListener('resize', resize); observer.disconnect(); };
  }, [Boolean(model)]);
  useEffect(() => {
    const key = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !history.length) { setHoveredId(null); setActiveFamily(null); }
    };
    window.addEventListener('keydown', key);
    return () => window.removeEventListener('keydown', key);
  }, [history.length]);
  const open = useCallback((id: string, entry?: CardOrigin) => {
    const node = model?.byId.get(id);
    if (!node) return;
    setOrigin(entry); setSelectedId(id); setHistory([id]); setHoveredId(null);
    if (node.family) setActiveFamily(node.family.family_id);
  }, [model]);
  const navigate = (id: string) => {
    const node = model?.byId.get(id);
    if (!node) return;
    setHistory((old) => old[old.length - 1] === id ? old : [...old, id]); setSelectedId(id);
    if (node.family) setActiveFamily(node.family.family_id);
  };
  const back = () => {
    const previous = history[history.length - 2];
    if (previous) { setHistory(history.slice(0, -1)); setSelectedId(previous); const family = model?.byId.get(previous)?.family; if (family) setActiveFamily(family.family_id); }
  };
  const toggle = () => {
    if (activeFamily && selectedId && model?.byId.get(selectedId)?.family?.family_id !== activeFamily) setSelectedId(activeFamily);
    setNetwork((old) => !old); setHoveredId(null);
  };

  if (!registry || !model) return <div className="room-loading"><span className="room-eyebrow">NaCl / RESEARCH ARCHIVE</span>{error ? <><p>{error}</p><button onClick={() => setRequest((old) => old + 1)}>{t('重试', 'Retry')}</button></> : <p>{t('正在读取研究卡片…', 'Loading research cards…')}</p>}</div>;
  const hover = hoveredId ? model.byId.get(hoveredId) : null;
  const modalNode = history.length ? model.byId.get(history[history.length - 1]) : null;
  const hoveredDeckIndex = model.decks.findIndex((deck) => deck.family.family_id === hover?.family?.family_id);
  return <section ref={roomRef} className={`idea-room${network ? ' mode-network' : ' mode-decks'}${activeFamily ? ' family-open' : ''}`} aria-label={t('因子研究空间', 'Factor research room')}>
    <div className="room-atmosphere" aria-hidden="true"><div className="room-halo"/><div className="room-starfield"/><div className="room-floor"/><div className="room-floor-ring ring-outer"/><div className="room-floor-ring ring-inner"/></div>
    <header className="room-header">
      <div className="room-title"><span className="room-eyebrow">NaCl <i /> THE RESEARCH COLLECTION</span><h1>{network ? t('因子星图', 'The constellation') : t('灵感藏馆', 'The idea archive')}</h1><span className="room-collection-count">{String(registry.cards.length).padStart(2, '0')} {t('张卡片', 'CARDS')} <i /> {String(model.decks.length).padStart(2, '0')} {t('个家族', 'FAMILIES')}</span></div>
    </header>
    {network ? <NeuralGraph model={model} selectedId={selectedId} hoveredId={hoveredId} activeFamily={activeFamily} paused={Boolean(modalNode)} onHover={setHoveredId} onOpen={open}/>
      : <Decks model={model} selectedId={selectedId} hoveredId={hoveredId} paused={Boolean(modalNode)} onFamily={(id) => { setActiveFamily(id); setHoveredId(null); }} onHover={setHoveredId} onOpen={open}/>}
    <Keeper network={network} onToggle={toggle} label={network ? t('返回藏馆', 'Return to the archive') : t('唤起星图', 'Reveal the constellation')} />
    {hover && !modalNode && <aside className="room-preview" key={hover.id} style={{ '--deck-color': hover.color } as CSSProperties} aria-live="polite">
      <div className="preview-heading"><span>{hover.id}</span><span>{hover.practiced > 0 && <i className="practice-dot"/>}{hover.card ? t(TYPE_LABEL[hover.card.structure.type]) : hover.kind === 'family' ? t('因子家族', 'FACTOR FAMILY') : t('因子表达', 'EXPRESSION')}</span></div>
      <div className="preview-body"><div><h2>{hover.card ? shortName(hover.card, language) : hover.expression ? t(hover.expression.name) : t(hover.family?.name, hover.family?.name_en)}</h2><p>{hover.card ? t(hover.card.idea_summary) : hover.expression ? t(hover.expression.description) : t(hover.family?.core_mechanism)}</p></div><Sigil index={Math.max(0, hoveredDeckIndex)}/></div>
      <footer><span>{hover.family?.family_id}{hover.expression ? ` / ${hover.expression.expression_id}` : ''}</span><span aria-hidden="true">↗</span></footer>
    </aside>}
    <footer className="room-footer"><span className="room-mode"><i /> {network ? '02 / CONSTELLATION' : '01 / ARCHIVE'}</span><span className="room-gesture-hint">{network ? t('拖动平移 · 滚动缩放 · 点击选卡', 'Drag to pan · Scroll to zoom · Click to open') : t('靠近卡堆展开 · 点击角色切换视图', 'Hover a deck to fan · Select the archivist to switch views')}</span><button className="room-framework" onClick={(e) => open('ROOT', originOf(e.currentTarget))}>{t('研究框架', 'Framework')} <span aria-hidden="true">↗</span></button></footer>
    {modalNode && <IdeaDialog onResults={onResults} node={modalNode} registry={registry} model={model} origin={origin} canBack={history.length > 1} onBack={back} onSelect={navigate} onClose={() => { setHistory([]); setHoveredId(null); }}/>}
  </section>;
}
