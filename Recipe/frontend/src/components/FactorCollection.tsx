import { useEffect, useRef, useState } from 'react';
import { useLanguage } from '../i18n';
import type { Strategy } from '../types';
import { Keeper } from './idea-room/Keeper';
import { Sigil } from './idea-room/Decks';
import { ResearchAlert } from './ResearchRules';
import './idea-room/idea-room.css';

export function FactorCollection({ strategies, onSelect }: { strategies: Strategy[]; onSelect: (id: string) => void }) {
  const { t } = useLanguage();
  const factors = [...new Map(strategies.filter((s) => s.ready).map((s) => [s.factor_id, s])).values()];
  const [running, setRunning] = useState(!window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const state = useRef({ angle: 0, speed: .18, running, drag: false, x: 0, last: 0, start: 0, moved: false });
  state.current.running = running;
  const cards = useRef<(HTMLButtonElement | null)[]>([]);
  const space = useRef<HTMLDivElement>(null);
  useEffect(() => {
    let frame = 0, last = performance.now();
    const animate = (now: number) => {
      const s = state.current, dt = Math.min(.05, (now - last) / 1000); last = now;
      if (s.running && !s.drag) { s.angle += s.speed * dt; s.speed += (.18 - s.speed) * Math.min(1, dt * .15); }
      const radius = Math.min(330, (space.current?.clientWidth ?? 900) * .29);
      cards.current.forEach((card, i) => {
        if (!card) return;
        const a = s.angle + i / factors.length * Math.PI * 2, depth = Math.cos(a), scale = .78 + (depth + 1) * .18;
        card.style.transform = `translate(-50%, -50%) translate(${Math.sin(a) * radius}px, ${depth * 42}px) scale(${scale}) rotateY(${-Math.sin(a) * 25}deg)`;
        card.style.zIndex = String(Math.round((depth + 1) * 100)); card.style.opacity = String(.55 + (depth + 1) * .225);
      });
      frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate); return () => cancelAnimationFrame(frame);
  }, [factors.length]);
  return <section className="factor-collection"><div className="collection-top"><ResearchAlert/><span className="room-eyebrow">NaCl <i/> COMPLETED EXPERIMENTS</span></div>
    <div className="collection-title"><span className="kicker">FACTORLAB / COLLECTION</span><h1>{t('让研究进入轨道', 'Research in orbit')}</h1><p>{factors.length} {t('个已测试 idea', 'tested ideas')} · {strategies.filter((s) => s.ready).length} {t('个注册配置', 'registered configurations')}</p></div>
    <div className="factor-orbit" ref={space} onPointerDown={(e) => {
      if (e.button !== 0) return; const s = state.current;
      s.drag = true; s.start = e.clientX; s.x = e.clientX; s.last = performance.now(); s.moved = false;
    }} onPointerMove={(e) => {
      const s = state.current; if (!s.drag) return;
      if (Math.abs(e.clientX - s.start) > 5) { s.moved = true; e.currentTarget.setPointerCapture(e.pointerId); }
      const now = performance.now(), delta = e.clientX - s.x;
      s.angle += delta * .009; s.speed = Math.max(-5, Math.min(5, delta * .009 / Math.max(.008, (now - s.last) / 1000))); s.x = e.clientX; s.last = now;
    }} onPointerUp={() => { const s = state.current; s.drag = false; if (s.moved) setRunning(true); }} onPointerCancel={() => { state.current.drag = false; }} onPointerLeave={() => { if (!state.current.moved) state.current.drag = false; }}>
      <div className="orbit-ring"/><div className="orbit-ring secondary"/><div className="orbit-core">S<span>RESEARCH ENGINE</span></div>
      {factors.map((strategy, i) => <button className="orbit-factor-card" key={strategy.factor_id} ref={(node) => { cards.current[i] = node; }} onClick={() => { if (!state.current.moved) onSelect(strategies.find((s) => s.factor_id === strategy.factor_id && s.ready)!.strategy_id); }}><span className="card-edition">FACTORLAB <i className="practice-dot"/></span><Sigil index={[0, 1, 4, 6][i] ?? i}/><b>{strategy.factor_id}</b><span>{t(strategy.factor_id === 'FTR001' ? '趋势动量' : strategy.factor_id === 'FRV001' ? '均值回归' : strategy.factor_id === 'FID004' ? '开盘区间突破' : '截面动量', strategy.factor_id === 'FTR001' ? 'Trend momentum' : strategy.factor_id === 'FRV001' ? 'Mean reversion' : strategy.factor_id === 'FID004' ? 'Opening range breakout' : 'Cross-sectional momentum')}</span><small>{strategies.filter((s) => s.factor_id === strategy.factor_id && s.ready).length} {t('种配置', 'configurations')} ↗</small></button>)}
    </div>
    <div className="orbit-controls"><button onClick={() => { if (!running) state.current.speed = .18; setRunning(!running); }}>{running ? 'Ⅱ' : '▶'} {running ? t('停转', 'Stop') : t('旋转', 'Spin')}</button><button onClick={() => { state.current.speed = Math.min(5, Math.abs(state.current.speed) + 1.2); setRunning(true); }}>↻ {t('加速', 'Accelerate')}</button><small>{t('拖动拨转 · 点击卡片进入', 'Swipe to spin · Click a card to enter')}</small></div>
    <div className="collection-keeper"><Keeper network={false} onToggle={() => setRunning(!running)} label={t('拨动研究轨道', 'Set the research orbit in motion')}/></div>
  </section>;
}
