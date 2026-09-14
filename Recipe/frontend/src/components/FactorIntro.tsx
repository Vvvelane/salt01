import { useEffect, useState } from 'react';
import { api } from '../api';
import { useLanguage } from '../i18n';
import type { Replay, Strategy } from '../types';
import { SignalFormula } from './ResearchRules';
import { formatValue, linePath } from './PerformanceChart';

export const minuteTime = (value: unknown) => value == null ? '—' : String(value).replace('T', ' ').slice(0, 16);
export function FactorIntro({ strategy, onEnter, onBack }: { strategy: Strategy; onEnter: () => void; onBack: () => void }) {
  const { t } = useLanguage();
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(!window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const [replay, setReplay] = useState<Replay>();
  const [error, setError] = useState('');
  const [frame, setFrame] = useState(0);
  const [example, setExample] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    api.replay(strategy.strategy_id, controller.signal).then(setReplay).catch((e) => { if (!controller.signal.aborted) setError(String(e)); });
    return () => controller.abort();
  }, [strategy.strategy_id]);
  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => setStep((s) => (s + 1) % 4), 2600);
    return () => window.clearInterval(timer);
  }, [playing]);
  useEffect(() => {
    if (!playing || !replay?.bars.length) return;
    const timer = window.setInterval(() => setFrame((f) => (f + 1) % replay.bars.length), Math.max(80, 9000 / replay.bars.length));
    return () => window.clearInterval(timer);
  }, [playing, replay]);
  const stages = [
    ['ECONOMIC', '经济层', 'Economic layer', '只读取当时已知市场信息与上一方向，生成 X 和方向建议。先退场，再检查空仓入场。架构写作 ≤ b，当前 v3 实际实现为严格 < b。纯经济零阈值是参照；当前注册策略使用固定 k / b，不进行参数搜索。', 'Read market information known at t and the previous direction. Build X and a direction proposal. Check exits before new entries. The architecture uses ≤ b; v3 implements strict < b. Zero economic thresholds are a reference; registered runs use fixed k / b, without parameter search.'],
    ['POSITION', '持仓层', 'Position layer', '加入入场价、持仓极值、账户状态和数量。止损、止盈、回撤规则可以否决持仓，不能创造新的方向。当前一手策略没有账户级 sizing；FID 的路径止损与形状机制不可完全拆开。', 'Add entry price, held-position extrema, account state and quantity. Stops and drawdown controls can veto a position but cannot invent direction. One-lot runs have no account-level sizing; FID couples path-dependent stops to shape.'],
    ['INSTITUTION', '制度层', 'Institutional layer', '交易所、时钟与换月约束具有最高否决权：即使经济信号继续看多，时段平仓也会使持仓归零。当前涨跌停判定仍是数据代理，真实限制有待补齐。', 'Exchange, clock and roll constraints have the highest veto priority. A session close may flatten a bullish signal. Price-limit handling still relies on data proxies; complete exchange restrictions remain future work.'],
    ['EXECUTION', '执行与摩擦', 'Execution & friction', '收盘计算信号，指定下一根 open 尝试成交并扣除手续费、滑点。v3 不允许同事件反手。架构中 exit_layer 是归因目标，目前文件保存的是 exit_reason。', 'Evaluate at close; attempt a fill at the designated next open, with fees and slippage. v3 forbids same-event reversal. The architecture proposes exit_layer attribution; saved ledgers currently contain exit_reason.'],
  ];
  const examples = [
    [t('信号退场', 'Signal exit'), t('示例：持有多头，X 从 +0.8 降到 −0.1，b=0。经济层建议清仓 → 持仓层接受 → 制度层允许 → 下一 open 平仓。', 'Example: held long; X falls from +0.8 to −0.1 with b=0. Economic proposal flattens → position layer accepts → institutional rules allow → exit at the next open.')],
    [t('持仓止损', 'Position stop'), t('示例：经济信号仍看多，但价格触及依赖入场价的止损线。持仓层否决继续持有；这不是经济假设本身反转。此示例不表示 FTR / FRV 已启用价格止损。', 'Example: the signal remains bullish, but price hits an entry-dependent stop. The position layer vetoes holding. This does not reverse the economic hypothesis, and does not imply that FTR / FRV use a price stop.')],
    [t('制度平仓', 'Institutional exit'), t('示例：信号和持仓规则都允许继续持有，时段结束前的强平规则仍优先清仓；FCM 还受整篮可执行性与换月规则限制。', 'Example: signal and position rules allow holding, but session liquidation takes priority. FCM also depends on basket-wide executability and roll rules.')],
  ];
  const prices = replay?.bars.map((b) => b.close ?? b.open ?? 0) ?? [];
  const lo = Math.min(...prices), hi = Math.max(...prices), spread = hi - lo || 1;
  const x = (i: number) => 25 + i / Math.max(1, prices.length - 1) * 730;
  const y = (price: number) => 125 - (price - lo) / spread * 100;
  const trade = replay?.trade;
  return <section className="factor-intro">
    <header><button className="quiet-button" onClick={onBack}>← {t('卡片库', 'Collection')}</button><span className="kicker">{strategy.factor_id} / MODEL → TRADE</span><button className="quiet-button" onClick={() => setPlaying(!playing)}>{playing ? 'Ⅱ' : '▶'}</button></header>
    <div className="intro-heading"><h1>{t('一个信号，如何成为一笔交易', 'From a signal to a trade')}</h1><p>{t('先提出方向，再通过持仓与制度约束，最后执行。', 'Propose direction, apply position and institutional constraints, then execute.')}</p></div>
    <div className="layer-pipeline">{stages.map(([code, cn, en], i) => <button key={code} className={step === i ? 'active' : ''} onClick={() => { setStep(i); setPlaying(false); }}><span>0{i + 1}</span><b>{t(cn, en)}</b><small>{code}</small>{i < 3 && <i>→</i>}</button>)}</div>
    <div className="layer-description" key={step}><span className="kicker">0{step + 1} / {stages[step][0]}</span><h2>{t(stages[step][1], stages[step][2])}</h2><p>{t(stages[step][3], stages[step][4])}</p></div>
    <div className="intro-columns"><article className="model-primer"><span className="kicker">META MODEL · ECONOMIC PROPOSAL</span><SignalFormula strategy={strategy}/><p>{t('共同框架：价格 → 原始表达 → 用已知历史尺度标准化 → X → 方向状态机。FTR 矩形核是净位移，FRV 反向读取位移；FID 使用开盘区间尺度；FCM 将波动率调整动量转成截面排名。', 'Shared framework: price → raw expression → scale with known history → X → direction state machine. FTR uses a rectangular displacement kernel, FRV reverses displacement, FID scales by the opening range, and FCM maps volatility-adjusted momentum to cross-sectional ranks.')}</p><p className="subtle">{t('架构中的周转率推导阈值仍属待定，不是当前实现。滚动窗口与持有期限是两个独立设定；条件型 idea（如成交量门控）必须与方向信号组合。', 'Turnover-derived thresholds in the architecture remain tentative. Lookback and holding horizon are separate settings. Conditional ideas such as volume gates require a directional signal.')}</p><div className="example-tabs">{examples.map(([label], i) => <button key={i} className={example === i ? 'active' : ''} onClick={() => setExample(i)}>{label}</button>)}</div><p>{examples[example][1]}</p></article>
      <article className="ledger-replay"><span className="kicker">SAVED LEDGER · {t('真实样本回放', 'REAL TRADE EXAMPLE')}</span>
        {error ? <p className="error-banner">{error}</p> : !replay ? <p>{t('读取成交及对应行情…', 'Loading ledger and source bars…')}</p> : !trade ? <p>{t('没有可回放成交', 'No saved trade to replay')}</p> : <>
          <div className="replay-caption"><b>{String(trade.contract)} · {String(trade.side)}</b><span>{minuteTime(replay.bars[frame]?.ts)}</span></div>
          {prices.length > 0 && <svg viewBox="0 0 780 160" role="img" aria-label={t('该成交对应的真实价格记录', 'Actual source prices around the saved trade')}><path d={linePath(prices.map((p, i) => ({ x: x(i), y: y(p) })))} fill="none" stroke="#304742" strokeWidth="1.5"/><path d={linePath(prices.slice(0, frame + 1).map((p, i) => ({ x: x(i), y: y(p) })))} fill="none" stroke="#c9e6a7" strokeWidth="2"/><circle cx={x(frame)} cy={y(prices[frame])} r="4" fill="#d7ff64"/></svg>}
          <input aria-label={t('回放位置', 'Replay position')} type="range" min="0" max={Math.max(0, prices.length - 1)} value={frame} onChange={(e) => { setFrame(Number(e.target.value)); setPlaying(false); }}/>
          <dl className="replay-events"><div><dt>{t('信号已知', 'Signal known')}</dt><dd>{minuteTime(trade.entry_signal_time ?? replay.ranking?.signal_time ?? trade.signal_date)}<small>{replay.ranking ? `g = ${formatValue(Number(replay.ranking.g), false, 3)}` : `X = ${formatValue(Number(trade.entry_signal), false, 3)}`}</small></dd></div><div><dt>{t('实际成交', 'Saved fill')}</dt><dd>{minuteTime(trade.entry_time ?? trade.execution_time)}<small>{String(trade.entry_price ?? trade.price)}</small></dd></div>{trade.action && <div><dt>{t('操作 / 原因', 'Action / reason')}</dt><dd>{String(trade.action)}<small>{String(trade.reason)}</small></dd></div>}{trade.exit_time && <div><dt>{t('退出', 'Exit')}</dt><dd>{minuteTime(trade.exit_time)}<small>{String(trade.exit_reason)} · {String(trade.exit_price)}</small></dd></div>}</dl>
          <p className="subtle">{t('曲线来自本地分钟 bar；信号数值来自成交 / 排名文件，仅展示已保存的信号时点。动画推进的是历史记录，不是实时计算。', 'The curve uses local minute bars; signal values come from the trade / ranking ledger at saved signal times. Animation advances historical records, not a live calculation.')}{replay.sampled && t(' 长持仓价格序列已抽样，保留真实时间。', ' Long-hold prices are sampled, preserving actual timestamps.')}</p>
        </>}
      </article></div>
    <footer><small>NaCl / factor_architecture.md · {t('架构与当前 v3 实现分开说明', 'Architecture distinguished from current v3 implementation')}</small><button className="enter-results" onClick={onEnter}>{t('进入完整回测', 'Open full results')} <span>↗</span></button></footer>
  </section>;
}
