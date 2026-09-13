import { useEffect, useMemo, useState } from 'react';
import { api } from '../api';
import { SCOPE_LABEL, TYPE_LABEL } from '../structure';
import type { FactorCard, Registry } from '../types';

function TextBlock({ value, empty = '未填写' }: { value: string | null; empty?: string }) {
  return <div className={value ? 'text-block' : 'text-block empty'}>{value || empty}</div>;
}

export function Cards({ focusId }: { focusId: string | null }) {
  const [registry, setRegistry] = useState<Registry | null>(null);
  const [familyId, setFamilyId] = useState('ALL');
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState<FactorCard | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.cards().then((data) => {
      setRegistry(data);
      setSelected(data.cards.find((card) => card.factor_id === focusId) ?? data.cards[0] ?? null);
    }).catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)));
  }, [focusId]);

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return (registry?.cards ?? []).filter((card) => {
      const inFamily = familyId === 'ALL' || card.family === familyId;
      const haystack = `${card.factor_id} ${card.name} ${card.expression} ${card.legacy_family} ${card.tags.join(' ')}`.toLowerCase();
      return inFamily && (!needle || haystack.includes(needle));
    });
  }, [registry, familyId, query]);

  const family = registry?.families.find((item) => item.family_id === selected?.family) ?? null;
  const expression = family?.expressions.find((item) => item.expression_id === selected?.expression) ?? null;
  const strategies = selected ? registry?.factorlab[selected.factor_id] ?? [] : [];
  const expressionCount = registry?.families.reduce((n, item) => n + item.expressions.length, 0) ?? 0;

  function follow(reference: string) {
    const card = registry?.cards.find((item) => item.factor_id === reference);
    if (card) {
      setSelected(card);
      setFamilyId('ALL');
      setQuery('');
      return;
    }
    const relatedFamily = registry?.families.find((item) => item.family_id === reference);
    if (relatedFamily) setFamilyId(relatedFamily.family_id);
  }

  return (
    <div className="cards-page">
      <div className="page-heading registry-heading">
        <div><span className="kicker">KNOWLEDGE SOURCE / STRUCTURED JSON</span><h1>NaCl Factor Registry</h1><p>轴 A 经济假设 → 轴 B 表达 → Card；轴 C 结构只作属性。构造类型表示技术组织方式，不表示经济学父子层级。</p></div>
        <div className="registry-stats"><div><strong>{registry?.cards.length ?? 0}</strong><span>CARDS</span></div><div><strong>{expressionCount}</strong><span>EXPRESSIONS</span></div><div><strong>{registry?.families.length ?? 0}</strong><span>FAMILIES</span></div></div>
      </div>
      {error && <div className="error-banner">{error}</div>}
      <div className="family-strip">
        <button className={familyId === 'ALL' ? 'selected' : ''} onClick={() => setFamilyId('ALL')}><b>ALL</b><span>全部</span></button>
        {registry?.families.map((item) => <button key={item.family_id} className={familyId === item.family_id ? 'selected' : ''} onClick={() => setFamilyId(item.family_id)}><b>{item.family_id}</b><span>{item.name}</span></button>)}
      </div>
      <div className="registry-layout">
        <aside className="card-index panel">
          <div className="search-box"><span>SEARCH</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="ID、名称、表达或旧家族" /></div>
          <div className="result-count">{filtered.length} RESULTS</div>
          <div className="card-list">
            {filtered.map((card) => (
              <button key={card.factor_id} className={`${selected?.factor_id === card.factor_id ? 'selected' : ''}${registry?.factorlab[card.factor_id] ? ' practiced' : ''}`} onClick={() => setSelected(card)}>
                <div><b>{card.factor_id}</b><span>{card.expression}</span></div>
                <strong>{card.name}</strong>
                <small>{TYPE_LABEL[card.structure.type]} · {SCOPE_LABEL[card.structure.scope]} · {card.structure.data.join(' + ')}</small>
              </button>
            ))}
          </div>
        </aside>
        <article className="card-detail panel">
          {selected ? <>
            <header className="card-title"><div><div className="id-line"><span>{selected.factor_id}</span><span>{selected.expression}</span><span>旧 {selected.legacy_family}</span><span>{selected.construction_kind || 'UNSET'}</span>{strategies.length > 0 && <span className="practiced-tag">FACTORLAB · {strategies.length}</span>}</div><h2>{selected.name}</h2><div className="tag-row">{selected.tags.map((tag) => <span key={tag}>{tag}</span>)}</div></div><div className="family-seal"><b>{selected.family}</b><span>{family?.name}</span></div></header>
            <section className="family-context">
              <span className="kicker">AXIS A · FAMILY THESIS</span><p>{family?.core_mechanism || '未填写'}</p><code>{family?.core_hypothesis || '—'}</code>
              <div className="expression-context"><span className="kicker">AXIS B · {expression?.expression_id} {expression?.name}</span><p>{expression?.description}</p></div>
            </section>
            <dl className="structure-strip">
              <div><dt>C 结构类型</dt><dd>{TYPE_LABEL[selected.structure.type]}</dd></div>
              <div><dt>C 标的范围</dt><dd>{SCOPE_LABEL[selected.structure.scope]}</dd></div>
              <div><dt>C 数据需求</dt><dd>{selected.structure.data.join(' + ')}</dd></div>
              <div><dt>LAYER SEPARABLE</dt><dd>{String(selected.structure.layer_separable)}</dd></div>
            </dl>
            <div className="definition-grid">
              <section><span className="section-number">01</span><h3>Idea Summary</h3><TextBlock value={selected.idea_summary} /></section>
              <section><span className="section-number">02</span><h3>Mathematical Construction</h3><TextBlock value={selected.mathematical_construction} /></section>
              <section><span className="section-number">03</span><h3>Observable Data</h3><TextBlock value={selected.observable_data} /></section>
              <section><span className="section-number">04</span><h3>Temporal Structure</h3><TextBlock value={selected.temporal_structure} /></section>
            </div>
            <section className="detail-section"><span className="kicker">RELATIONSHIPS</span><div className="relation-row"><label>COMPETES WITH</label>{selected.competes_with.length ? selected.competes_with.map((item) => <button onClick={() => follow(item)} key={item}>{item}</button>) : <span>—</span>}</div><div className="relation-row"><label>COMPOSED WITH</label>{selected.composed_with.length ? selected.composed_with.map((item) => <button onClick={() => follow(item)} key={item}>{item}</button>) : <span>—</span>}</div></section>
            <section className="detail-section"><span className="kicker">ECONOMIC FAILURE MODES</span><TextBlock value={selected.economic_failure_modes} /></section>
            <footer className="source-line">SOURCE · {selected.source.document}:{selected.source.line} · GENERATED BY {registry?.generated_by}</footer>
          </> : <div className="chart-empty">选择一张 Card</div>}
        </article>
      </div>
    </div>
  );
}
