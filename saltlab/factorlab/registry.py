from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class FactorSpec:
    factor_id: str
    name: str
    family: str
    stage: int
    status: str
    parameters: Dict[str, Any]
    strategy: str
    formula: str
    limitation: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _s(fid: str, name: str, family: str, stage: int, status: str,
       params: Dict[str, Any], strategy: str, formula: str,
       limitation: str = "") -> FactorSpec:
    return FactorSpec(fid, name, family, stage, status, params, strategy, formula, limitation)


def factor_registry() -> Tuple[FactorSpec, ...]:
    # Parameters are the first canonical choices from factor_research.md. All
    # alternatives remain documented in that source and are not selected by
    # holdout performance.
    return (
        _s("FTR001", "time_series_momentum", "trend", 1, "implemented", {"lookback": 60}, "directional", "log(C_t/C_{t-n})"),
        _s("FTR002", "distance_from_moving_average", "trend", 1, "implemented", {"lookback": 60}, "directional", "(C-SMA_n)/(SMA_n*sd(return))"),
        _s("FTR003", "moving_average_spread", "trend", 1, "implemented", {"short": 20, "long": 60}, "directional", "(SMA_s-SMA_l)/SMA_l"),
        _s("FTR004", "donchian_breakout", "trend", 1, "partial", {"lookback": 60}, "directional_signal_only", "close versus prior rolling high/low", "ATR stop/target execution is pending; direction and next-open timing are implemented"),
        _s("FTR006", "regression_slope_tstat", "trend", 1, "implemented", {"lookback": 60}, "directional_hysteresis", "OLS slope t-stat of log price"),
        _s("FTR007", "kaufman_efficiency_ratio", "trend", 1, "implemented", {"lookback": 20}, "directional", "signed net change / path length"),
        _s("FRV001", "short_term_reversal", "reversal", 1, "partial", {"lookback": 3, "z_window": 60}, "reversal_signal_only", "negative prior return", "ATR stop execution is pending"),
        _s("FRV002", "volume_confirmed_reversal", "reversal", 2, "implemented", {"return_window": 1, "volume_window": 20}, "reversal", "negative return times abnormal volume"),
        _s("FRV004", "price_zscore_reversion", "reversal", 1, "partial", {"lookback": 60}, "reversion_signal_only", "negative z-score of log price", "ATR stop execution is pending"),
        _s("FRV005", "rsi_reversion", "reversal", 1, "partial", {"lookback": 14}, "rsi_stateful_signal_only", "Wilder RSI", "ATR stop execution is pending"),
        _s("FVR001", "close_close_volatility", "volatility", 1, "implemented", {"lookback": 20}, "risk_scaler_only", "rolling sample sd of log returns"),
        _s("FVR002", "parkinson_volatility", "volatility", 1, "implemented", {"lookback": 20}, "risk_scaler_only", "sqrt(mean(log(H/L)^2)/(4 log 2))"),
        _s("FVR004", "rogers_satchell_volatility", "volatility", 1, "implemented", {"lookback": 20}, "risk_scaler_only", "Rogers-Satchell estimator"),
        _s("FVR005", "yang_zhang_volatility", "volatility", 1, "implemented", {"lookback": 20}, "risk_scaler_only", "Yang-Zhang estimator"),
        _s("FVR006", "atr_normalized", "volatility", 1, "implemented", {"lookback": 14}, "risk_scaler_only", "Wilder ATR / close"),
        _s("FVO001", "volume_growth", "volume", 2, "implemented", {"lookback": 20}, "analysis_only", "log(V_t / SMA(V)_{t-1})"),
        _s("FVO002", "abnormal_volume", "volume", 2, "implemented", {"ema": 20, "z_window": 60}, "analysis_only", "log volume minus lagged EMA, z-scored"),
        _s("FCM001", "cross_sectional_momentum", "cross_section", 3, "partial", {"lookback": 60, "quantile": 0.2}, "cross_sectional_long_short", "cross-sectional rank of time-series momentum", "fixed major-file universe; PIT membership pending"),
        _s("FCM002", "cross_sectional_reversal", "cross_section", 3, "partial", {"lookback": 1, "quantile": 0.2}, "cross_sectional_long_short", "cross-sectional rank of negative short return", "fixed major-file universe; PIT membership pending"),
        _s("FCS001", "cross_sectional_low_volatility", "cross_section", 3, "partial", {"lookback": 20, "quantile": 0.2}, "cross_sectional_long_short", "negative cross-sectional rank of volatility", "fixed major-file universe; PIT membership pending"),
        _s("FCS004", "relative_momentum", "cross_section", 3, "partial", {"lookback": 60, "quantile": 0.2}, "cross_sectional_long_short", "instrument momentum minus equal-weight market momentum", "fixed major-file universe; PIT membership pending"),
        _s("FCS005", "cross_sectional_skewness", "cross_section", 3, "partial", {"lookback": 60, "quantile": 0.2}, "cross_sectional_long_short", "rank of rolling return skewness", "fixed major-file universe; PIT membership pending"),
        _s("FOT002", "realized_skewness_proxy", "other", 1, "partial", {"lookback": 20}, "analysis_only", "daily OHLC signed range variance proxy", "daily OHLC cannot reproduce intraday realized semivariance"),
        _s("FSE001", "same_month_seasonality", "seasonality", 7, "partial", {"min_years": 5}, "directional", "expanding prior-year same-calendar-month return mean", "requires five prior observations; major continuous history is unverified"),
        _s("FVR007", "intraday_realized_volatility", "volatility", 8, "pending", {"minutes": (5, 15), "days": (5, 20)}, "unsupported", "intraday realized volatility", "session and trading-date semantics pending"),
        _s("FVO005", "open_interest_change", "open_interest", 4, "pending", {"lookback": 20}, "unsupported", "OI change", "position column semantics are not confirmed"),
        _s("FVO007", "price_open_interest_quadrant", "open_interest", 4, "pending", {}, "unsupported", "price/OI quadrant", "position column semantics are not confirmed"),
        _s("FCA001", "term_structure_carry", "term_structure", 5, "pending", {"near": 1, "far": 2}, "unsupported", "annualized futures curve carry", "expiry, contract month and roll rule pending"),
        _s("FCA005", "calendar_spread_momentum", "term_structure", 5, "pending", {"lookback": 60}, "unsupported", "fixed-leg spread momentum", "contract metadata and synchronized legs pending"),
        _s("FRL002", "pairs_mean_reversion", "relative_value", 6, "pending", {"formation": 120, "z_window": 60}, "unsupported", "rolling Engle-Granger spread", "economic pair whitelist and leg metadata pending"),
        _s("FID001", "open_first_30m", "intraday", 8, "pending", {"minutes": 30}, "unsupported", "first/last session-window return", "session semantics pending"),
        _s("FID003", "open_to_last_30m", "intraday", 8, "pending", {"minutes": 30}, "unsupported", "open to last 30-minute return", "session semantics pending"),
    )
