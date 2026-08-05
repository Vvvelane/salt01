from pathlib import Path


STATIC = Path(__file__).parents[1] / "static"


def test_three_fixed_routes_and_market_contract():
    app = (STATIC / "js/app.js").read_text(encoding="utf-8")
    market = (STATIC / "js/views/market.js").read_text(encoding="utf-8")
    assert "#/market" in app and "#/data" in app and "#/research" in app
    assert "bid" not in market.lower() or "bid/ask" in market.lower()
    for token in ("asset_id", "start", "end", "Bar Inspector", "symbol change", "close ≠ mid"):
        assert token in market


def test_chart_has_interaction_and_dispose():
    chart = (STATIC / "js/components/chart.js").read_text(encoding="utf-8")
    assert "wheel" in chart and "pointerdown" in chart and "click" in chart
    assert "ResizeObserver" in chart and "dispose" in chart

