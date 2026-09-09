from datetime import datetime, timedelta, timezone

from .backtest import BacktestEngine, ExecutionPolicy
from .data import aggregate_ohlc, audit_candles, dataset_fingerprint
from .models import Candle, Order, OrderType, Side, Trade
from .metrics import summarize_trades
from .excursions import trade_excursion


def c(ts, o, h, l, cl):
    return Candle(datetime.fromisoformat(ts).replace(tzinfo=timezone.utc), o, h, l, cl)


def test_audit_detects_duplicate_and_gap():
    bars = [c("2026-01-01T00:00:00", 10, 11, 9, 10), c("2026-01-01T00:02:00", 10, 11, 9, 10), c("2026-01-01T00:02:00", 10, 11, 9, 10)]
    audit = audit_candles(bars)
    assert audit["duplicateTimestamps"] == 1
    assert audit["gapCount"] == 1
    assert audit["pass"] is False


def test_m1_to_m5_requires_complete_bucket():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    bars = [Candle(start + timedelta(minutes=i), 100+i, 101+i, 99+i, 100+i) for i in range(6)]
    out = aggregate_ohlc(bars, 5)
    assert len(out) == 1
    assert out[0].open == 100
    assert out[0].close == 104
    assert out[0].high == 105
    assert out[0].low == 99


def test_limit_fill_and_stop_first_conflict():
    bars = [
        c("2026-01-01T00:00:00", 100, 102, 99, 101),
        c("2026-01-01T00:01:00", 101, 105, 95, 102),
    ]
    order = Order("t1", Side.BUY, OrderType.LIMIT, 1, bars[0].timestamp, price=100, stop_loss=95, take_profit=105)
    trades = BacktestEngine(ExecutionPolicy(stop_first_on_conflict=True)).run(bars, [order])
    assert len(trades) == 1
    assert trades[0].entry_price == 100
    assert trades[0].exit_price == 95
    assert trades[0].exit_reason == "STOP"
    assert trades[0].r_multiple == -1


def test_metrics_are_r_based_and_directional():
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    trades = [
        Trade("win", Side.BUY, t0, 100, 1, 99, 102, t0 + timedelta(minutes=2), 102, "TARGET"),
        Trade("loss", Side.SELL, t0, 100, 1, 101, 98, t0 + timedelta(minutes=3), 101, "STOP"),
    ]
    summary = summarize_trades(trades)
    assert summary["tradeCount"] == 2
    assert summary["winRate"] == 0.5
    assert summary["profitFactor"] == 1.0
    assert summary["longTradeCount"] == 1
    assert summary["shortTradeCount"] == 1


def test_dataset_fingerprint_is_order_independent():
    bars = [c("2026-01-01T00:00:00", 1, 2, 0, 1.5), c("2026-01-01T00:01:00", 1.5, 3, 1, 2)]
    a = dataset_fingerprint(bars, provider="test", symbol="XAUUSD", timeframe="1m")
    b = dataset_fingerprint(list(reversed(bars)), provider="test", symbol="XAUUSD", timeframe="1m")
    assert a == b


def test_excursion_reports_directional_mae_mfe():
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    trade = Trade("x", Side.BUY, t0, 100, 1, 98, 104, t0 + timedelta(minutes=2), 104, "TARGET")
    bars = [c("2026-01-01T00:00:00", 100, 102, 99, 101), c("2026-01-01T00:01:00", 101, 105, 97, 103), c("2026-01-01T00:02:00", 103, 104, 102, 104)]
    ex = trade_excursion(trade, bars)
    assert ex["maePrice"] == -3
    assert ex["mfePrice"] == 5
    assert ex["maeR"] == -1.5
    assert ex["mfeR"] == 2.5
