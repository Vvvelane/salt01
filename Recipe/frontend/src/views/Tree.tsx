import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { CSSProperties, PointerEvent as ReactPointerEvent } from 'react';
import { api } from '../api';
import { SCOPE_LABEL, TYPE_LABEL, TYPE_SHORT, shortName } from '../structure';
import type { Expression, FactorCard, Family, Registry, StructureScope, StructureType } from '../types';

type NodeKind = 'root' | 'family' | 'expression' | 'card';
type TreeNode = {
  id: string;
  kind: NodeKind;
  children: TreeNode[];
  family?: Family;
  expression?: Expression;
  card?: FactorCard;
  practiced: number;
  total: number;
};
type Placed = { node: TreeNode; x: number; y: number; parent: Placed | null; collapsed: boolean };
type View = { x: number; y: number; k: number };

const COLUMN_X: Record<NodeKind, number> = { root: 0, family: 210, expression: 470, card: 770 };
const NODE_W: Record<NodeKind, number> = { root: 150, family: 206, expression: 244, card: 272 };
const NODE_H: Record<NodeKind, number> = { root: 46, family: 44, expression: 32, card: 26 };
const ROW = 32;
const MIN_K = 0.2;
const MAX_K = 2.6;

function buildTree(registry: Registry): TreeNode {
  const practiced = (card: FactorCard) => (registry.factorlab[card.factor_id] ? 1 : 0);
  const families = [...registry.families].sort((a, b) => a.order - b.order).map((family) => {
    const expressions = family.expressions.map((expression) => {
      const cards = registry.cards
        .filter((card) => card.expression === expression.expression_id)
        .map<TreeNode>((card) => ({ id: card.factor_id, kind: 'card', children: [], card, practiced: practiced(card), total: 1 }));
      return { id: expression.expression_id, kind: 'expression', children: cards, family, expression, practiced: cards.reduce((n, c) => n + c.practiced, 0), total: cards.length } satisfies TreeNode;
    });
    return { id: family.family_id, kind: 'family', children: expressions, family, practiced: expressions.reduce((n, e) => n + e.practiced, 0), total: expressions.reduce((n, e) => n + e.total, 0) } satisfies TreeNode;
  });
  return { id: 'ROOT', kind: 'root', children: families, practiced: families.reduce((n, f) => n + f.practiced, 0), total: registry.cards.length };
}

function layout(root: TreeNode, collapsed: Set<string>): Placed[] {
  const placed: Placed[] = [];
  let cursor = 0;
  let lastFamily = '';
  let lastExpression = '';
  function visit(node: TreeNode, parent: Placed | null, inheritedFamily: string, inheritedExpression: string): Placed {
    const familyId = node.kind === 'family' ? node.id : inheritedFamily;
    const expressionId = node.kind === 'expression' ? node.id : inheritedExpression;
    const isCollapsed = collapsed.has(node.id) && node.children.length > 0;
    const item: Placed = { node, x: COLUMN_X[node.kind], y: 0, parent, collapsed: isCollapsed };
    placed.push(item);
    if (!node.children.length || isCollapsed) {
      if (lastFamily && familyId !== lastFamily) cursor += 26;
      else if (lastExpression && expressionId !== lastExpression) cursor += 10;
      item.y = cursor + (node.kind === 'card' ? 0 : 6);
      cursor += node.kind === 'card' ? ROW : 48;
      lastFamily = familyId;
      lastExpression = expressionId;
      return item;
    }
    const kids = node.children.map((child) => visit(child, item, familyId, expressionId));
    item.y = (kids[0].y + kids[kids.length - 1].y) / 2;
    return item;
  }
  visit(root, null, '', '');
  return placed;
}

function edgePath(from: Placed, to: Placed) {
  const x1 = from.x + NODE_W[from.node.kind];
  const x2 = to.x;
  const mid = x1 + (x2 - x1) * 0.55;
  return `M ${x1} ${from.y} C ${mid} ${from.y}, ${mid} ${to.y}, ${x2} ${to.y}`;
}

function descendants(node: TreeNode): TreeNode[] {
  return node.children.flatMap((child) => [child, ...descendants(child)]);
}

type Highlight = { type: StructureType | null; scope: StructureScope | null };

export function Tree({ onOpenCard }: { onOpenCard: (factorId: string) => void }) {
  const [registry, setRegistry] = useState<Registry | null>(null);
  const [error, setError] = useState('');
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());
  const [selectedId, setSelectedId] = useState('ROOT');
  const [view, setView] = useState<View>({ x: 40, y: 40, k: 0.8 });
  const [highlight, setHighlight] = useState<Highlight>({ type: null, scope: null });
  const [animate, setAnimate] = useState(false);
  const canvasRef = useRef<HTMLDivElement>(null);
  const drag = useRef<{ x: number; y: number; vx: number; vy: number; moved: boolean } | null>(null);

  useEffect(() => {
    api.cards().then(setRegistry).catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)));
  }, []);

  const root = useMemo(() => (registry ? buildTree(registry) : null), [registry]);
  const placed = useMemo(() => (root ? layout(root, collapsed) : []), [root, collapsed]);
  const allNodes = useMemo(() => (root ? new Map([root, ...descendants(root)].map((node) => [node.id, node])) : new Map<string, TreeNode>()), [root]);
  const selected = allNodes.get(selectedId) ?? root;

  const matches = useCallback((card?: FactorCard) => {
    if (!card) return true;
    return (!highlight.type || card.structure.type === highlight.type) && (!highlight.scope || card.structure.scope === highlight.scope);
  }, [highlight]);
  const filtering = Boolean(highlight.type || highlight.scope);

  const fitTo = useCallback((ids?: Set<string>) => {
    const box = canvasRef.current?.getBoundingClientRect();
    const items = ids ? placed.filter((item) => ids.has(item.node.id)) : placed;
    if (!box || !items.length) return;
    const minX = Math.min(...items.map((item) => item.x)) - 30;
    const maxX = Math.max(...items.map((item) => item.x + NODE_W[item.node.kind])) + 30;
    const minY = Math.min(...items.map((item) => item.y - NODE_H[item.node.kind] / 2)) - 30;
    const maxY = Math.max(...items.map((item) => item.y + NODE_H[item.node.kind] / 2)) + 30;
    const k = Math.min(MAX_K, Math.max(MIN_K, Math.min(box.width / (maxX - minX), box.height / (maxY - minY))));
    setAnimate(true);
    setView({ k, x: (box.width - (maxX - minX) * k) / 2 - minX * k, y: (box.height - (maxY - minY) * k) / 2 - minY * k });
  }, [placed]);

  // First paint: readable scale anchored at the top so the trunk and first families are legible.
  const initialised = useRef(false);
  useEffect(() => {
    if (initialised.current || !placed.length || !canvasRef.current) return;
    initialised.current = true;
    const box = canvasRef.current.getBoundingClientRect();
    const width = COLUMN_X.card + NODE_W.card + 60;
    const k = Math.max(0.5, Math.min(1, box.width / width));
    const top = Math.min(...placed.map((item) => item.y - NODE_H[item.node.kind] / 2));
    setView({ k, x: Math.max(24, (box.width - width * k) / 2), y: 64 - top * k });
  }, [placed]);

  useEffect(() => {
    const element = canvasRef.current;
    if (!element) return;
    function onWheel(event: WheelEvent) {
      event.preventDefault();
      setAnimate(false);
      const box = element!.getBoundingClientRect();
      if (event.ctrlKey || event.metaKey) {
        const px = event.clientX - box.left;
        const py = event.clientY - box.top;
        setView((current) => {
          const k = Math.min(MAX_K, Math.max(MIN_K, current.k * Math.exp(-event.deltaY * 0.01)));
          return { k, x: px - ((px - current.x) * k) / current.k, y: py - ((py - current.y) * k) / current.k };
        });
      } else {
        setView((current) => ({ ...current, x: current.x - event.deltaX, y: current.y - event.deltaY }));
      }
    }
    element.addEventListener('wheel', onWheel, { passive: false });
    return () => element.removeEventListener('wheel', onWheel);
  }, [registry]);

  function zoomBy(factor: number) {
    const box = canvasRef.current?.getBoundingClientRect();
    if (!box) return;
    setAnimate(true);
    setView((current) => {
      const k = Math.min(MAX_K, Math.max(MIN_K, current.k * factor));
      const px = box.width / 2;
      const py = box.height / 2;
      return { k, x: px - ((px - current.x) * k) / current.k, y: py - ((py - current.y) * k) / current.k };
    });
  }

  function onPointerDown(event: ReactPointerEvent<HTMLDivElement>) {
    if ((event.target as Element).closest('.tree-node')) return;
    drag.current = { x: event.clientX, y: event.clientY, vx: view.x, vy: view.y, moved: false };
    event.currentTarget.setPointerCapture(event.pointerId);
    setAnimate(false);
  }
  function onPointerMove(event: ReactPointerEvent<HTMLDivElement>) {
    if (!drag.current) return;
    const dx = event.clientX - drag.current.x;
    const dy = event.clientY - drag.current.y;
    if (Math.abs(dx) + Math.abs(dy) > 3) drag.current.moved = true;
    setView((current) => ({ ...current, x: drag.current!.vx + dx, y: drag.current!.vy + dy }));
  }
  function onPointerUp() {
    drag.current = null;
  }

  function toggle(node: TreeNode) {
    setSelectedId(node.id);
    if (node.kind === 'card' || node.kind === 'root') return;
    setCollapsed((current) => {
      const next = new Set(current);
      if (next.has(node.id)) next.delete(node.id);
      else next.add(node.id);
      return next;
    });
  }

  // Expand every collapsed ancestor (and the node itself), then fit once the new layout exists.
  const pendingFocus = useRef<string | null>(null);
  function reveal(id: string) {
    const node = allNodes.get(id);
    if (!node) return;
    setSelectedId(id);
    const opened = [...allNodes.values()].filter((candidate) => candidate.id === id || descendants(candidate).some((child) => child.id === id)).map((candidate) => candidate.id);
    pendingFocus.current = id;
    if (opened.some((candidate) => collapsed.has(candidate))) {
      setCollapsed((current) => new Set([...current].filter((candidate) => !opened.includes(candidate))));
    } else {
      fitTo(new Set([id, ...descendants(node).map((child) => child.id)]));
      pendingFocus.current = null;
    }
  }
  useEffect(() => {
    const node = pendingFocus.current ? allNodes.get(pendingFocus.current) : null;
    if (!node) return;
    pendingFocus.current = null;
    fitTo(new Set([node.id, ...descendants(node).map((child) => child.id)]));
  }, [placed, allNodes, fitTo]);

  const lod = view.k < 0.42 ? 'far' : view.k < 0.7 ? 'mid' : 'near';
  const litEdge = (item: Placed) => item.node.practiced > 0;
  const nodeStyle = (item: Placed): CSSProperties => ({ transform: `translate(${item.x}px, ${item.y}px)` });

  if (error) return <div className="tree-page"><div className="error-banner">{error}</div></div>;

  return (
    <div className="tree-page">
      <div className="tree-toolbar">
        <div className="tree-title">
          <span className="kicker">NaCl STRUCTURE · A 经济假设 → B 表达 → CARD</span>
          <h1>Factor Tree</h1>
        </div>
        <div className="tree-controls">
          <div className="tree-button-row">
            <button onClick={() => zoomBy(1 / 1.25)} aria-label="缩小">−</button>
            <span className="zoom-readout">{Math.round(view.k * 100)}%</span>
            <button onClick={() => zoomBy(1.25)} aria-label="放大">+</button>
            <button onClick={() => fitTo()}>适配全部</button>
            <button onClick={() => setCollapsed(new Set())}>全部展开</button>
            <button onClick={() => setCollapsed(new Set(registry?.families.map((family) => family.family_id)))}>只看家族</button>
            <button onClick={() => setCollapsed(new Set(registry?.families.flatMap((family) => family.expressions.map((expression) => expression.expression_id))))}>到表达层</button>
          </div>
          <div className="tree-filter-row">
            <span>轴 C 高亮</span>
            {(Object.keys(TYPE_LABEL) as StructureType[]).map((type) => (
              <button key={type} className={highlight.type === type ? 'on' : ''} onClick={() => setHighlight((current) => ({ ...current, type: current.type === type ? null : type }))}>{TYPE_LABEL[type]}</button>
            ))}
            <i />
            {(Object.keys(SCOPE_LABEL) as StructureScope[]).map((scope) => (
              <button key={scope} className={highlight.scope === scope ? 'on' : ''} onClick={() => setHighlight((current) => ({ ...current, scope: current.scope === scope ? null : scope }))}>{SCOPE_LABEL[scope]}</button>
            ))}
          </div>
        </div>
      </div>

      <div className="tree-layout">
        <div
          className={`tree-canvas lod-${lod}${filtering ? ' filtering' : ''}${animate ? ' animate' : ''}`}
          ref={canvasRef}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerCancel={onPointerUp}
        >
          <div className="tree-legend">
            <span><i className="legend-lit" />Factorlab 已实践</span>
            <span><i className="legend-gray" />未实践</span>
            <small>拖拽平移 · ⌘/Ctrl + 滚轮缩放 · 单击折叠 · 双击聚焦</small>
          </div>
          <svg width="100%" height="100%">
            <defs>
              <linearGradient id="neon-base" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#d4ff3a" />
                <stop offset="48%" stopColor="#39ff7a" />
                <stop offset="100%" stopColor="#00e0a4" />
              </linearGradient>
              <radialGradient id="neon-sheen" cx="0.25" cy="-0.2" r="1.1">
                <stop offset="0%" stopColor="#ffffff" stopOpacity="0.7" />
                <stop offset="45%" stopColor="#ffffff" stopOpacity="0.12" />
                <stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
              </radialGradient>
              <pattern id="neon-weave" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">
                <line x1="0" y1="0" x2="0" y2="6" stroke="#04210f" strokeWidth="1.2" strokeOpacity="0.16" />
              </pattern>
              <filter id="neon-glow" x="-30%" y="-80%" width="160%" height="260%">
                <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur" />
                <feColorMatrix in="blur" type="matrix" values="0 0 0 0 0.22  0 0 0 0 1  0 0 0 0 0.45  0 0 0 0.85 0" />
                <feMerge><feMergeNode /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
              <filter id="edge-glow" x="-10%" y="-50%" width="120%" height="200%">
                <feGaussianBlur stdDeviation="2.2" result="blur" />
                <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
            </defs>
            <g className="tree-viewport" style={{ transform: `translate(${view.x}px, ${view.y}px) scale(${view.k})` }}>
              <g className="tree-edges">
                {placed.filter((item) => item.parent).map((item) => {
                  const dim = filtering && (item.node.kind === 'card' ? !matches(item.node.card) : !descendants(item.node).some((node) => node.card && matches(node.card)));
                  return (
                    <path
                      key={`${item.parent!.node.id}-${item.node.id}`}
                      className={`tree-edge${litEdge(item) ? ' lit' : ''}${dim ? ' dim' : ''}`}
                      style={{ d: `path("${edgePath(item.parent!, item)}")` } as CSSProperties}
                      filter={litEdge(item) ? 'url(#edge-glow)' : undefined}
                    />
                  );
                })}
              </g>
              {placed.map((item) => {
                const { node } = item;
                const w = NODE_W[node.kind];
                const h = NODE_H[node.kind];
                const lit = node.kind === 'card' && node.practiced > 0;
                const dim = filtering && (node.kind === 'card' ? !matches(node.card) : node.kind !== 'root' && !descendants(node).some((child) => child.card && matches(child.card)));
                const cls = `tree-node kind-${node.kind}${lit ? ' lit' : ''}${dim ? ' dim' : ''}${selectedId === node.id ? ' selected' : ''}${item.collapsed ? ' collapsed' : ''}`;
                return (
                  <g
                    key={node.id}
                    className={cls}
                    style={nodeStyle(item)}
                    onClick={(event) => { event.stopPropagation(); toggle(node); }}
                    onDoubleClick={(event) => { event.stopPropagation(); reveal(node.id); }}
                  >
                    <g className="node-body" transform={`translate(0 ${-h / 2})`}>
                      {lit ? (
                        <g filter="url(#neon-glow)" className="neon-stack">
                          <rect width={w} height={h} rx={h / 2} fill="url(#neon-base)" />
                          <rect width={w} height={h} rx={h / 2} fill="url(#neon-weave)" />
                          <rect width={w} height={h} rx={h / 2} fill="url(#neon-sheen)" />
                        </g>
                      ) : (
                        <rect className="node-shape" width={w} height={h} rx={node.kind === 'card' ? h / 2 : 6} />
                      )}
                      {node.kind === 'root' && <>
                        <text className="node-id" x={16} y={19}>NaCl REGISTRY</text>
                        <text className="node-sub" x={16} y={35}>{node.total} cards · {registry?.families.length} families</text>
                      </>}
                      {node.kind === 'family' && <>
                        <text className="node-id" x={14} y={19}>{node.id}</text>
                        <text className="node-name" x={54} y={19}>{node.family!.name}</text>
                        <text className="node-sub" x={14} y={35}>{node.family!.name_en}</text>
                        <text className="node-count" x={w - 12} y={19} textAnchor="end">{node.total}</text>
                        {node.practiced > 0 && <text className="node-lit-count" x={w - 12} y={35} textAnchor="end">● {node.practiced}</text>}
                      </>}
                      {node.kind === 'expression' && <>
                        <text className="node-id" x={12} y={20}>{node.id.split('-')[1]}</text>
                        <text className="node-name" x={40} y={20}>{node.expression!.name}</text>
                        {node.practiced > 0 && <text className="node-lit-count" x={w - 10} y={20} textAnchor="end">●</text>}
                      </>}
                      {node.kind === 'card' && <>
                        <text className="node-id" x={13} y={17}>{node.id}</text>
                        <text className="node-name" x={70} y={17}>{shortName(node.card!)}</text>
                        <text className="node-structure" x={w - 12} y={17} textAnchor="end">{TYPE_SHORT[node.card!.structure.type]}·{SCOPE_LABEL[node.card!.structure.scope]}</text>
                      </>}
                    </g>
                    {item.collapsed && <text className="collapse-badge" x={w + 10} y={4}>+{node.total}</text>}
                  </g>
                );
              })}
            </g>
          </svg>
        </div>

        <aside className="tree-detail panel">
          {selected && registry && <NodeDetail node={selected} registry={registry} onSelect={reveal} onOpenCard={onOpenCard} />}
        </aside>
      </div>
    </div>
  );
}

function NodeDetail({ node, registry, onSelect, onOpenCard }: { node: TreeNode; registry: Registry; onSelect: (id: string) => void; onOpenCard: (id: string) => void }) {
  const cardsOf = (predicate: (card: FactorCard) => boolean) => registry.cards.filter(predicate);
  const CardChip = ({ card }: { card: FactorCard }) => (
    <button className={registry.factorlab[card.factor_id] ? 'chip lit' : 'chip'} onClick={() => onSelect(card.factor_id)}>{card.factor_id}</button>
  );

  if (node.kind === 'root') {
    const practiced = cardsOf((card) => Boolean(registry.factorlab[card.factor_id]));
    return (
      <div className="detail-inner">
        <span className="kicker">STRUCTURE FRAMEWORK</span>
        <h2>三轴结构</h2>
        <dl className="axis-list">
          <div><dt>A</dt><dd><b>经济假设 → 家族</b>每张 Card 只属于一个家族。</dd></div>
          <div><dt>B</dt><dd><b>表达 → 家族内分簇</b>同一假设的不同侧重，窗口对齐后可用 X 相关性检验。</dd></div>
          <div><dt>C</dt><dd><b>结构 → Card 属性</b>方向性 / 条件性 / 形状性；单标的 / 截面 / 多腿；数据需求。</dd></div>
        </dl>
        <h3>家族</h3>
        <div className="detail-list">
          {registry.families.map((family) => (
            <button key={family.family_id} onClick={() => onSelect(family.family_id)}>
              <b>{family.family_id}</b><span>{family.name}</span><small>{registry.cards.filter((card) => card.family === family.family_id).length}</small>
            </button>
          ))}
        </div>
        <h3>Factorlab 已实践</h3>
        <div className="chip-row">{practiced.map((card) => <CardChip key={card.factor_id} card={card} />)}</div>
      </div>
    );
  }

  if (node.kind === 'family') {
    const family = node.family!;
    return (
      <div className="detail-inner">
        <span className="kicker">AXIS A · 经济假设</span>
        <h2>{family.family_id} · {family.name}</h2>
        <p className="detail-en">{family.name_en} · 来源旧家族 {family.legacy_families.join(' / ')}</p>
        <section><h3>Core Mechanism</h3><p>{family.core_mechanism}</p></section>
        <section><h3>Core Hypothesis</h3><code>{family.core_hypothesis}</code></section>
        {family.relations.length > 0 && <section><h3>家族关系</h3>{family.relations.map((relation) => (
          <div className="relation-line" key={relation.type + relation.target}><button onClick={() => onSelect(relation.target)}>{relation.type} → {relation.target}</button><span>{relation.note}</span></div>
        ))}</section>}
        <section><h3>轴 B 表达</h3>{family.expressions.map((expression) => (
          <div className="expression-line" key={expression.expression_id}>
            <button onClick={() => onSelect(expression.expression_id)}><b>{expression.expression_id}</b> {expression.name}</button>
            <div className="chip-row">{cardsOf((card) => card.expression === expression.expression_id).map((card) => <CardChip key={card.factor_id} card={card} />)}</div>
          </div>
        ))}</section>
      </div>
    );
  }

  if (node.kind === 'expression') {
    const expression = node.expression!;
    const members = cardsOf((card) => card.expression === expression.expression_id);
    return (
      <div className="detail-inner">
        <span className="kicker">AXIS B · 表达 · {node.family!.family_id} {node.family!.name}</span>
        <h2>{expression.expression_id} · {expression.name}</h2>
        <section><h3>表达定义</h3><p>{expression.description}</p></section>
        {expression.architecture_ref && <section><h3>架构参考</h3><p>{expression.architecture_ref}</p></section>}
        <section><h3>Cards · 轴 C</h3>
          <div className="member-table">
            {members.map((card) => (
              <button key={card.factor_id} className={registry.factorlab[card.factor_id] ? 'lit' : ''} onClick={() => onSelect(card.factor_id)}>
                <b>{card.factor_id}</b><span>{shortName(card)}</span><small>{TYPE_LABEL[card.structure.type]} · {SCOPE_LABEL[card.structure.scope]}</small>
              </button>
            ))}
          </div>
        </section>
      </div>
    );
  }

  const card = node.card!;
  const strategies = registry.factorlab[card.factor_id] ?? [];
  const family = registry.families.find((item) => item.family_id === card.family);
  const expression = family?.expressions.find((item) => item.expression_id === card.expression);
  return (
    <div className="detail-inner">
      <span className="kicker">CARD · {card.family} / {card.expression} · 旧 {card.legacy_family}</span>
      <h2>{card.factor_id}</h2>
      <p className="detail-en">{card.name}</p>
      <div className={strategies.length ? 'practice-state lit' : 'practice-state'}>{strategies.length ? `Factorlab 已实践 · ${strategies.length} 个注册` : '尚未在 Factorlab 实践'}</div>
      <dl className="structure-grid">
        <div><dt>A 家族</dt><dd><button onClick={() => onSelect(card.family)}>{family?.name}</button></dd></div>
        <div><dt>B 表达</dt><dd><button onClick={() => onSelect(card.expression)}>{expression?.name}</button></dd></div>
        <div><dt>C 结构类型</dt><dd>{TYPE_LABEL[card.structure.type]}</dd></div>
        <div><dt>C 标的范围</dt><dd>{SCOPE_LABEL[card.structure.scope]}</dd></div>
        <div><dt>C 数据需求</dt><dd>{card.structure.data.join(' + ')}</dd></div>
        <div><dt>两层可分</dt><dd>{card.structure.layer_separable ? 'true' : 'false'}</dd></div>
      </dl>
      <section><h3>Idea Summary</h3><p>{card.idea_summary || '未填写'}</p></section>
      {strategies.length > 0 && <section><h3>Factorlab 注册</h3>{strategies.map((strategy) => (
        <div className="strategy-line" key={strategy.strategy_id}><b>{strategy.strategy_id}</b><span>{strategy.name} · {strategy.frequency}</span></div>
      ))}</section>}
      <button className="primary open-card" onClick={() => onOpenCard(card.factor_id)}>在 Registry 中打开</button>
    </div>
  );
}
