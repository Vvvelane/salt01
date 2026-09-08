export type ApiEnvelope<T> = {
  data: T;
  meta: {
    catalog_revision?: string | null;
    catalog_schema_version?: string | null;
    index_contract_ready?: boolean;
  };
  warnings: { code: string; message: string }[];
  status: string;
};

export type Exchange = {
  exchange_id: string;
  exchange_code: string;
  exchange_name: string;
};

export type Product = {
  product_id: string;
  exchange_id: string;
  exchange_name?: string;
  product_code: string;
  product_name: string;
  status: string;
};

export type DatasetAvailability = {
  dataset_key: string;
  status: string;
  row_count: number;
  series_count: number;
  min_time: string | null;
  max_time: string | null;
};

export type Bar = {
  timestamp: string;
  raw_datetime?: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  volume: number | null;
  amount?: number | null;
  open_interest?: number | null;
  contract_code?: string | null;
  source_symbol?: string | null;
  timestamp_semantics?: string;
  trading_date?: string | null;
  session_id?: string | null;
  is_placeholder?: boolean;
  selection_source?: string | null;
};

export type DailyPayload = {
  bars: Bar[];
  truncated: boolean;
  semantic_status: Record<string, string>;
  selection_source?: string;
  rolls?: { timestamp: string | null; old_contract: string; new_contract: string }[];
  warnings?: { code: string; message: string }[];
};

export type IntradayPayload = {
  bars: Bar[];
  truncated: boolean;
  trading_date: string;
  session_windows: { session_id: string; start: string; end: string }[];
  semantic_status: Record<string, string>;
  warnings?: { code: string; message: string }[];
};

export type Field = {
  field_name?: string;
  raw_field?: string;
  display_name?: string;
  semantic_status?: string;
  economic_identity?: string;
  aggregation_note?: string;
  warning?: string;
};
