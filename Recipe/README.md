# Recipe

Recipe is a local, read-only browser for the product data workbench. It
consumes only the published DuckDB index contract and Parquet paths published
by `salt-data`; it does not scan a data root or open client-provided paths.
The current product scope is Catalog, daily market browsing, and one-trading-day
1min drill-down. The drill-down resolves `v_session_rules` against the official
`v_trading_calendar`, validates single-contract requests with
`v_contract_lifecycle`, and reads physical series only through `v_market_series`.
For the daily main view, Recipe uses the row-level contract identity from the
main 1min series to select the corresponding all-contract daily bars; it does
not use the vendor main-daily file because that file has no contract identity.
Quality computation and quality-result visualization are deliberately out of
scope. Research remains a real empty state until a validated run manifest is
published.

## Development

```bash
uv sync
cp .env.example .env
uvicorn recipe.app:app --app-dir src
```

`SALT_DATA_ROOT` identifies the only approved physical data root. Relative
paths in `v_market_series.storage_locator` are resolved below that root and
validated before DuckDB reads them. All requests use `/api/v2` and require the
DuckDB views in `RECIPE_INDEX_DSN`.
