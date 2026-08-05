# Recipe

Recipe is a local, read-only browser for market bars, data semantics, and
registered research outputs. The implementation is deliberately limited to
the three views defined in `../recipe.md`.

## Development

```bash
python -m pip install -e '.[test]'
RECIPE_MARKET_ROOT=/path/to/价格行为 python -m recipe.catalog refresh
uvicorn recipe.app:app --app-dir src
```

The catalog is a rebuildable metadata cache under `var/catalog.sqlite`.
Market and research roots are never returned by the API.
