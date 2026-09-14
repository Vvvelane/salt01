import type { Expression, FactorCard, Family, Registry } from '../../types';

export type IdeaNode = {
  id: string;
  kind: 'root' | 'family' | 'expression' | 'card';
  family?: Family;
  expression?: Expression;
  card?: FactorCard;
  parent: string | null;
  color: string;
  practiced: number;
  total: number;
};
export type IdeaLink = { source: string; target: string };
export type IdeaDeck = { family: Family; cards: FactorCard[]; color: string; practiced: number };
export type IdeaModel = { nodes: IdeaNode[]; links: IdeaLink[]; byId: Map<string, IdeaNode>; decks: IdeaDeck[] };
export const FAMILY_COLORS = ['#d5f59a', '#83d7dd', '#b7abf3', '#88bedc', '#d1b987', '#d79bab', '#86cdb4', '#aaaee1', '#dcc8ac'];

/** One registry and one hierarchy feed both spatial presentations. */
export function buildIdeaModel(registry: Registry): IdeaModel {
  const families = [...registry.families].sort((a, b) => a.order - b.order);
  const practiced = (card: FactorCard) => Boolean(registry.factorlab[card.factor_id]?.length);
  const nodes: IdeaNode[] = [{ id: 'ROOT', kind: 'root', parent: null, color: '#d5f59a', total: registry.cards.length, practiced: registry.cards.filter(practiced).length }];
  const links: IdeaLink[] = [];
  const decks: IdeaDeck[] = [];
  const add = (node: IdeaNode) => { nodes.push(node); links.push({ source: node.parent!, target: node.id }); };
  families.forEach((family, familyIndex) => {
    const color = FAMILY_COLORS[familyIndex % FAMILY_COLORS.length];
    const cards = family.expressions.flatMap((expression) => registry.cards.filter((card) => card.expression === expression.expression_id));
    const count = cards.filter(practiced).length;
    decks.push({ family, cards, color, practiced: count });
    add({ id: family.family_id, kind: 'family', parent: 'ROOT', family, color, practiced: count, total: cards.length });
    family.expressions.forEach((expression) => {
      const members = cards.filter((card) => card.expression === expression.expression_id);
      add({ id: expression.expression_id, kind: 'expression', parent: family.family_id, expression, family, color, practiced: members.filter(practiced).length, total: members.length });
      members.forEach((card) => {
        add({ id: card.factor_id, kind: 'card', parent: expression.expression_id, card, family, expression, color, practiced: Number(practiced(card)), total: 1 });
      });
    });
  });
  return { nodes, links, decks, byId: new Map(nodes.map((node) => [node.id, node])) };
}

export function lineage(model: IdeaModel, id: string | null): Set<string> {
  const ids = new Set<string>();
  let node = id ? model.byId.get(id) : undefined;
  while (node && !ids.has(node.id)) { ids.add(node.id); node = node.parent ? model.byId.get(node.parent) : undefined; }
  return ids;
}
