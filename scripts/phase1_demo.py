"""Small real-data + JSON reader smoke path. Does not construct a strategy.

Run this script from the workspace environment after ``uv sync``.  The
workspace installs ``saltcore`` and ``salt-nacl-registry`` as editable packages;
the script deliberately does not modify ``sys.path``.
"""

from nacl_registry import load_registry

from saltcore import read_bars


def main():
    bars = read_bars(product="AU", start="2026-08-03", end="2026-08-05")
    print(bars.meta.to_string(index=False))
    print(bars.one().head(3).to_string(index=False))
    registry = load_registry()
    card = registry.get("FTR001")
    print(
        f"Registry: {len(registry.list())} cards; example: {card['factor_id']} {card['name']}"
    )
    graph = registry.graph(["FTR001", "FRV001"])
    print(f"Graph subset: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
    print("Factorlab: draft scaffold only; no strategy or backtest was executed.")


if __name__ == "__main__":
    main()
