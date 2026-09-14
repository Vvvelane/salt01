import { useLanguage } from '../i18n';
import type { Strategy } from '../types';

export function ResearchAlert() {
  const { t } = useLanguage();
  const items = [
    ['价格与成交', 'Prices & fills', 'FRV / FCM 信号目前使用 close；FTR 交易日锚点已使用 open，FID 开盘区间依赖 high / low。成交已采用下一根 open，另计不利滑点；后续扩展价格表达，而非首次引入 open。', 'FRV / FCM signals use close. FTR uses an opening anchor; FID uses range highs and lows. Fills already use the next open with adverse slippage. Future work broadens price constructions.'],
    ['数据边界', 'Data coverage', '使用已发布的未复权主连，尚未自行重建连续合约。缺失分钟未补成完整时间网格；无效、零量和平 OHLC 观测按规则跳过。观测窗口可能长于墙钟时间。', 'Published, unadjusted main series; no independently reconstructed continuous contract. Missing minutes are not filled onto a complete grid. Invalid, zero-volume and flat OHLC observations are filtered. Observation windows can exceed elapsed clock time.'],
    ['市场微观结构', 'Market microstructure', '暂无 Level 2、逐笔成交或实时 data feed 接口。OHLC 无法还原 bar 内真实价格顺序；日度涨跌停表尚未接入成交判定，止损也不能代表真实逐笔成交。', 'No Level 2, tick-by-tick or live data feed connection. OHLC does not recover the intrabar path. Daily price limits are not yet integrated into execution checks; stops are not tick-level executions.'],
    ['研究口径', 'Research conventions', '研究池来自当下选定的 11 品种，存在选样偏差；历史时段采用当前规则情景。单品种按一手独立记账，无账户风控；FCM 则是分数权重的标准化收益，不能与货币 PnL 相加。', 'The 11-product pool is selected today and carries selection bias. Historical sessions use a current-rules scenario. Single-product runs trade one lot independently, without account risk controls; FCM uses fractional-weight normalized returns, not currency PnL.'],
    ['更新与复现', 'Updates & reproducibility', '页面读取已完成的 v3_10y 文件，不运行参数搜索或实时回测。参数展示优先使用该次运行保存的快照；手续费已入账，滑点点数表显示当前配置，未声称历史逐时费率。', 'This page reads completed v3_10y artifacts, without parameter search or live backtesting. Parameters come from the saved run snapshot. Fees are already booked; the slippage table shows current configuration, not historical point-in-time rates.'],
  ];
  return <details className="research-alert"><summary><span>!</span><div><b>{t('版本说明与已知问题', 'Version notes & known limitations')}</b><small>FACTORLAB · RESEARCH BUILD</small></div><i>⌄</i></summary><div className="alert-body">{items.map(([cn, en, body, english]) => <section key={en}><h3>{t(cn, en)}</h3><p>{t(body, english)}</p></section>)}</div></details>;
}

export function SignalFormula({ strategy: s }: { strategy: Strategy }) {
  const f = (v: unknown) => Number(v) || 0;
  let numerator = '<mi>raw</mi>', denominator = '<msub><mi>σ</mi><mrow><mi>t</mi><mo>−</mo><mn>1</mn></mrow></msub><mo>·</mo><msqrt><mi>n</mi></msqrt>';
  if (s.implementation === 'rolling_displacement') numerator = `${Number(s.signal_sign) < 0 ? '<mo>−</mo>' : ''}<mi>ln</mi><mo>(</mo><mfrac><msub><mi>C</mi><mi>t</mi></msub><msub><mi>C</mi><mrow><mi>t</mi><mo>−</mo><mn>${f(s.lookback_bars)}</mn></mrow></msub></mfrac><mo>)</mo>`;
  if (s.implementation === 'daily_scale_displacement') numerator = `<mo>−</mo><mi>ln</mi><mo>(</mo><mfrac><msub><mi>C</mi><mi>t</mi></msub><msub><mi>C</mi><mrow><mi>D</mi><mo>−</mo><mn>${f(s.lookback_days)}</mn></mrow></msub></mfrac><mo>)</mo>`;
  if (s.implementation === 'trading_day_anchor') { numerator = '<mi>ln</mi><mo>(</mo><msub><mi>C</mi><mi>t</mi></msub><mo>/</mo><msub><mi>O</mi><mtext>anchor</mtext></msub><mo>)</mo>'; denominator = '<msub><mi>σ</mi><mrow><mi>t</mi><mo>−</mo><mn>1</mn></mrow></msub><msqrt><mi>elapsed</mi><mo>+</mo><mi>gap</mi></msqrt>'; }
  if (s.implementation === 'opening_range') { numerator = '<msub><mi>C</mi><mi>t</mi></msub><mo>−</mo><mo>(</mo><mi>H</mi><mo>+</mo><mi>L</mi><mo>)</mo><mo>/</mo><mn>2</mn>'; denominator = '<mo>(</mo><mi>H</mi><mo>−</mo><mi>L</mi><mo>)</mo><mo>/</mo><mn>2</mn>'; }
  const formula = s.unit === 'return' ? '<msub><mi>g</mi><mi>i</mi></msub><mo>=</mo><mn>1</mn><mo>−</mo><mfrac><mrow><mn>2</mn><mo>(</mo><msub><mi>rank</mi><mi>i</mi></msub><mo>−</mo><mn>0.5</mn><mo>)</mo></mrow><mi>N</mi></mfrac>' : `<msub><mi>X</mi><mi>t</mi></msub><mo>=</mo><mfrac><mrow>${numerator}</mrow><mrow>${denominator}</mrow></mfrac>`;
  return <div className="signal-formula" dangerouslySetInnerHTML={{ __html: `<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">${formula}</math>` }}/>;
}

export function StrategyRules({ strategy: s }: { strategy: Strategy }) {
  const { t } = useLanguage();
  const basket = s.unit === 'return', opening = s.implementation === 'opening_range';
  const k = Number(s.entry_threshold), b = Number(s.exit_threshold);
  const holding = s.derived_holding_trading_days ? `${s.lookback_days} ${t('个交易日', 'trading days')}` : s.derived_holding_bars ? `${s.lookback_bars} bars` : s.max_holding_bars ? `${s.max_holding_bars} bars` : t('至时段边界', 'Until scope boundary');
  const descriptions: Record<string, [string, string]> = {
    rolling_displacement: [`${s.lookback_bars} 个有效分钟观测的对数位移，以滞后 ${s.volatility_lookback} 观测波动率标准化；n 为回看观测数。`, `Log displacement over ${s.lookback_bars} valid minute observations, scaled by lagged ${s.volatility_lookback}-observation volatility; n is the lookback.`],
    trading_day_anchor: [`交易日首个有效 open 为锚点；至少 ${s.minimum_elapsed_bars} 个等效观测后入场。夜日跳空方差在校准期固定，进入日盘后加入尺度。`, `Anchor: first valid open of the trading date. At least ${s.minimum_elapsed_bars} effective observations before entry. Calibrated night/day gap variance enters the scale after the day session opens.`],
    daily_scale_displacement: [`每个分钟 close 对比 ${s.lookback_days} 个交易日前 close；n=${s.lookback_days}，日波动率窗口 ${s.volatility_lookback_days}，只使用已完成日线且锚点须同合约。`, `Each minute close vs the close ${s.lookback_days} trading dates ago; n=${s.lookback_days}, daily volatility window ${s.volatility_lookback_days}. Completed daily bars only, with the same contract as the anchor.`],
    opening_range: [`${s.session_name} session 前 ${s.opening_range_bars} 个有效 bar 固定 H / L；突破区间才产生方向。`, `Freeze H / L from the first ${s.opening_range_bars} valid bars of the ${s.session_name} session; a range breakout proposes direction.`],
    cross_sectional_momentum: [`${s.lookback_days} 日 close 动量 / ${s.volatility_lookback_days} 日波动率；10 品种降序排名，同分取平均名次，再映射到 g。`, `${s.lookback_days}-day close momentum / ${s.volatility_lookback_days}-day volatility. Descending ranks across 10 products; ties use average rank, then map to g.`],
  };
  return <div className="strategy-rules"><div className="construction"><span className="kicker">SIGNAL CONSTRUCTION</span><SignalFormula strategy={s}/><p>{t(...(descriptions[s.implementation] ?? ['', '']))}</p></div><div className="rule-grid">
    <div><small>{t('入场逻辑', 'Entry')}</small><p>{basket ? t('|g| ≥ 0.6；各取 2 个多头 / 空头，同名次不任意打破。', '|g| ≥ 0.6; capacity 2 long / 2 short, without arbitrary tie breaking.') : `${t('空仓时', 'When flat')} |X| > ${k}; pos = sign(X).`}</p></div>
    <div><small>{t('出场逻辑', 'Exit')}</small><p>{basket ? t('多头 g < 0.2 / 空头 g > −0.2 才退出；先保留合格持仓，再补空位。', 'Long exits below 0.2; short exits above −0.2. Retain eligible members before filling empty slots.') : `${t('先检查', 'Check first')} X × pos < ${b}; ${holding}.`}</p></div>
    <div><small>{t('持仓与止损', 'Position & stops')}</small><p>{basket ? t('多头 +1、空头 −1，总敞口 2；腿内等权，分数权重，无整数手数 / 账户止损。', 'Long +1, short −1, gross 2; equal weights within each leg, fractional sizing, no account stop.') : opening ? t(`初始止损为开盘区间另一端；持仓方向 X 从峰值回撤阈值 ${s.drawdown_threshold}，形状与持仓路径耦合；每方向一次。`, `Initial stop at the opposite range boundary; held-direction X peak-to-current drawdown threshold ${s.drawdown_threshold}. Shape and position path are coupled; one entry per direction.`) : t('每品种固定一手，不加仓；无固定价格止损 / 止盈。信号、持有期限和时段规则控制退出。', 'One lot per product, no pyramiding or fixed price stop / take profit. Signal, holding horizon and session rules control exits.')}</p></div>
    <div><small>{t('制度与执行', 'Institution & execution')}</small><p>{basket ? t('T 日收盘信号 → 下一交易日日盘 open；整篮全成或全不成；已发布主连换月前一日预平。', 'T-close signal → next trading-date day open; all-or-none basket execution; pre-close one day before the published main roll.') : t(`指定下一根 bar 的 open 尝试成交；不在同一事件反手。${s.holding_scope === 'research_period' ? '允许跨 session，研究末端平仓。' : '时段结束前 5 分钟停止入场并尝试平仓。'}`, `Attempt at the designated next-bar open, no same-event reversal. ${s.holding_scope === 'research_period' ? 'May cross sessions; liquidate at research end.' : 'Stop entry and attempt liquidation in the final 5 minutes of the scope.'}`)}</p></div>
  </div></div>;
}
