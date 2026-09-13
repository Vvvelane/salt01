export type Product = { id: string; code: string; name: string };
export type Exchange = { id: string; name: string; products: Product[] };
export type Universe = { phase: string; source: string; exchanges: Exchange[] };

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

export type FactorStrategy = {
  strategy_id: string;
  factor_id: string;
  name: string;
  implementation: string;
  frequency: '1min' | 'daily';
  entry_threshold: number;
  exit_threshold: number;
  available_products: string[];
  [key: string]: unknown;
};

export type FactorProduct = {
  product_id: string;
  name: string;
  exchange: string;
  sector: string;
  asset_class: string;
};

export type FactorCatalog = {
  version: string;
  strategies: FactorStrategy[];
  products: FactorProduct[];
};

export type PnlPoint = { date: string; net_pnl: number; cumulative_net_pnl: number };
export type PnlCurve = { product_id: string; points: PnlPoint[] };

export type FactorResults = {
  strategy: FactorStrategy;
  products: FactorProduct[];
  range: { start: string | null; end: string | null };
  curves: PnlCurve[];
  total_curve: PnlCurve;
  annual: Array<{ year: string; net_pnl: number; cumulative_net_pnl: number }>;
  metrics: { net_pnl: number; max_drawdown: number; trades: number; win_rate: number | null };
  trades: Array<Record<string, string | number | null>>;
  trades_returned: number;
  incomplete_ten_year_products: string[];
};
