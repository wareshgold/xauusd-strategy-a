"""Source-neutral research engine primitives for SP2L.

This package intentionally contains no Strategy A geometry decisions.
"""

from .models import Candle, Order, Fill, Trade
from .data import aggregate_ohlc, audit_candles, dataset_fingerprint
from .timeframes import aggregate_m1_to_m5
from .dataset_package import DatasetReadiness, SplitSummary, load_readiness
from .baselines import BaselineResult, flat_baseline, price_baseline
from .backtest import BacktestEngine
from .metrics import summarize_trades
from .excursions import trade_excursion

__all__ = [
    "Candle", "Order", "Fill", "Trade",
    "aggregate_ohlc", "aggregate_m1_to_m5", "audit_candles", "dataset_fingerprint",
    "DatasetReadiness", "SplitSummary", "load_readiness",
    "BaselineResult", "flat_baseline", "price_baseline",
    "BacktestEngine", "summarize_trades", "trade_excursion",
]
