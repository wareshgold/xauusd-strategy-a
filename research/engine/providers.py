"""Provider adapters for raw market data.

This module is strategy-neutral. It maps provider payloads into canonical
Candle objects and preserves provider metadata; it does not infer missing bars
or apply Strategy A geometry.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from .models import Candle


@dataclass(frozen=True)
class ProviderBatch:
    provider: str
    symbol: str
    interval: str
    source_timezone: str
    retrieval_metadata: dict
    candles: tuple[Candle, ...]


def _parse_timestamp(value: str, source_timezone: str) -> datetime:
    """Parse provider datetime and normalize it to UTC.

    A naive provider timestamp is interpreted only with an explicitly supplied
    provider timezone. No local-machine timezone is ever consulted.
    """
    text = value.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        if not source_timezone:
            raise ValueError("naive timestamp requires explicit source_timezone")
        dt = dt.replace(tzinfo=ZoneInfo(source_timezone))
    return dt.astimezone(timezone.utc)


def parse_twelve_data_time_series(payload: dict, *, requested_symbol: str,
                                  requested_interval: str,
                                  source_timezone: str | None = None) -> ProviderBatch:
    """Parse a Twelve Data /time_series JSON response deterministically.

    The adapter accepts the provider's ``meta`` + ``values`` structure. It
    does not perform network I/O and therefore remains deterministic and easy
    to fixture-test.
    """
    if payload.get("status") == "error":
        raise ValueError(payload.get("message", "provider returned an error"))

    meta = payload.get("meta") or {}
    values = payload.get("values")
    if not isinstance(values, list) or not values:
        raise ValueError("provider payload contains no values")

    symbol = str(meta.get("symbol") or requested_symbol)
    interval = str(meta.get("interval") or requested_interval)
    provider_tz = source_timezone or meta.get("timezone")
    if not provider_tz:
        raise ValueError("provider timezone is required for provenance-safe parsing")

    candles: list[Candle] = []
    for item in values:
        try:
            timestamp = _parse_timestamp(str(item["datetime"]), provider_tz)
            o = float(item["open"])
            h = float(item["high"])
            l = float(item["low"])
            c = float(item["close"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("invalid provider OHLC row") from exc
        candles.append(Candle(timestamp, o, h, l, c, symbol=symbol, timeframe=interval))

    # Preserve payload metadata, but never use it as a trading rule.
    retrieval = {
        "provider": "Twelve Data",
        "source_timezone": provider_tz,
        "meta": dict(meta),
        "requested_symbol": requested_symbol,
        "requested_interval": requested_interval,
    }
    return ProviderBatch("Twelve Data", symbol, interval, provider_tz, retrieval, tuple(candles))
