"""Display-only heartbeat monitor for the V2 SP2L forward runner.

This process never initializes MT5, never evaluates strategy geometry, and never
places/cancels orders. It only tails the existing forward event ledger and
prints HEARTBEAT events in its own PowerShell window.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", required=True)
    parser.add_argument("--poll-seconds", type=float, default=1.0)
    args = parser.parse_args()

    path = Path(args.events)
    print("=== SP2L V2 Forward — Heartbeat Monitor ===")
    print(f"Ledger: {path}")
    print("Display-only: no MT5 connection, no strategy execution, no orders.")
    print("Waiting for HEARTBEAT events...\n")

    path.parent.mkdir(parents=True, exist_ok=True)
    position = path.stat().st_size if path.exists() else 0

    while True:
        if not path.exists():
            time.sleep(args.poll_seconds)
            continue

        with path.open("r", encoding="utf-8") as f:
            f.seek(position)
            while True:
                line = f.readline()
                if not line:
                    position = f.tell()
                    break
                position = f.tell()
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("event") != "HEARTBEAT":
                    continue

                ts = event.get("ts_utc", "?")
                uptime = event.get("uptime_seconds", "?")
                pid = event.get("pid", "?")
                connected = event.get("mt5_connected", "?")
                allowed = event.get("trade_allowed", "?")
                symbols = event.get("symbols", {})
                last_bars = ", ".join(
                    f"{symbol}={data.get('last_bar_utc') or '-'}"
                    for symbol, data in symbols.items()
                )
                ledger = event.get("ledger", {})
                print(
                    f"[{ts}] PID={pid} uptime={uptime}s "
                    f"MT5={connected} trade_allowed={allowed} "
                    f"last_bar={last_bars or '-'} "
                    f"active_orders={event.get('active_orders', 0)} "
                    f"active_positions={event.get('active_positions', 0)} "
                    f"seen={event.get('state_seen', 0)} "
                    f"notified={event.get('state_notified', 0)} "
                    f"ledger={ledger}",
                    flush=True,
                )
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    main()
