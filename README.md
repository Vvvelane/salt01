# salt01

NaCl contracts, saltlab research packages, and the read-only Recipe browser.

This repository consumes versioned manifests and published data from
`salt00`; it does not own raw market files or a second CSV catalog.

Use the repository's ARM64 Python 3.12 uv environment:

```bash
uv sync --locked --all-packages
uv run --package recipe pytest
```

