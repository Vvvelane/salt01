import { useEffect, useRef, useState } from 'react';
import type { CSSProperties } from 'react';
import { useLanguage } from '../../i18n';
import { shortName } from '../../structure';
import type { IdeaModel } from './model';

export type CardOrigin = { x: number; y: number; width: number };
export function originOf(element: HTMLElement): CardOrigin {
  const rect = element.getBoundingClientRect();
  return { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2, width: rect.width };
}

export function Sigil({ index = 0 }: { index?: number }) {
  return <svg viewBox="0 0 100 100" fill="none" aria-hidden="true" className="card-sigil">
    <circle cx="50" cy="50" r="34" stroke="currentColor" strokeOpacity=".23" />
    <circle cx="50" cy="50" r="27" stroke="currentColor" strokeOpacity=".16" strokeDasharray="2 5" />
    <g transform={`rotate(${index * 20} 50 50)`}>
      {Array.from({ length: 3 + index % 4 }, (_, i) => <path key={i} transform={`rotate(${i * 360 / (3 + index % 4)} 50 50)`} d="M50 20 59 43 50 50 41 43Z" stroke="currentColor" strokeWidth=".8" fill="currentColor" fillOpacity=".06" />)}
    </g>
    <path d="m50 41 9 9-9 9-9-9Z" stroke="currentColor" /><circle cx="50" cy="50" r="2" fill="currentColor" />
    <path d="M50 10v5m0 70v5M10 50h5m70 0h5" stroke="currentColor" strokeOpacity=".5" />
  </svg>;
}

export function Decks({ model, selectedId, hoveredId, paused, onFamily, onHover, onOpen }: {
  model: IdeaModel; selectedId: string | null; hoveredId: string | null; paused: boolean;
  onFamily: (id: string | null) => void; onHover: (id: string | null) => void;
  onOpen: (id: string, origin?: CardOrigin) => void;
}) {
  const { t, language } = useLanguage();
  const regionRef = useRef<HTMLDivElement>(null);
  const handRef = useRef<HTMLDivElement>(null);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pointerInside = useRef(false);
  const live = useRef({ paused, onHover });
  live.current = { paused, onHover };
  const [expandedFamily, setExpandedFamily] = useState<string | null>(null);
  const [width, setWidth] = useState(1000);
  const cancelClose = () => { if (closeTimer.current !== null) clearTimeout(closeTimer.current); closeTimer.current = null; };
  const collapse = () => { cancelClose(); setExpandedFamily(null); live.current.onHover(null); };
  const expand = (id: string) => { cancelClose(); setExpandedFamily(id); onFamily(id); };
  const isCardRegion = (target: EventTarget | null) => target instanceof Element
    && Boolean(target.closest('.family-pile, .idea-card-slot, .deck-caption'))
    && Boolean(regionRef.current?.contains(target));
  const leaveRegion = () => {
    pointerInside.current = false;
    cancelClose();
    // Allow the short journey from a pile to its fanned cards without pinning the hand open.
    closeTimer.current = setTimeout(() => { if (!live.current.paused && !pointerInside.current) collapse(); }, 150);
  };
  useEffect(() => {
    const outside = (event: PointerEvent) => {
      if (!live.current.paused && !regionRef.current?.contains(event.target as Node)) collapse();
    };
    const escape = (event: KeyboardEvent) => { if (event.key === 'Escape' && !live.current.paused) collapse(); };
    document.addEventListener('pointerdown', outside);
    document.addEventListener('keydown', escape);
    return () => { cancelClose(); document.removeEventListener('pointerdown', outside); document.removeEventListener('keydown', escape); };
  }, []);
  useEffect(() => {
    if (!paused && !pointerInside.current) collapse();
  }, [paused]);
  useEffect(() => {
    const element = handRef.current;
    if (!element) return;
    const observer = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width));
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  const deck = model.decks.find((item) => item.family.family_id === expandedFamily);
  const index = model.decks.indexOf(deck!);
  const spread = deck ? Math.min(78, Math.max(width <= 650 ? 45 : 0, (width - 126) / Math.max(1, deck.cards.length - 1))) : 0;
  const fanWidth = deck ? Math.max(width, (deck.cards.length - 1) * spread + 126) : width;

  return <div ref={regionRef} className={`room-decks${deck ? ' has-hand' : ''}`}
    onPointerOver={(event) => { if (event.pointerType !== 'touch' && isCardRegion(event.target)) { pointerInside.current = true; cancelClose(); } }}
    onPointerOut={(event) => { if (event.pointerType !== 'touch' && !isCardRegion(event.relatedTarget)) leaveRegion(); }}
    onBlur={(event) => { if (!event.currentTarget.contains(event.relatedTarget) && !pointerInside.current && !paused) collapse(); }}>
    {deck && <div className="deck-caption" key={deck.family.family_id} style={{ '--deck-color': deck.color } as CSSProperties}>
      <span className="room-eyebrow">{deck.family.family_id} <i /> {String(index + 1).padStart(2, '0')} / {String(model.decks.length).padStart(2, '0')}</span>
      <button onClick={(e) => onOpen(deck.family.family_id, originOf(e.currentTarget))}>{t(deck.family.name, deck.family.name_en)} <span aria-hidden="true">↗</span></button>
      <span>{deck.cards.length} {t('张研究卡片', 'research cards')} · {deck.family.expressions.length} {t('种表达', 'expressions')}</span>
    </div>}
    <div ref={handRef} className="room-hand" aria-label={t('研究卡片', 'Research cards')}>
      {deck && <div className="hand-fan" key={deck.family.family_id} style={{ '--deck-color': deck.color, width: fanWidth } as CSSProperties}>
        {deck.cards.map((card, i) => {
          const offset = i - (deck.cards.length - 1) / 2;
          const angle = offset * Math.min(3.6, 28 / deck.cards.length);
          const node = model.byId.get(card.factor_id)!;
          const focused = hoveredId === card.factor_id;
          return <div key={card.factor_id} className={`idea-card-slot${focused ? ' is-hovered' : ''}`}
            style={{ '--card-x': `${offset * spread}px`, '--card-y': `${Math.abs(offset) ** 1.6 * 1.2}px`, '--card-angle': `${angle}deg`, '--card-order': i } as CSSProperties}
            onPointerEnter={() => onHover(card.factor_id)} onPointerLeave={() => onHover(null)}>
            <button className={`idea-card-back${focused ? ' is-hovered' : ''}${selectedId === card.factor_id ? ' is-selected' : ''}${node.practiced ? ' is-practiced' : ''}`}
            aria-label={`${card.factor_id} · ${shortName(card, language)}`}
            onFocus={() => onHover(card.factor_id)} onBlur={() => onHover(null)}
            onClick={(e) => onOpen(card.factor_id, originOf(e.currentTarget))}>
            <span className="card-edition">NaCl <i className={node.practiced ? 'practice-dot' : ''} /></span>
            <Sigil index={index} />
            <b>{card.factor_id}</b>
            <span className="card-expression">{card.expression}</span>
            <span className="card-bottom-line" />
          </button></div>;
        })}
      </div>}
    </div>
    <div className="room-deck-shelf" aria-label={t('因子家族', 'Factor families')}>
      {model.decks.map((item, i) => <button key={item.family.family_id}
        className={`family-pile${item.practiced ? ' is-practiced' : ''}${expandedFamily === item.family.family_id ? ' is-active' : ''}`}
        style={{ '--deck-color': item.color, '--pile-angle': `${(i - 4) * 1.5}deg`, '--pile-y': `${Math.abs(i - 4) ** 1.5 * 3}px` } as CSSProperties}
        aria-label={`${item.family.family_id} · ${t(item.family.name, item.family.name_en)} · ${item.cards.length} ${t('张卡片', 'cards')}`}
        aria-expanded={expandedFamily === item.family.family_id}
        onPointerEnter={(e) => { if (e.pointerType !== 'touch') expand(item.family.family_id); }}
        onFocus={(e) => { if (e.currentTarget.matches(':focus-visible')) expand(item.family.family_id); }}
        onClick={() => { if (expandedFamily === item.family.family_id && !pointerInside.current) collapse(); else expand(item.family.family_id); }}>
        <span className="pile-stack"><span className="pile-layer layer-three"/><span className="pile-layer layer-two"/><span className="pile-top"><span className="pile-index">{String(i + 1).padStart(2, '0')}</span><Sigil index={i}/><b>{item.family.family_id}</b><span className="pile-count">{String(item.cards.length).padStart(2, '0')}</span></span></span>
        <span className="pile-label">{t(item.family.name, item.family.name_en)}</span>
        <span className="pile-status">{item.practiced > 0 && <i className="practice-dot" />} {item.family.family_id}</span>
      </button>)}
    </div>
  </div>;
}
