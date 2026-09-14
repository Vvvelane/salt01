import { useEffect, useRef } from 'react';
import type { CSSProperties } from 'react';
import { useLanguage } from '../../i18n';
import type { Registry } from '../../types';
import { Sigil } from './Decks';
import type { CardOrigin } from './Decks';
import type { IdeaModel, IdeaNode } from './model';
import { NodeDetail } from './NodeDetail';

export function IdeaDialog({ node, registry, model, origin, canBack, onBack, onSelect, onClose, onResults }: {
  onResults: (strategy: string) => void; node: IdeaNode; registry: Registry; model: IdeaModel; origin?: CardOrigin;
  canBack: boolean; onBack: () => void; onSelect: (id: string) => void; onClose: () => void;
}) {
  const { t } = useLanguage();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const originRef = useRef(origin);
  const deckIndex = model.decks.findIndex((deck) => deck.family.family_id === node.family?.family_id);
  const siblings = node.kind === 'card' ? model.decks[deckIndex]?.cards.map((card) => card.factor_id) ?? []
    : model.nodes.filter((item) => item.parent === node.parent && item.id !== 'ROOT').map((item) => item.id);
  const index = siblings.indexOf(node.id);
  useEffect(() => {
    const dialog = dialogRef.current!;
    const trigger = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const oldOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    dialog.showModal(); closeRef.current?.focus({ preventScroll: true });
    return () => {
      dialog.close(); document.body.style.overflow = oldOverflow;
      const target = trigger?.isConnected ? trigger : document.querySelector<HTMLElement>('.room-keeper');
      target?.focus({ preventScroll: true });
    };
  }, []);
  useEffect(() => { scrollRef.current?.scrollTo({ top: 0 }); }, [node.id]);
  const entry = originRef.current;
  const style = {
    '--deck-color': node.color,
    '--enter-x': `${entry ? entry.x - window.innerWidth / 2 : 0}px`,
    '--enter-y': `${entry ? entry.y - window.innerHeight / 2 : 35}px`,
    '--enter-scale': entry ? Math.max(.12, Math.min(.6, entry.width / Math.min(940, window.innerWidth - 40))) : .8,
  } as CSSProperties;
  return <dialog ref={dialogRef} className="idea-dialog" style={style} aria-label={`${node.id} · ${t('研究详情', 'Research details')}`}
    onCancel={(event) => { event.preventDefault(); onClose(); }} onClick={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <div className="dialog-arrival"><div className="dialog-flip">
      <div className="dialog-card-reverse" aria-hidden="true"><span>NaCl / RESEARCH ARCHIVE</span><Sigil index={Math.max(0, deckIndex)} /><b>{node.id}</b><span>SALT RESEARCH TERMINAL</span></div>
      <div className="dialog-card-face">
        <header className="dialog-toolbar">
          <div className="dialog-breadcrumb">
            {canBack && <button onClick={onBack} aria-label={t('返回上一张', 'Go back')} title={t('返回上一张', 'Go back')}>←</button>}
            <button onClick={() => onSelect('ROOT')}>NaCl</button>
            {node.family && <><span>/</span><button onClick={() => onSelect(node.family!.family_id)}>{node.family.family_id}</button></>}
            {node.expression && <><span>/</span><button onClick={() => onSelect(node.expression!.expression_id)}>{node.expression.expression_id}</button></>}
          </div>
          <div className="dialog-pagination">
            {siblings.length > 1 && <><span>{String(index + 1).padStart(2, '0')} / {String(siblings.length).padStart(2, '0')}</span>
              <button onClick={() => onSelect(siblings[(index - 1 + siblings.length) % siblings.length])} aria-label={t('上一张', 'Previous card')}>‹</button>
              <button onClick={() => onSelect(siblings[(index + 1) % siblings.length])} aria-label={t('下一张', 'Next card')}>›</button></>}
            <button ref={closeRef} className="dialog-close" onClick={onClose} aria-label={t('关闭详情', 'Close details')}>×</button>
          </div>
        </header>
        <div ref={scrollRef} className="dialog-scroll"><div key={node.id} className="dialog-detail-change"><NodeDetail onResults={onResults} node={node} registry={registry} onSelect={onSelect} /></div></div>
      </div>
    </div></div>
  </dialog>;
}
