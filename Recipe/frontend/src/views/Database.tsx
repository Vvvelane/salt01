import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type MouseEvent,
} from 'react';
import { api, STATIC_MODE } from '../api';
import { Keeper } from '../components/idea-room/Keeper';
import { useLanguage } from '../i18n';
import type {
  DatabaseAvailability,
  DatabaseDomain,
  DatabaseFile,
  DatabaseObservation,
  DatabaseOverview,
} from '../types';
import { MarketInspector } from './Market';
import '../components/idea-room/idea-room.css';
import './database.css';

type DetailTab = 'overview' | 'files';
type Detail = { domain: string; tab: DetailTab };

const MARKET_DATASETS = [
  { id: 'market.main.daily', zh: '主连 · 日线', en: 'Main · Daily' },
  { id: 'market.main.1min', zh: '主连 · 1min', en: 'Main · 1min' },
  { id: 'market.contract.daily', zh: '合约 · 日线', en: 'Contracts · Daily' },
  { id: 'market.contract.1min', zh: '合约 · 1min', en: 'Contracts · 1min' },
];

const number = (value: number, language: string) =>
  new Intl.NumberFormat(language === 'en' ? 'en-US' : 'zh-CN').format(value);
const bytes = (value: number, language: string) =>
  `${new Intl.NumberFormat(language === 'en' ? 'en-US' : 'zh-CN', { maximumFractionDigits: 2 }).format(value / 1_000_000_000)} GB`;
const shortHash = (value: string | null) =>
  value ? `${value.slice(0, 10)} ··· ${value.slice(-8)}` : '—';

function statusLabel(
  row: DatabaseAvailability | undefined,
  t: (text: string, english?: string) => string,
) {
  if (!row) return t('未知', 'Unknown');
  if (row.status === 'available') return t('已登记', 'Recorded');
  if (row.status === 'not_recorded') return t('无登记', 'Not recorded');
  return row.status;
}

function DatabaseAlert({
  snapshot,
  refreshing,
  onRefresh,
  onManifest,
}: {
  snapshot: DatabaseOverview;
  refreshing: boolean;
  onRefresh: () => void;
  onManifest: () => void;
}) {
  const { t, language } = useLanguage();
  const metrics = snapshot.metrics;
  return (
    <details className="research-alert db-release-alert">
      <summary>
        <span>!</span>
        <div>
          <b>{t('数据版本与最近变更', 'Data version & recent changes')}</b>
          <small>SALT-DATA · READ-ONLY</small>
        </div>
        <i>⌄</i>
      </summary>
      <div className="alert-body">
        <section>
          <h3>{t('当前发布', 'Current publication')}</h3>
          <p>{snapshot.catalog.revision ?? t('Catalog 版本未记录', 'Catalog revision not recorded')}</p>
          <p>{t('构建时间', 'Built')} · {snapshot.catalog.built_at ?? '—'}</p>
        </section>
        <section>
          <h3>{t('完整性边界', 'Integrity boundary')}</h3>
          <p>{t(
            `${number(metrics.hash_registered, language)} / ${number(metrics.hash_total, language)} 个文件具有 Manifest SHA-256 基线；${number(metrics.verified_files, language)} 个文件已在 Recipe 中重新读取核验。`,
            `${number(metrics.hash_registered, language)} / ${number(metrics.hash_total, language)} files have a manifest SHA-256 baseline; ${number(metrics.verified_files, language)} files have been re-read and verified by Recipe.`,
          )}</p>
          <p>{t('Recipe 只读 salt-data；核验记录保存在 Recipe 自己的本地缓存。', 'Recipe reads salt-data only; observations are stored in Recipe’s own local cache.')}</p>
        </section>
        <section>
          <h3>{t('最近发布与变更', 'Recent publications')}</h3>
          <div className="db-alert-runs">
            {snapshot.recent_batches.slice(0, 6).map((batch) => (
              <div key={batch.run_id}>
                <span className={`db-batch-status status-${batch.status.toLowerCase()}`}>{batch.status}</span>
                <b>{batch.run_id}</b>
                <small>{number(batch.item_count, language)} {t('个项目', 'items')} · {Object.entries(batch.actions).map(([name, count]) => `${name} ${count}`).join(' · ')}</small>
              </div>
            ))}
            {!snapshot.recent_batches.length && <p>{t('没有可展示的发布记录。', 'No publication records are available.')}</p>}
          </div>
        </section>
        <div className="db-alert-actions">
          <button onClick={onManifest}>{t('查看清单与核验依据', 'View manifest evidence')} ↗</button>
          <button onClick={onRefresh} disabled={refreshing}>{refreshing ? t('读取中…', 'Refreshing…') : t('刷新观察', 'Refresh view')} ↻</button>
        </div>
      </div>
    </details>
  );
}

function DatabaseOrbit({
  snapshot,
  onSelect,
  refreshing,
  onRefresh,
  onManifest,
}: {
  snapshot: DatabaseOverview;
  onSelect: (domain: string) => void;
  refreshing: boolean;
  onRefresh: () => void;
  onManifest: () => void;
}) {
  const { t, language } = useLanguage();
  const [running, setRunning] = useState(() =>
    typeof window === 'undefined' || !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  );
  // Half a slot of offset: at rest no capsule parks directly in front of the keeper.
  const state = useRef({ angle: Math.PI / Math.max(1, snapshot.domains.length), speed: 0.16, running, drag: false, x: 0, last: 0, start: 0, moved: false });
  const pipes = useRef<(HTMLButtonElement | null)[]>([]);
  const space = useRef<HTMLDivElement>(null);
  state.current.running = running;

  useEffect(() => {
    let frame = 0;
    let last = performance.now();
    const animate = (now: number) => {
      const current = state.current;
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      if (current.running && !current.drag) {
        current.angle += current.speed * dt;
        current.speed += (0.16 - current.speed) * Math.min(1, dt * 0.12);
      }
      const radius = Math.min(420, (space.current?.clientWidth ?? 1100) * 0.32);
      // Follow the drawn ring: the front arc passes below the keeper's torso instead of across it.
      const lift = (space.current?.clientHeight ?? 520) * 0.3;
      pipes.current.forEach((pipe, index) => {
        if (!pipe) return;
        const angle = current.angle + index / snapshot.domains.length * Math.PI * 2;
        const depth = Math.cos(angle);
        const scale = 0.68 + (depth + 1) * 0.2;
        pipe.style.transform = `translate(-50%, -50%) translate(${Math.sin(angle) * radius}px, ${depth * lift}px) scale(${scale}) rotateY(${-Math.sin(angle) * 23}deg)`;
        pipe.style.zIndex = String(Math.round((depth + 1) * 100));
        pipe.style.opacity = '1';
      });
      frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [snapshot.domains]);

  return (
    <section className="db-collection">
      <div className="db-collection-top">
        <DatabaseAlert snapshot={snapshot} refreshing={refreshing} onRefresh={onRefresh} onManifest={onManifest}/>
        <span className="room-eyebrow">salt-data <i/> {t('已发布数据域', 'PUBLISHED DOMAINS')}</span>
      </div>
      <header className="db-collection-title">
        <span className="kicker">SALT-DATA / VAULT CAPSULES</span>
        <h1>{t('数据封存舱', 'Database Management')}</h1>
        <p>{snapshot.domains.length} {t('个数据域', 'data domains')} · {number(snapshot.metrics.registered_files, language)} {t('个登记文件', 'registered files')}</p>
      </header>
      <div
        className="db-pipeline-orbit"
        ref={space}
        onPointerDown={(event) => {
          if (event.button !== 0) return;
          const current = state.current;
          current.drag = true;
          current.start = event.clientX;
          current.x = event.clientX;
          current.last = performance.now();
          current.moved = false;
        }}
        onPointerMove={(event) => {
          const current = state.current;
          if (!current.drag) return;
          if (Math.abs(event.clientX - current.start) > 5) {
            current.moved = true;
            event.currentTarget.setPointerCapture(event.pointerId);
          }
          const now = performance.now();
          const delta = event.clientX - current.x;
          current.angle += delta * 0.008;
          current.speed = Math.max(-4, Math.min(4, delta * 0.008 / Math.max(0.008, (now - current.last) / 1000)));
          current.x = event.clientX;
          current.last = now;
        }}
        onPointerUp={() => {
          const current = state.current;
          current.drag = false;
          if (current.moved) setRunning(true);
        }}
        onPointerCancel={() => { state.current.drag = false; }}
      >
        <div className="db-orbit-ring"/>
        <div className="db-orbit-ring secondary"/>
        <div className="db-orbit-core">
          <Keeper network={false} onToggle={() => setRunning(!running)} label={t('控制封存舱轨道', 'Control the vault orbit')}/>
          <div className="db-vault-count"><span>SALT-DATA</span><b>{number(snapshot.metrics.registered_files, language)}</b><small>FILES IN MANIFEST</small></div>
        </div>
        {snapshot.domains.map((domain, index) => (
          <button
            className={`db-pipe${domain.id === 'market' ? ' is-live' : ' is-dim'}`}
            key={domain.id}
            ref={(node) => { pipes.current[index] = node; }}
            onClick={() => { if (!state.current.moved) onSelect(domain.id); }}
            aria-label={`${t(domain.name, domain.name_en)} · ${number(domain.file_count, language)} ${t('个文件', 'files')}`}
            style={{
              '--fill': `${32 + (index * 17) % 53}%`,
              '--liquid': domain.id === 'market' ? '#79be66' : ['#5f9c8f', '#6f8f9c', '#8a9a7c', '#62909a'][index % 4],
            } as CSSProperties}
          >
            <span className="db-pipe-shell">
              <i className="db-pipe-cap"/><i className="db-pipe-liquid"><i/><i/><i/></i><i className="db-pipe-glass"/>
              <span className="db-pipe-index">{String(index + 1).padStart(2, '0')} · {domain.id.toUpperCase()}</span>
              <b>{t(domain.name, domain.name_en)}</b>
              <strong>{number(domain.file_count, language)}</strong>
              <small>{domain.series_count != null ? `${number(domain.series_count, language)} ${t('条序列', 'series')}` : `${bytes(domain.size_bytes, language)} · SHA ${number(domain.hash_registered, language)}`}</small>
              <em>{domain.id === 'market' ? t('已接入 · 解封', 'ONLINE · UNSEALED') : t('密封存储', 'CLASSIFIED · SEALED')}</em>
            </span>
          </button>
        ))}
      </div>
      <div className="db-orbit-controls">
        <button onClick={() => { if (!running) state.current.speed = 0.16; setRunning(!running); }}>{running ? 'Ⅱ' : '▶'} {running ? t('停转', 'Stop') : t('旋转', 'Spin')}</button>
        <button onClick={() => { state.current.speed = Math.min(4, Math.abs(state.current.speed) + 1); setRunning(true); }}>↻ {t('加速', 'Accelerate')}</button>
      </div>
    </section>
  );
}

function MarketCoverage({ snapshot, onSelect }: { snapshot: DatabaseOverview; onSelect: (productId: string) => void }) {
  const { t, language } = useLanguage();
  const lookup = useMemo(() => new Map(snapshot.availability.map((row) => [`${row.product_id}|${row.dataset_key}`, row])), [snapshot.availability]);
  const exchanges = useMemo(() => [...new Set(snapshot.products.map((product) => product.exchange_id))], [snapshot.products]);
  return (
    <section className="db-matrix panel">
      <header className="db-section-heading"><div><span className="kicker">PRODUCT × MARKET DATA</span><h2>{t('品种覆盖', 'Market coverage')}</h2></div><span className="db-section-meta">{number(snapshot.products.length, language)} {t('个品种', 'products')} · {MARKET_DATASETS.length} {t('类行情', 'market datasets')}</span></header>
      <p className="db-note">{t('点击亮起的数据点，直接在下方打开该品种行情。暗点表示 Catalog 未登记。', 'Click a lit data point to open that product in the market viewer below. Dim points are not recorded in the Catalog.')}</p>
      <div className="db-matrix-scroll"><table><thead><tr><th>{t('交易所 / 品种', 'Exchange / Product')}</th>{MARKET_DATASETS.map((dataset) => <th key={dataset.id}>{t(dataset.zh, dataset.en)}</th>)}</tr></thead><tbody>{exchanges.map((exchange) => <MarketExchangeRows key={exchange} exchange={exchange} products={snapshot.products.filter((product) => product.exchange_id === exchange)} lookup={lookup} language={language} onSelect={onSelect} t={t}/>)}</tbody></table></div>
    </section>
  );
}

function MarketExchangeRows({ exchange, products, lookup, language, onSelect, t }: {
  exchange: string;
  products: DatabaseOverview['products'];
  lookup: Map<string, DatabaseAvailability>;
  language: string;
  onSelect: (productId: string) => void;
  t: (text: string, english?: string) => string;
}) {
  return <>
    <tr className="db-exchange-row"><th colSpan={MARKET_DATASETS.length + 1}>{exchange} <span>{language === 'en' ? exchange : products[0]?.exchange_name}</span></th></tr>
    {products.map((product) => <tr key={product.product_id}>
      <th className="db-product-cell"><span>{product.product_code}</span><small>{language === 'en' ? product.status : product.product_name}</small>{product.status === 'retired' && <i>{t('已退市', 'Retired')}</i>}</th>
      {MARKET_DATASETS.map((dataset) => {
        const row = lookup.get(`${product.product_id}|${dataset.id}`);
        const available = row?.status === 'available';
        const state = available ? 'available' : row?.status === 'not_recorded' ? 'empty' : 'unknown';
        const title = `${product.product_id} · ${t(dataset.zh, dataset.en)} · ${statusLabel(row, t)}${row?.min_time ? ` · ${row.min_time} → ${row.max_time ?? '—'}` : ''}`;
        return <td key={dataset.id}><button className={`db-matrix-cell ${state}`} title={title} aria-label={title} disabled={!available} onClick={() => onSelect(product.product_id)}><i/>{available && <span>{number(row?.row_count ?? 0, language)}</span>}</button></td>;
      })}
    </tr>)}
  </>;
}

function FileRows({ files, language, task, onVerify, onCancel, t }: {
  files: DatabaseFile[];
  language: string;
  task: DatabaseObservation | null;
  onVerify: (file: DatabaseFile) => void;
  onCancel: () => void;
  t: (text: string, english?: string) => string;
}) {
  const copy = async (value: string) => { try { await navigator.clipboard.writeText(value); } catch { /* Clipboard access may be unavailable. */ } };
  return <div className="db-file-list">{files.map((file) => {
    const active = task?.relative_path === file.relative_path && task.status === 'running';
    const completed = task?.relative_path === file.relative_path && task.status === 'complete' ? task.result : null;
    const evidence = completed ?? file.observation;
    const progress = active && task.total_bytes ? Math.min(100, task.bytes_read / task.total_bytes * 100) : 0;
    const integrity = evidence?.status;
    return <article className={`db-file-row${integrity ? ` check-${integrity}` : ''}`} key={`${file.kind}/${file.relative_path}`}>
      <div className="db-file-main"><div className="db-file-path"><span className="db-file-kind">{file.kind === 'raw' ? t('原始', 'RAW') : t('派生', 'DERIVED')} · {file.format.toUpperCase()}</span><code title={file.relative_path}>{file.relative_path}</code></div>
        <div className="db-file-facts"><span>{t('大小', 'Size')} <b>{bytes(file.size_bytes, language)}</b></span>{file.row_count != null && <span>{t('行数', 'Rows')} <b>{number(file.row_count, language)}</b></span>}<span>{t('基线 SHA-256', 'Manifest SHA-256')} <code title={file.sha256 ?? ''}>{shortHash(file.sha256)}</code><button className="db-copy" onClick={() => file.sha256 && copy(file.sha256)} aria-label={t('复制完整 SHA-256', 'Copy full SHA-256')}>⧉</button></span></div>
        {active && <div className="db-progress"><span style={{ width: `${progress}%` }}/><small>{number(task.bytes_read, language)} / {number(task.total_bytes, language)} bytes</small></div>}
        {evidence && <p className={`db-check-result ${integrity ?? ''}`}><b>{integrity === 'verified' ? t('内容与基线一致', 'Content matches manifest') : integrity === 'mismatch' ? t('内容与基线不一致', 'Content differs from manifest') : integrity === 'missing' ? t('当前文件缺失', 'Current file is missing') : integrity === 'updating' ? t('检查期间文件或清单发生变化', 'File or manifest changed during check') : integrity === 'unreadable' ? t('文件无法读取', 'File could not be read') : integrity}</b>{evidence.checked_at && <span>{new Date(evidence.checked_at).toLocaleString(language === 'en' ? 'en-US' : 'zh-CN')} · {t('实测', 'observed')} {shortHash(evidence.observed_sha256 ?? null)}</span>}{evidence.message && <span>{evidence.message}</span>}</p>}
      </div>
      <div className="db-file-actions">{active ? <button className="quiet-button" onClick={onCancel}>{t('取消', 'Cancel')}</button> : <button className="db-verify-button" disabled={!file.sha256 || Boolean(task && task.status === 'running')} onClick={() => onVerify(file)}>{t('核验此文件', 'Verify file')}</button>}</div>
    </article>;
  })}</div>;
}

export function Database({ initialSnapshot }: { initialSnapshot?: DatabaseOverview } = {}) {
  const { t, language } = useLanguage();
  const [snapshot, setSnapshot] = useState<DatabaseOverview | undefined>(initialSnapshot);
  const [loading, setLoading] = useState(!initialSnapshot);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [detail, setDetail] = useState<Detail | null>(null);
  const [marketProductId, setMarketProductId] = useState<string>();
  const [offset, setOffset] = useState(0);
  const [fileData, setFileData] = useState<{ total: number; files: DatabaseFile[]; scope_note: string }>();
  const [filesLoading, setFilesLoading] = useState(false);
  const [fileError, setFileError] = useState('');
  const [task, setTask] = useState<DatabaseObservation | null>(null);
  const marketTarget = useRef<HTMLElement>(null);

  const refresh = useCallback(async (quiet = false) => {
    if (quiet) setRefreshing(true); else setLoading(true);
    setError('');
    try { setSnapshot(await api.databaseOverview()); }
    catch (reason) { setError(String(reason)); }
    finally { setLoading(false); setRefreshing(false); }
  }, []);
  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => {
    if (!detail || detail.tab !== 'files' || STATIC_MODE) return;
    const controller = new AbortController(); setFilesLoading(true); setFileError('');
    api.databaseFiles(detail.domain, offset, controller.signal)
      .then((data) => setFileData({ total: data.total, files: data.files, scope_note: data.scope_note }))
      .catch((reason) => { if (!controller.signal.aborted) setFileError(String(reason)); })
      .finally(() => { if (!controller.signal.aborted) setFilesLoading(false); });
    return () => controller.abort();
  }, [detail?.domain, detail?.tab, offset]);
  useEffect(() => {
    if (task?.status === 'complete') void refresh(true);
    if (!task || task.status !== 'running') return;
    const controller = new AbortController();
    const timer = window.setTimeout(() => { api.databaseObservation(task.task_id, controller.signal).then(setTask).catch((reason) => setFileError(String(reason))); }, 500);
    return () => { controller.abort(); window.clearTimeout(timer); };
  }, [task?.task_id, task?.status, task?.bytes_read, refresh]);
  useEffect(() => {
    if (!detail) return;
    const onKey = (event: KeyboardEvent) => { if (event.key === 'Escape') { event.stopPropagation(); setDetail(null); } };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [detail]);

  const open = (domain: string, tab: DetailTab = 'overview') => {
    setOffset(0); setFileData(undefined);
    if (domain === 'market') setMarketProductId(undefined);
    setDetail({ domain, tab });
  };
  const setTab = (tab: DetailTab) => { setOffset(0); setFileData(undefined); setDetail((current) => current ? { ...current, tab } : current); };
  const selectMarketProduct = (productId: string) => {
    setMarketProductId(productId);
    window.setTimeout(() => marketTarget.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 0);
  };
  const verify = async (file: DatabaseFile) => {
    setFileError(''); setTask(null);
    try { setTask(await api.startDatabaseObservation(file.relative_path)); }
    catch (reason) { setFileError(String(reason)); }
  };
  const cancel = async () => {
    if (!task) return;
    try { setTask(await api.cancelDatabaseObservation(task.task_id)); }
    catch (reason) { setFileError(String(reason)); }
  };

  if (loading && !snapshot) return <div className="room-loading">{t('正在读取 salt-data Catalog…', 'Reading salt-data Catalog…')}</div>;
  if (error && !snapshot) return <div className="workspace"><div className="error-banner">{error}</div><button className="quiet-button" onClick={() => void refresh()}>{t('重试', 'Retry')}</button></div>;
  if (!snapshot) return null;

  const metrics = snapshot.metrics;
  const manifestDetail = detail?.domain === 'manifest';
  const marketDetail = detail?.domain === 'market';
  const currentDomain: DatabaseDomain | undefined = snapshot.domains.find((domain) => domain.id === detail?.domain);
  const hideModal = (event: MouseEvent<HTMLDivElement>) => { if (event.target === event.currentTarget) setDetail(null); };

  return <div className="database-page">
    {error && <div className="error-banner db-floating-error">{error}</div>}
    <DatabaseOrbit snapshot={snapshot} onSelect={(domain) => open(domain)} refreshing={refreshing} onRefresh={() => void refresh(true)} onManifest={() => open('manifest')}/>

    {detail && <div className="db-modal-backdrop" role="presentation" onMouseDown={hideModal}><section className={`db-detail-modal${marketDetail ? ' is-market' : ''}`} role="dialog" aria-modal="true" aria-label={manifestDetail ? t('清单与索引', 'Manifest and index') : t(currentDomain?.name, currentDomain?.name_en)}>
      <header className="db-detail-header"><div><button className="quiet-button" onClick={() => setDetail(null)}>← {t('数据封存舱', 'Data vault')}</button><span className="kicker">{manifestDetail ? 'MANIFEST / CATALOG' : `${currentDomain?.id.toUpperCase()} / DATA CAPSULE`}</span><h2>{manifestDetail ? t('清单与索引', 'Manifest & index') : t(currentDomain?.name, currentDomain?.name_en)}</h2></div><button className="db-close" aria-label={t('关闭', 'Close')} onClick={() => setDetail(null)}>×</button></header>
      {!manifestDetail && !marketDetail && <nav className="db-detail-tabs">{(STATIC_MODE ? ['overview'] as DetailTab[] : ['overview', 'files'] as DetailTab[]).map((tab) => <button className={detail.tab === tab ? 'active' : ''} key={tab} onClick={() => setTab(tab)}>{tab === 'overview' ? t('管线概览', 'Pipeline overview') : t('文件与指纹', 'Files & hashes')}</button>)}</nav>}
      <div className="db-detail-scroll">
        {manifestDetail && <div className="db-manifest-detail"><p className="db-lead">{t('本页面从 salt-data 当前 Manifest 与 Catalog 读取状态。已登记的 SHA-256 是比较基线；只有逐文件读取并重新计算后，才显示内容一致。', 'This page reads the current salt-data manifests and Catalog. A registered SHA-256 is a comparison baseline; content is marked as matching only after the file has been read and rehashed.')}</p><div className="db-detail-stat-grid"><div><small>Catalog revision</small><b>{snapshot.catalog.revision ?? '—'}</b></div><div><small>Catalog schema</small><b>{snapshot.catalog.schema_version ?? '—'}</b></div><div><small>{t('原始 Manifest 最近扫描', 'Raw manifest last scan')}</small><b>{String(snapshot.manifests.raw.latest_scanned_at ?? '—')}</b></div><div><small>{t('派生 Manifest 最近扫描', 'Derived manifest last scan')}</small><b>{String(snapshot.manifests.derived.latest_scanned_at ?? '—')}</b></div><div><small>{t('登记 SHA-256', 'Registered SHA-256')}</small><b>{number(metrics.hash_registered, language)} / {number(metrics.hash_total, language)}</b></div><div><small>{t('当前内容核验', 'Current content checks')}</small><b>{number(metrics.verified_files, language)} {t('通过', 'verified')} · {number(metrics.review_files, language)} {t('复核', 'review')}</b></div></div><h3>{t('观察边界', 'Observation boundary')}</h3><p>{t('检查只读取文件并比较当前 Manifest 中的完整 SHA-256。检查期间若文件或 Manifest 变化，结果标记为更新中；Recipe 不会修改、修复或重写 salt-data。', 'Checks read files and compare their complete SHA-256 against the current manifest. Changes during a check are marked as updating. Recipe does not write, repair or rewrite salt-data.')}</p></div>}

        {marketDetail && <div className="db-market-domain"><MarketCoverage snapshot={snapshot} onSelect={selectMarketProduct}/><section className="db-market-target" ref={marketTarget}><header><span className="kicker">MARKET INSPECTOR</span><h2>{t('行情', 'Market')}</h2></header>{STATIC_MODE ? <p className="db-note">{t('分钟级行情查询仅在本地环境提供，公开演示只展示上方的品种覆盖矩阵。', 'Minute-level market lookup is only available in the local environment; the public demo shows the coverage matrix above only.')}</p> : <MarketInspector key={marketProductId ?? 'market-default'} initialProductId={marketProductId}/>}</section></div>}

        {!manifestDetail && !marketDetail && detail.tab === 'overview' && currentDomain && <div className="db-domain-overview"><p className="db-lead">{t('该管线按当前 Manifest 文件清单显示。点击“文件与指纹”可以查看具体路径、行数和 SHA-256，并按需重新读取核验。', 'This pipeline is summarized from the current manifest. Open Files & hashes to inspect paths, row counts and SHA-256 values, and optionally re-read a file for verification.')}</p><div className="db-detail-stat-grid"><div><small>{t('登记文件', 'Registered files')}</small><b>{number(currentDomain.file_count, language)}</b></div><div><small>{t('登记规模', 'Registered size')}</small><b>{bytes(currentDomain.size_bytes, language)}</b></div><div><small>{t('有 SHA-256 基线', 'Files with SHA-256')}</small><b>{number(currentDomain.hash_registered, language)} / {number(currentDomain.hash_total, language)}</b></div><div><small>{t('已核验内容', 'Content verified')}</small><b>{number(currentDomain.verified_files, language)}</b></div>{currentDomain.series_count != null && <div><small>{t('逻辑序列', 'Logical series')}</small><b>{number(currentDomain.series_count, language)}</b></div>}{currentDomain.coverage_products != null && <div><small>{t('覆盖品种', 'Covered products')}</small><b>{number(currentDomain.coverage_products, language)} / {number(currentDomain.coverage_total ?? 0, language)}</b></div>}</div><div className="db-state-callout"><span className={currentDomain.review_files ? 'review' : ''}/><div><b>{currentDomain.review_files ? t('存在需要复核的内容', 'Content needs review') : currentDomain.verified_files ? t('已有部分内容核验', 'Some content has been verified') : t('尚未执行内容核验', 'Content has not been verified')}</b><small>{t('Manifest hash 是比较基线，不自动代表当前磁盘文件已经通过。', 'A manifest hash is a comparison baseline; it does not automatically prove the current disk file passed.')}</small></div></div>{!STATIC_MODE && <button className="db-inline-action" onClick={() => setTab('files')}>{t('查看文件与内容指纹', 'Inspect files and content hashes')} ↗</button>}</div>}

        {!manifestDetail && !marketDetail && !STATIC_MODE && detail.tab === 'files' && <div className="db-files-detail"><p className="db-note">{fileData?.scope_note ?? t('正在读取当前 Manifest 中对应的数据域…', 'Reading this domain from the current manifests…')}</p>{fileError && <div className="error-banner">{fileError}</div>}{filesLoading && <p className="db-note">{t('读取文件索引…', 'Loading file index…')}</p>}{fileData && <><FileRows files={fileData.files} language={language} task={task} onVerify={(file) => void verify(file)} onCancel={() => void cancel()} t={t}/><footer className="db-file-pagination"><span>{number(fileData.total ? offset + 1 : 0, language)}–{number(Math.min(offset + fileData.files.length, fileData.total), language)} / {number(fileData.total, language)}</span><div><button disabled={!offset} onClick={() => { setOffset(Math.max(0, offset - 60)); setFileData(undefined); }}>←</button><button disabled={offset + 60 >= fileData.total} onClick={() => { setOffset(offset + 60); setFileData(undefined); }}>→</button></div></footer></>}</div>}
      </div>
    </section></div>}
  </div>;
}
