export type Product = { id: string; code: string; name: string };
export type Exchange = { id: string; name: string; products: Product[] };
export type Universe = { phase: string; source: string; exchanges: Exchange[] };

export type DatabaseDomain = {
  id: string;
  name: string;
  name_en: string;
  file_count: number;
  size_bytes: number;
  hash_registered: number;
  hash_total: number;
  verified_files: number;
  review_files: number;
  coverage_products: number | null;
  coverage_total: number | null;
  available_pairs: number;
  total_pairs: number;
  series_count: number | null;
  integrity: 'unverified' | 'verified' | 'review';
};
export type DatabaseProduct = {
  exchange_id: string;
  exchange_code: string;
  exchange_name: string;
  product_id: string;
  product_code: string;
  product_name: string;
  status: string;
  has_market: boolean;
};
export type DatabaseAvailability = {
  dataset_key: string;
  product_id: string;
  status: string;
  row_count: number;
  series_count: number;
  min_time: string | null;
  max_time: string | null;
  content_revision: string | null;
  schema_version: string | null;
};
export type DatabaseBatch = {
  run_id: string;
  created_at: string | null;
  completed_at: string | null;
  status: string;
  item_count: number;
  actions: Record<string, number>;
  provider: string | null;
  path: string;
};
export type DatabaseOverview = {
  source: string;
  catalog: { revision: string | null; built_at: string | null; schema_version: string | null };
  manifests: { raw: Record<string, string | number | null>; derived: Record<string, string | number | null> };
  metrics: {
    registered_files: number; registered_bytes: number; hash_registered: number; hash_total: number;
    verified_files: number; unverified_files: number; review_files: number; product_count: number; market_series: number;
  };
  domains: DatabaseDomain[];
  products: DatabaseProduct[];
  availability: DatabaseAvailability[];
  quality: { assessed: boolean; events: number; product_summaries: number; status: string };
  recent_batches: DatabaseBatch[];
  read_only: boolean;
};
export type DatabaseFile = {
  kind: string;
  relative_path: string;
  dataset: string;
  manifest_kind: string;
  format: string;
  size_bytes: number;
  mtime_ns: number;
  sha256: string | null;
  row_count: number | null;
  schema_hash: string | null;
  schema_columns: string | null;
  scanned_at: string | null;
  observation: DatabaseObservationResult | null;
};
export type DatabaseFiles = {
  domain: string;
  product_id?: string;
  offset: number;
  limit: number;
  total: number;
  files: DatabaseFile[];
  scope_note: string;
};
export type DatabaseObservationResult = {
  status: string;
  stable?: boolean;
  matches?: boolean;
  expected_sha256?: string;
  observed_sha256?: string;
  expected_size_bytes?: number;
  observed_size_bytes?: number;
  size_matches?: boolean;
  mtime_matches?: boolean;
  checked_at?: string;
  message?: string;
  manifest_kind?: string;
};
export type DatabaseObservation = {
  task_id: string;
  relative_path: string;
  total_bytes: number;
  bytes_read: number;
  status: 'running' | 'complete' | 'cancelled';
  result: DatabaseObservationResult | null;
};

export type Bar = {
  ts: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  volume: number | null;
  amount: number | null;
  open_interest: number | null;
  contract: string | null;
  product_id: string;
};

export type BarsResponse = {
  product: Product;
  contract: string | null;
  freq: '1min' | 'daily';
  rows: Bar[];
  row_count: number;
  returned: number;
  truncated: boolean;
  has_before: boolean;
  has_after: boolean;
};

export type StructureType = 'directional' | 'conditional' | 'shape' | 'directional_conditional';
export type StructureScope = 'single' | 'cross_section' | 'multi_leg';

export type Expression = {
  expression_id: string;
  name: string;
  description: string;
  architecture_ref: string | null;
};

export type Family = {
  family_id: string;
  name: string;
  name_en: string;
  order: number;
  core_mechanism: string | null;
  core_hypothesis: string | null;
  legacy_families: string[];
  relations: Array<{ type: string; target: string; note: string }>;
  expressions: Expression[];
};

export type CardStructure = {
  type: StructureType;
  scope: StructureScope;
  data: string[];
  layer_separable: boolean;
};

export type FactorCard = {
  factor_id: string;
  family: string;
  expression: string;
  legacy_family: string;
  name: string;
  structure: CardStructure;
  tags: string[];
  construction_kind: string | null;
  idea_summary: string | null;
  mathematical_construction: string | null;
  observable_data: string | null;
  temporal_structure: string | null;
  competes_with: string[];
  composed_with: string[];
  economic_failure_modes: string | null;
  source: { document: string; line: number };
};

export type PracticedStrategy = { strategy_id: string; name: string; frequency: string };

export type Registry = {
  schema_version: string;
  generated_by: string;
  framework: {
    structure_types: Record<StructureType, { label: string; definition: string; standalone: boolean }>;
    scopes: Record<StructureScope, string>;
  };
  families: Family[];
  cards: FactorCard[];
  factorlab: Record<string, PracticedStrategy[]>;
};

export type Strategy = {
  strategy_id: string; factor_id: string; name: string; implementation: string; frequency: '1min' | 'daily';
  unit: 'currency' | 'return'; ready: boolean; available_products: string[]; generated_at: string | null;
  config_changed: boolean; execution: Record<string, unknown>; [key: string]: unknown;
};
export type ResearchCatalog = { version: string; strategies: Strategy[]; products: { product_id: string; name: string }[] };
export type Curve = { id: string; points: { date: string; value: number | null }[] };
export type Trade = Record<string, string | number | null>;
export type ResearchResults = {
  strategy: Strategy; curves: Curve[]; total: Curve;
  annual: { year: string; net: number; gross: number; fees: number }[];
  metrics: { net: number; drawdown: number; trades: number; win_rate: number | null; fees: number; average_fee: number | null };
  slippage: Record<string, number>; trades: Trade[];
  diagnostics: { attribution_reconciled?: boolean; attribution_error?: string; rankings?: Trade[]; positions?: Trade[];
    failed_rebalances?: number; pre_main_roll_closes?: number; insufficient_universe_days?: number;
    exit_reasons?: Record<string, number>; incomplete_products?: string[] };
};

export type Replay = { trade: Trade | null; bars: Bar[]; ranking: Trade | null; sampled: boolean };
