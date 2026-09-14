import type { IdeaModel, IdeaNode } from './model';

export type ForestPoint = { node: IdeaNode; x: number; y: number; z: number };
export type ForestLayout = { points: ForestPoint[]; width: number; height: number };
export type Displacement = { x: number; y: number; vx: number; vy: number };
export type Camera = { zoom: number; x: number; y: number };
export type ScreenPoint = ForestPoint & { size: number; depth: number };

/** Independent, downward trees. ROOT remains registry metadata, never a visual hub. */
export function layoutForest(model: IdeaModel, viewportWidth: number, viewportHeight: number): ForestLayout {
  const columns = viewportWidth < 480 ? 1 : viewportWidth < 760 ? 2 : 3;
  const width = Math.max(viewportWidth, columns === 1 ? 560 : columns === 2 ? 780 : 1000);
  const rows = Math.ceil(model.decks.length / columns);
  const rowHeight = Math.max(132, (viewportHeight - 24) / Math.max(1, rows));
  const height = Math.max(viewportHeight, rows * rowHeight + 24);
  const points: ForestPoint[] = [];
  for (let row = 0; row < rows; row++) {
    const decks = model.decks.slice(row * columns, (row + 1) * columns);
    const weights = decks.map((deck) => Math.max(3, deck.cards.length) + (deck.family.expressions.length - 1) * .35);
    const totalWeight = weights.reduce((a, b) => a + b, 0);
    const gutter = 34;
    const available = width - 56 - gutter * (decks.length - 1);
    let left = 28;
    decks.forEach((deck, index) => {
      const familyWidth = available * weights[index] / totalWeight;
      const expressions = deck.family.expressions;
      const expressionGap = Math.min(12, familyWidth * .025);
      const cardSpace = (familyWidth - 20 - expressionGap * (expressions.length - 1)) / Math.max(1, deck.cards.length);
      const y = 30 + row * rowHeight;
      const z = ((row * columns + index) % 3 - 1) * 7;
      points.push({ node: model.byId.get(deck.family.family_id)!, x: left + familyWidth / 2, y, z });
      let expressionLeft = left + 10;
      expressions.forEach((expression) => {
        const cards = deck.cards.filter((card) => card.expression === expression.expression_id);
        const expressionWidth = cardSpace * cards.length;
        points.push({ node: model.byId.get(expression.expression_id)!, x: expressionLeft + expressionWidth / 2, y: y + 39, z: z + 3 });
        cards.forEach((card, cardIndex) => points.push({
          node: model.byId.get(card.factor_id)!, x: expressionLeft + cardSpace * (cardIndex + .5), y: y + rowHeight - 63,
          z: z + 6 + Math.sin(cardIndex * 1.7) * 2,
        }));
        expressionLeft += expressionWidth + expressionGap;
      });
      left += familyWidth + gutter;
    });
  }
  return { points, width, height };
}

export function initialCamera(layout: ForestLayout, width: number, height: number): Camera {
  const zoom = Math.min(1, width / layout.width);
  return { zoom, x: 0, y: Math.max(0, (layout.height * zoom - height) / 2) };
}

export function projectPoint(point: ForestPoint, layout: ForestLayout, camera: Camera, width: number, height: number, parallax: { x: number; y: number }): ScreenPoint {
  const depth = 1 + point.z / 160;
  return {
    ...point,
    x: width / 2 + (point.x - layout.width / 2) * camera.zoom + camera.x + parallax.x * point.z * .35,
    y: height / 2 + (point.y - layout.height / 2) * camera.zoom + camera.y + parallax.y * point.z * .2,
    size: Math.max(2, Math.min(7, ({ root: 0, family: 5.3, expression: 3.1, card: 2.6 }[point.node.kind] + (point.node.kind === 'card' && point.node.practiced ? .4 : 0)) * depth * Math.sqrt(camera.zoom))),
    depth,
  };
}

/** Immediate push, then a short spring return; elapsed milliseconds keep 60/120 Hz consistent. */
export function moveDisplacement(motion: Displacement, target: { x: number; y: number } | null, elapsed: number) {
  const seconds = Math.max(0, Math.min(elapsed, 32)) / 1000;
  if (target) {
    const blend = -Math.expm1(-seconds / .025);
    motion.x += (target.x - motion.x) * blend;
    motion.y += (target.y - motion.y) * blend;
    motion.vx = motion.vy = 0;
  } else {
    // Substeps keep the spring stable through dropped frames.
    const steps = Math.max(1, Math.ceil(seconds / .008));
    const dt = seconds / steps;
    for (let i = 0; i < steps; i++) {
      motion.vx += (-motion.x * 420 - motion.vx * 28) * dt;
      motion.vy += (-motion.y * 420 - motion.vy * 28) * dt;
      motion.x += motion.vx * dt; motion.y += motion.vy * dt;
    }
    if (Math.abs(motion.x) + Math.abs(motion.y) + Math.abs(motion.vx) + Math.abs(motion.vy) < .025) motion.x = motion.y = motion.vx = motion.vy = 0;
  }
}

export function hitNode(points: ScreenPoint[], x: number, y: number): ScreenPoint | undefined {
  let result: ScreenPoint | undefined, nearest = Infinity;
  for (const point of points) {
    const distance = Math.hypot(point.x - x, point.y - y);
    // IDs beneath leaves are clickable too; users do not have to hit a tiny dot.
    const labelY = point.node.kind === 'card' ? point.y + 13 : point.y - 12;
    const labelWidth = Math.max(32, point.node.id.length * 5.5);
    const inLabel = Math.abs(x - point.x) <= labelWidth / 2 + 3 && Math.abs(y - labelY) < 8;
    const score = inLabel ? Math.hypot(point.x - x, labelY - y) : distance;
    if ((distance <= Math.max(10, point.size + 5) || inLabel) && score < nearest) { result = point; nearest = score; }
  }
  return result;
}
