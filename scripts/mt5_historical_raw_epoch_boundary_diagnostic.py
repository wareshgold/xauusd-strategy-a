#!/usr/bin/env python3
import json
from datetime import datetime, timezone
import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1

def parse_utc(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).replace(second=0, microsecond=0)

start = parse_utc("2026-09-10T10:00:00Z")
end = parse_utc("2026-09-10T10:04:00Z")

if not mt5.initialize():
    raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

try:
    rates = mt5.copy_rates_range(SYMBOL, TIMEFRAME, start, end)
    if rates is None:
        raise SystemExit(f"copy_rates_range failed: {mt5.last_error()}")

    start_epoch = int(start.timestamp())
    end_epoch = int(end.timestamp())
    raw = [int(r["time"]) for r in rates]

    result = {
        "query_start_epoch": start_epoch,
        "query_end_epoch": end_epoch,
        "returned_count": len(raw),
        "raw_epochs": raw,
        "raw_minus_query_start": [x - start_epoch for x in raw],
        "raw_minus_query_end": [x - end_epoch for x in raw],
        "raw_deltas_seconds": [b - a for a, b in zip(raw, raw[1:])],
        "first_raw_minus_query_start": raw[0] - start_epoch if raw else None,
        "last_raw_minus_query_end": raw[-1] - end_epoch if raw else None,
        "all_60_second_steps": all(b - a == 60 for a, b in zip(raw, raw[1:])),
        "raw_set_matches_expected_numeric_set": set(raw) == set(range(start_epoch, end_epoch + 60, 60)),
        "last_error": mt5.last_error(),
        "diagnostic": "HISTORICAL_RAW_EPOCH_BOUNDARY_TEST; NO_TIMESTAMP_CONVERSION; NO_SHIFT"
    }

    print(json.dumps(result, indent=2))
finally:
    mt5.shutdown()
