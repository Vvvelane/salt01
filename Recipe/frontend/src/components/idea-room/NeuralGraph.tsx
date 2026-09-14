import { useEffect, useRef } from 'react';
import { useLanguage } from '../../i18n';
import { lineage } from './model';
import type { IdeaModel } from './model';
import type { CardOrigin } from './Decks';
import { hitNode, initialCamera, layoutForest, moveDisplacement, projectPoint } from './forest';
import type { Displacement, ScreenPoint } from './forest';

type Props = {
  model: IdeaModel; selectedId: string | null; hoveredId: string | null; activeFamily: string | null; paused: boolean;
  onHover: (id: string | null) => void; onOpen: (id: string, origin?: CardOrigin) => void;
};
type Point = { x: number; y: number };
type Gesture = { id: number; start: Point; last: Point; moved: boolean; nodeId: string | null };

export function NeuralGraph(props: Props) {
  const { t } = useLanguage();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const current = useRef(props);
  const hoverRef = useRef(props.hoveredId);
  current.current = props;
  hoverRef.current = props.hoveredId;
  const controls = useRef({ zoom: (_: number) => {}, reset: () => {}, focus: (_: string) => {} });

  useEffect(() => {
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    let width = canvas.clientWidth, height = canvas.clientHeight, frame = 0, lastTime = 0;
    let layout = layoutForest(props.model, width, height);
    let camera = initialCamera(layout, width, height);
    let pointer: Point | null = null;
    let gesture: Gesture | null = null;
    let projected: ScreenPoint[] = [];
    const pointers = new Map<number, Point>();
    let pinchDistance = 0;
    const motions = new Map(layout.points.map(({ node }) => [node.id, { x: 0, y: 0, vx: 0, vy: 0 } as Displacement]));
    const links = props.model.links.filter((link) => link.source !== 'ROOT');
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const setHover = (id: string | null) => {
      if (hoverRef.current !== id) { hoverRef.current = id; current.current.onHover(id); }
      canvas.style.cursor = gesture?.moved ? 'grabbing' : id ? 'pointer' : 'grab';
    };
    const reset = () => {
      camera = initialCamera(layout, width, height);
      motions.forEach((m) => { m.x = m.y = m.vx = m.vy = 0; });
      setHover(null);
    };
    const resize = () => {
      // Layout dimensions must not include CSS entry transforms or browser page zoom.
      width = canvas.clientWidth; height = canvas.clientHeight;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      layout = layoutForest(props.model, width, height);
      reset();
    };
    resize();
    const observer = new ResizeObserver(resize);
    observer.observe(canvas);
    const limitPan = () => {
      const limitX = Math.max(0, (layout.width * camera.zoom - width) / 2) + width * .35;
      const limitY = Math.max(0, (layout.height * camera.zoom - height) / 2) + height * .35;
      camera.x = Math.max(-limitX, Math.min(limitX, camera.x));
      camera.y = Math.max(-limitY, Math.min(limitY, camera.y));
    };
    const zoomAt = (factor: number, anchor: Point = { x: width / 2, y: height / 2 }) => {
      const next = Math.max(.5, Math.min(3, camera.zoom * factor));
      const ratio = next / camera.zoom;
      camera.x = anchor.x - width / 2 - (anchor.x - width / 2 - camera.x) * ratio;
      camera.y = anchor.y - height / 2 - (anchor.y - height / 2 - camera.y) * ratio;
      camera.zoom = next; limitPan();
    };
    controls.current = {
      zoom: zoomAt, reset,
      focus: (id) => {
        const point = layout.points.find((p) => p.node.id === id);
        if (!point) return;
        const p = projectPoint(point, layout, camera, width, height, { x: 0, y: 0 });
        if (p.x < 40 || p.x > width - 40 || p.y < 30 || p.y > height - 30) {
          camera.x += width / 2 - p.x; camera.y += height / 2 - p.y; limitPan();
        }
        setHover(id);
      },
    };
    const animate = (time: number) => {
      frame = requestAnimationFrame(animate);
      if (document.hidden || current.current.paused || !width || !height) { lastTime = time; return; }
      const elapsed = lastTime ? Math.min(32, time - lastTime) : 16.67;
      lastTime = time;
      const reduced = motionQuery.matches;
      const parallax = pointer && !reduced && !gesture ? { x: (pointer.x / width - .5) * 2, y: (pointer.y / height - .5) * 2 } : { x: 0, y: 0 };
      const active = hoverRef.current ?? current.current.selectedId;
      const path = lineage(props.model, active);
      const activeFamily = active ? props.model.byId.get(active)?.family?.family_id : current.current.activeFamily;
      projected = layout.points.map((point) => {
        const screen = projectPoint(point, layout, camera, width, height, parallax);
        const m = motions.get(point.node.id)!;
        if (reduced) m.x = m.y = m.vx = m.vy = 0;
        else if (point.node.id === hoverRef.current || point.node.id === gesture?.nodeId) {
          // Keep the hovered/pressed node still so it cannot escape a click.
          m.vx = m.vy = 0;
        } else {
          let target: Point | null = null;
          if (pointer && !gesture) {
            const dx = screen.x - pointer.x, dy = screen.y - pointer.y;
            const distance = Math.hypot(dx, dy);
            if (distance > .1 && distance < 76) {
              const push = (1 - distance / 76) * 13;
              target = { x: dx / distance * push, y: dy / distance * push * .65 };
            }
          }
          moveDisplacement(m, target, elapsed);
        }
        return { ...screen, x: screen.x + m.x, y: screen.y + m.y };
      });
      ctx.clearRect(0, 0, width, height);
      const byId = new Map(projected.map((p) => [p.node.id, p]));
      for (const link of links) {
        const a = byId.get(link.source)!, b = byId.get(link.target)!;
        if (Math.max(a.y, b.y) < 0 || Math.min(a.y, b.y) > height) continue;
        const lit = path.has(a.node.id) && path.has(b.node.id);
        const sameFamily = b.node.family?.family_id === activeFamily;
        ctx.globalAlpha = b.node.practiced ? (lit ? .95 : .65) : (lit || sameFamily ? .24 : .09);
        ctx.strokeStyle = b.node.practiced ? b.node.color : '#66757d';
        ctx.lineWidth = lit ? 1.15 : .65;
        const bend = Math.max(8, (b.y - a.y) * .48);
        ctx.beginPath(); ctx.moveTo(a.x, a.y + a.size);
        ctx.bezierCurveTo(a.x, a.y + bend, b.x, b.y - bend, b.x, b.y - b.size); ctx.stroke();
      }
      const labels: { x: number; y: number; width: number }[] = [];
      for (const p of projected) {
        if (p.x < -30 || p.x > width + 30 || p.y < -25 || p.y > height + 25) continue;
        const lit = path.has(p.node.id), hovered = hoverRef.current === p.node.id;
        const family = p.node.kind === 'family', card = p.node.kind === 'card';
        ctx.fillStyle = p.node.practiced ? p.node.color : '#71818b';
        if (family || lit) {
          ctx.globalAlpha = lit ? .1 : .045;
          ctx.beginPath(); ctx.arc(p.x, p.y, p.size * 3, 0, Math.PI * 2); ctx.fill();
        }
        ctx.globalAlpha = p.node.practiced ? 1 : lit ? .6 : .3;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2); ctx.fill();
        if (hovered || current.current.selectedId === p.node.id) {
          ctx.strokeStyle = p.node.color; ctx.globalAlpha = .7; ctx.lineWidth = .8;
          ctx.beginPath(); ctx.arc(p.x, p.y, p.size + 4, 0, Math.PI * 2); ctx.stroke();
        }
        const label = p.node.kind === 'expression' ? p.node.id.split('-').at(-1)! : p.node.id;
        const fontSize = family ? 10.5 : card ? Math.min(10, Math.max(8, 8.5 * Math.sqrt(camera.zoom))) : 8;
        ctx.font = `${family ? '600 ' : ''}${fontSize}px ui-monospace, monospace`;
        const labelWidth = ctx.measureText(label).width, x = p.x - labelWidth / 2, y = p.y + (card ? 14 : -12);
        const overlaps = card && !lit && labels.some((r) => x < r.x + r.width + 2 && x + labelWidth + 2 > r.x && Math.abs(y - r.y) < 11);
        if (overlaps) continue;
        labels.push({ x, y, width: labelWidth });
        ctx.globalAlpha = p.node.practiced ? .95 : lit ? .7 : .4;
        ctx.fillStyle = p.node.practiced ? p.node.color : '#71818b'; ctx.fillText(label, x, y);
      }
      ctx.globalAlpha = 1;
    };
    frame = requestAnimationFrame(animate);
    const position = (e: { clientX: number; clientY: number }) => {
      const rect = canvas.getBoundingClientRect();
      return { x: (e.clientX - rect.left) * width / Math.max(1, rect.width), y: (e.clientY - rect.top) * height / Math.max(1, rect.height) };
    };
    const down = (e: PointerEvent) => {
      if (e.button !== 0) return;
      const p = position(e); pointer = p; pointers.set(e.pointerId, p); canvas.setPointerCapture(e.pointerId);
      if (pointers.size === 2) {
        const ps = [...pointers.values()]; pinchDistance = Math.hypot(ps[0].x - ps[1].x, ps[0].y - ps[1].y);
        if (gesture) gesture.moved = true;
        return;
      }
      const nodeId = hitNode(projected, p.x, p.y)?.node.id ?? null;
      gesture = { id: e.pointerId, start: p, last: p, moved: false, nodeId };
      setHover(nodeId);
    };
    const move = (e: PointerEvent) => {
      const p = position(e); pointer = p;
      if (pointers.has(e.pointerId)) pointers.set(e.pointerId, p);
      if (pointers.size === 2) {
        const ps = [...pointers.values()], distance = Math.hypot(ps[0].x - ps[1].x, ps[0].y - ps[1].y);
        if (pinchDistance > 0) zoomAt(distance / pinchDistance, { x: (ps[0].x + ps[1].x) / 2, y: (ps[0].y + ps[1].y) / 2 });
        pinchDistance = distance; return;
      }
      if (gesture && gesture.id === e.pointerId) {
        if (gesture.moved || Math.hypot(p.x - gesture.start.x, p.y - gesture.start.y) > 5) {
          camera.x += p.x - gesture.last.x; camera.y += p.y - gesture.last.y; limitPan();
          gesture.last = p; gesture.moved = true; setHover(null);
        }
      } else setHover(hitNode(projected, p.x, p.y)?.node.id ?? null);
    };
    const up = (e: PointerEvent) => {
      if (gesture && !gesture.moved && gesture.nodeId && pointers.size === 1) {
        current.current.onOpen(gesture.nodeId, { x: e.clientX, y: e.clientY, width: 18 });
      }
      pointers.delete(e.pointerId); gesture = null; pinchDistance = 0;
      if (pointers.size === 1) { const [id, p] = [...pointers][0]; gesture = { id, start: p, last: p, moved: true, nodeId: null }; }
      if (canvas.hasPointerCapture(e.pointerId)) canvas.releasePointerCapture(e.pointerId);
      if (e.pointerType === 'touch') pointer = null;
    };
    const cancel = (e: PointerEvent) => { pointers.delete(e.pointerId); gesture = null; pinchDistance = 0; pointer = null; setHover(null); };
    const leave = () => { if (!gesture) { pointer = null; setHover(null); } };
    const wheel = (e: WheelEvent) => {
      e.preventDefault();
      if (!e.ctrlKey && (e.shiftKey || Math.abs(e.deltaX) > Math.abs(e.deltaY))) {
        camera.x -= e.deltaX || e.deltaY; camera.y -= e.shiftKey ? 0 : e.deltaY; limitPan();
      } else zoomAt(Math.exp(-e.deltaY * (e.ctrlKey ? .008 : .0015)), position(e));
      setHover(null);
    };
    canvas.addEventListener('pointerdown', down); canvas.addEventListener('pointermove', move);
    canvas.addEventListener('pointerup', up); canvas.addEventListener('pointercancel', cancel); canvas.addEventListener('pointerleave', leave);
    canvas.addEventListener('wheel', wheel, { passive: false });
    return () => {
      cancelAnimationFrame(frame); observer.disconnect();
      canvas.removeEventListener('pointerdown', down); canvas.removeEventListener('pointermove', move);
      canvas.removeEventListener('pointerup', up); canvas.removeEventListener('pointercancel', cancel); canvas.removeEventListener('pointerleave', leave);
      canvas.removeEventListener('wheel', wheel);
    };
  }, [props.model]);

  return <div className="room-network" role="group" aria-label={t('自上而下的因子图谱，点击节点打开详情', 'Top-down factor trees. Click a node to open its details.')}>
    <canvas ref={canvasRef} aria-hidden="true" />
    <div className="network-node-accessibility" aria-label={t('图谱节点', 'Graph nodes')}>
      {props.model.nodes.filter((node) => node.kind !== 'root').map((node) => <button key={node.id}
        onFocus={() => controls.current.focus(node.id)} onBlur={() => props.onHover(null)} onClick={() => props.onOpen(node.id)}>
        {node.id} · {t(node.card?.name ?? node.expression?.name ?? node.family?.name)}
      </button>)}
    </div>
    <div className="network-controls">
      <button onClick={() => controls.current.zoom(1.25)} aria-label={t('放大', 'Zoom in')}>+</button>
      <button onClick={() => controls.current.zoom(.8)} aria-label={t('缩小', 'Zoom out')}>−</button>
      <button onClick={() => controls.current.reset()} aria-label={t('重置视角', 'Reset view')} title={t('重置视角', 'Reset view')}>⟲</button>
    </div>
  </div>;
}
