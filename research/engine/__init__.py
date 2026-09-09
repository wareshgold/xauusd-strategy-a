"""Source-neutral research engine primitives for SP2L.

This package intentionally contains no Strategy A geometry decisions.
"""

from .models import Candle, Order, Fill, Trade
from .data import aggregate_ohlc, audit_candles, dataset_fingerprint
from .backtest import BacktestEngine
from .metrics import summarize_trades

__all__ = [
    "Candle", "Order", "Fill", "Trade",
    "aggregate_ohlc", "audit_candles", "dataset_fingerprint",
    "BacktestEngine", "summarize_trades",
]
