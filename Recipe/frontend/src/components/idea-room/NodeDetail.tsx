import { useLanguage } from '../../i18n';
import { SCOPE_LABEL, TYPE_LABEL, shortName } from '../../structure';
import type { FactorCard, Registry } from '../../types';
import type { IdeaNode } from './model';

export function NodeDetail({ node, registry, onSelect, onResults }: { onResults: (strategy: string) => void; node: IdeaNode; registry: Registry; onSelect: (id: string) => void }) {
  const { t, language } = useLanguage();
  const cardsOf = (predicate: (card: FactorCard) => boolean) => registry.cards.filter(predicate);
  const CardChip = ({ card }: { card: FactorCard }) => (
    <button className={registry.factorlab[card.factor_id] ? 'chip lit' : 'chip'} onClick={() => onSelect(card.factor_id)}>{card.factor_id}</button>
  );

  if (node.kind === 'root') {
    const practiced = cardsOf((card) => Boolean(registry.factorlab[card.factor_id]));
    return (
      <div className="detail-inner">
        <span className="kicker">STRUCTURE FRAMEWORK</span>
        <h2>{t('三轴结构')}</h2>
        <dl className="axis-list">
          <div><dt>A</dt><dd><b>{t('经济假设 → 家族')}</b>{t('每张 Card 只属于一个家族。')}</dd></div>
          <div><dt>B</dt><dd><b>{t('表达 → 家族内分簇')}</b>{t('同一假设的不同侧重，窗口对齐后可用 X 相关性检验。')}</dd></div>
          <div><dt>C</dt><dd><b>{t('结构 → Card 属性')}</b>{t('方向性 / 条件性 / 形状性；单标的 / 截面 / 多腿；数据需求。')}</dd></div>
        </dl>
        <h3>{t('家族')}</h3>
        <div className="detail-list">
          {registry.families.map((family) => (
            <button key={family.family_id} onClick={() => onSelect(family.family_id)}>
              <b>{family.family_id}</b><span>{t(family.name)}</span><small>{registry.cards.filter((card) => card.family === family.family_id).length}</small>
            </button>
          ))}
        </div>
        <h3>{t('Factorlab 已实践')}</h3>
        <div className="chip-row">{practiced.map((card) => <CardChip key={card.factor_id} card={card} />)}</div>
      </div>
    );
  }

  if (node.kind === 'family') {
    const family = node.family!;
    return (
      <div className="detail-inner">
        <span className="kicker">{t('AXIS A · 经济假设')}</span>
        <h2>{family.family_id} · {t(family.name)}</h2>
        <p className="detail-en">{t(family.name_en)} · {t('来源旧家族')} {family.legacy_families.join(' / ')}</p>
        <section><h3>Core Mechanism</h3><p>{t(family.core_mechanism)}</p></section>
        <section><h3>Core Hypothesis</h3><code>{t(family.core_hypothesis)}</code></section>
        {family.relations.length > 0 && <section><h3>{t('家族关系')}</h3>{family.relations.map((relation) => (
          <div className="relation-line" key={relation.type + relation.target}><button onClick={() => onSelect(relation.target)}>{relation.type} → {relation.target}</button><span>{t(relation.note)}</span></div>
        ))}</section>}
        <section><h3>{t('轴 B 表达')}</h3>{family.expressions.map((expression) => (
          <div className="expression-line" key={expression.expression_id}>
            <button onClick={() => onSelect(expression.expression_id)}><b>{expression.expression_id}</b> {t(expression.name)}</button>
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
        <span className="kicker">AXIS B · {t('表达')} · {node.family!.family_id} {t(node.family!.name)}</span>
        <h2>{expression.expression_id} · {t(expression.name)}</h2>
        <section><h3>{t('表达定义')}</h3><p>{t(expression.description)}</p></section>
        {expression.architecture_ref && <section><h3>{t('架构参考')}</h3><p>{t(expression.architecture_ref)}</p></section>}
        <section><h3>{t('Cards · 轴 C')}</h3>
          <div className="member-table">
            {members.map((card) => (
              <button key={card.factor_id} className={registry.factorlab[card.factor_id] ? 'lit' : ''} onClick={() => onSelect(card.factor_id)}>
                <b>{card.factor_id}</b><span>{shortName(card, language)}</span><small>{t(TYPE_LABEL[card.structure.type])} · {t(SCOPE_LABEL[card.structure.scope])}</small>
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
  const empty = t('未填写');
  const text = (value: string | null) => t(value) || empty;
  return (
    <div className="detail-inner">
      <span className="kicker">CARD · {card.family} / {card.expression} · {t('旧')} {card.legacy_family}</span>
      <h2>{card.factor_id}</h2>
      <p className="detail-en">{t(card.name)}</p>
      <div className="tag-row">{card.tags.map((tag) => <span key={tag}>{tag}</span>)}</div>
      <div className={strategies.length ? 'practice-state lit' : 'practice-state'}>{strategies.length ? t(`Factorlab 已实践 · ${strategies.length} 个注册`, `Implemented in Factorlab · ${strategies.length} strategies`) : t('尚未在 Factorlab 实践')}</div>
      <dl className="structure-grid">
        <div><dt>{t('A 家族')}</dt><dd><button onClick={() => onSelect(card.family)}>{t(family?.name)}</button></dd></div>
        <div><dt>{t('B 表达')}</dt><dd><button onClick={() => onSelect(card.expression)}>{t(expression?.name)}</button></dd></div>
        <div><dt>{t('C 结构类型')}</dt><dd>{t(TYPE_LABEL[card.structure.type])}</dd></div>
        <div><dt>{t('C 标的范围')}</dt><dd>{t(SCOPE_LABEL[card.structure.scope])}</dd></div>
        <div><dt>{t('C 数据需求')}</dt><dd>{card.structure.data.join(' + ')}</dd></div>
        <div><dt>{t('两层可分')}</dt><dd>{card.structure.layer_separable ? 'true' : 'false'}</dd></div>
      </dl>
      <section><h3>Idea Summary</h3><p>{text(card.idea_summary)}</p></section>
      <section><h3>Mathematical Construction</h3><p className="text-block">{text(card.mathematical_construction)}</p></section>
      <section><h3>Observable Data</h3><p className="text-block">{text(card.observable_data)}</p></section>
      <section><h3>Temporal Structure</h3><p className="text-block">{text(card.temporal_structure)}</p></section>
      <section>
        <h3>Relationships</h3>
        <div className="relation-row"><label>COMPETES WITH</label>{card.competes_with.length ? card.competes_with.map((item) => <button onClick={() => onSelect(item)} key={item}>{item}</button>) : <span>—</span>}</div>
        <div className="relation-row"><label>COMPOSED WITH</label>{card.composed_with.length ? card.composed_with.map((item) => <button onClick={() => onSelect(item)} key={item}>{item}</button>) : <span>—</span>}</div>
      </section>
      <section><h3>Economic Failure Modes</h3><p className="text-block">{text(card.economic_failure_modes)}</p></section>
      {strategies.length > 0 && <section><h3>{t('Factorlab 注册')}</h3>{strategies.map((strategy) => (
        <div className="strategy-line" key={strategy.strategy_id}><b>{strategy.strategy_id}</b><span>{t(strategy.name)} · {strategy.frequency}</span><button className="strategy-link" onClick={() => onResults(strategy.strategy_id)}>{t("查看回测 ↗", "Open results ↗")}</button></div>
      ))}</section>}
      <footer className="source-line">SOURCE · {card.source.document}:{card.source.line} · GENERATED BY {registry.generated_by}</footer>
    </div>
  );
}
