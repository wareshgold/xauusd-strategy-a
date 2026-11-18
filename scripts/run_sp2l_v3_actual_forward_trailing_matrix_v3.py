"""
SP2L V3 — ACTUAL FORWARD TRAILING MATRIX V3

Research-only counterfactual matrix.

IMPORTANT:
- Does NOT place orders.
- Does NOT modify the live forward runner.
- V2 is intentionally left untouched.
- RR / activation / trail / 2X are research parameters only.
- 2X intrabar ordering remains unresolved; this is an M1-touch counterfactual.
"""

from __future__ import annotations
import os

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import MetaTrader5 as mt5

import sp2l_v3_config as cfg


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "v3_matrix"
OUT.mkdir(parents=True, exist_ok=True)

# IMPORTANT: Matrix V3 must match live Forward trailing units for XAUUSD.ecn.
# MT5 symbol point = 0.01 price; live ACT10/TRAIL2 means 0.10/0.02 price.
PIP = 0.01
DEFAULT_MAGIC = 26092201

# ---------------------------------------------------------------------
# Frozen research grid
# ---------------------------------------------------------------------

RR_GRID = (1, 2, 4)

ACTS = (
    0,
    2,
    4,
    6,
    8,
    10,
    20,
    30,
    40,
    50,
)

TRAILS = (
    2,
    4,
    6,
    8,
    10,
    12,
    20,
    30,
    40,
    50,
)

TWO_X_GRID = (False, True)

EXPECTED_VARIANTS = (
    len(RR_GRID)
    * len(ACTS)
    * len(TRAILS)
    * len(TWO_X_GRID)
)

# Historical audited forward reference.
FORWARD_ACTIVATION_PIPS = 10
FORWARD_TRAIL_PIPS = 2
FORWARD_2X = False
FORWARD_RR = 2.0


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def finish(
    t,
    reason,
    exit_price,
    e2,
    active,
    final_sl,
    mfe,
    tp,
):
    direction = t["direction"]
    entry = float(t["entry"])
    initial_sl = float(t["sl"])

    risk = abs(entry - initial_sl)

    if exit_price is None:
        return {
            "position_id": t["position_id"],
            "reason": reason,
            "realized_R": None,
            "realized_usd": None,
            "entry2_filled": bool(e2),
            "total_entries": 2 if e2 else 1,
            "active": bool(active),
            "final_sl": final_sl,
            "mfe_price": mfe,
        }

    if direction == "BUY":
        pnl_price = float(exit_price) - entry
    else:
        pnl_price = entry - float(exit_price)

    realized_R = pnl_price / risk if risk else None

    # XAUUSD:
    # P/L = price movement × contract size × volume
    contract_size = float(t.get("contract_size", 100.0) or 100.0)
    volume = float(t.get("volume", 0.01) or 0.01)

    realized_usd = pnl_price * contract_size * volume

    return {
        "position_id": t["position_id"],
        "reason": reason,
        "realized_R": realized_R,
        "realized_usd": realized_usd,
        "entry2_filled": bool(e2),
        "total_entries": 2 if e2 else 1,
        "active": bool(active),
        "final_sl": final_sl,
        "mfe_price": mfe,
        "tp_price": tp,
        "entry_time": t["entry_time"],
        "exit_time": t["exit_time"],
        "observed_exit_price": t["exit_observed"],
        "observed_profit_usd": t["profit_usd"],
    }


# ---------------------------------------------------------------------
# MT5 data
# ---------------------------------------------------------------------

def load_fixture_trades(path, start, end, magic=None):
    """
    Load a frozen observed-position fixture exported from the prior
    actual-forward matrix trade CSV.

    Research-only provenance:
      source = FROZEN_OBSERVED_POSITION_FIXTURE

    Only observed-position fields are imported. Variant-dependent fields
    such as RR/TP/trailing/realized_R are intentionally ignored.
    """
    rows = []

    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)

        required = {
            "variant",
            "position_id",
            "direction",
            "weighted_entry",
            "final_sl",
            "entry_time",
            "exit_time",
            "observed_exit_price",
            "observed_profit_usd",
            "entry2_filled",
            "total_entries",
        }

        missing = required - set(reader.fieldnames or [])
        if missing:
            raise RuntimeError(
                "Fixture missing required columns: "
                + ", ".join(sorted(missing))
            )

        for r in reader:
            if r.get("variant") != "NO_TRAILING_RR1":
                continue

            if str(r.get("entry2_filled", "")).strip().lower() != "false":
                raise RuntimeError(
                    f"Fixture position {r.get('position_id')} has entry2_filled != False"
                )

            if str(r.get("total_entries", "")).strip() != "1":
                raise RuntimeError(
                    f"Fixture position {r.get('position_id')} has total_entries != 1"
                )

            entry_time = int(float(r["entry_time"]))
            exit_time = int(float(r["exit_time"]))

            rows.append(
                {
                    "position_id": int(r["position_id"]),
                    "direction": str(r["direction"]).upper(),
                    "entry": float(r["weighted_entry"]),
                    "sl": float(r["final_sl"]),
                    # Observed TP is deliberately NOT imported.
                    "tp": None,
                    "entry_time": entry_time,
                    "exit_time": exit_time,
                    "exit_observed": float(r["observed_exit_price"]),
                    "profit_usd": float(r["observed_profit_usd"]),
                    "volume": 0.01,
                    "contract_size": 100.0,
                }
            )

    rows = [
        r for r in rows
        if int(start.timestamp()) <= r["entry_time"] <= int(end.timestamp())
    ]

    rows.sort(key=lambda x: x["entry_time"])

    if not rows:
        raise RuntimeError(
            f"Frozen fixture produced 0 positions: {path}"
        )

    ids = [r["position_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError(
            "Frozen fixture contains duplicate position_id values"
        )

    print(
        "FIXTURE_SOURCE=FROZEN_OBSERVED_POSITION_FIXTURE"
    )
    print(
        f"FIXTURE_FILE={path}"
    )
    print(
        f"FIXTURE_VARIANT=NO_TRAILING_RR1"
    )
    print(
        f"FIXTURE_POSITIONS={len(rows)}"
    )
    print(
        f"FIXTURE_BUY={sum(r['direction'] == 'BUY' for r in rows)}"
    )
    print(
        f"FIXTURE_SELL={sum(r['direction'] == 'SELL' for r in rows)}"
    )
    print(
        "FIXTURE_2X_FILLED=0"
    )

    return rows

def completed_trades(symbol, start, end, magic):
    fixture_path = os.getenv("SP2L_MATRIX_FIXTURE_TRADES", "").strip()

    if fixture_path:
        return load_fixture_trades(
            fixture_path,
            start,
            end,
            magic,
        )

    deals = mt5.history_deals_get(start, end)

    if deals is None:
        raise RuntimeError(
            f"history_deals_get failed: {mt5.last_error()}"
        )

    positions = {}

    for d in deals:
        if getattr(d, "symbol", None) != symbol:
            continue

        if int(getattr(d, "magic", 0) or 0) != int(magic):
            continue

        position_id = int(getattr(d, "position_id", 0) or 0)

        if not position_id:
            continue

        entry_type = getattr(d, "entry", None)

        positions.setdefault(
            position_id,
            {
                "position_id": position_id,
                "deals": [],
            },
        )

        positions[position_id]["deals"].append(d)

    result = []

    for position_id, p in positions.items():
        ds = sorted(
            p["deals"],
            key=lambda x: int(getattr(x, "time", 0) or 0),
        )

        if not ds:
            continue

        opens = [
            d for d in ds
            if getattr(d, "entry", None)
            == mt5.DEAL_ENTRY_IN
        ]

        closes = [
            d for d in ds
            if getattr(d, "entry", None)
            == mt5.DEAL_ENTRY_OUT
        ]

        if not opens or not closes:
            continue

        op = opens[0]
        cl = closes[-1]

        direction = (
            "BUY"
            if getattr(op, "type", None) == mt5.DEAL_TYPE_BUY
            else "SELL"
        )

        entry_price = float(getattr(op, "price", 0.0) or 0.0)
        exit_price = float(getattr(cl, "price", 0.0) or 0.0)

        if not entry_price:
            continue

        position_info = mt5.positions_get(ticket=position_id)

        # Historical position is already closed, so positions_get will
        # normally be empty. Initial SL/TP are recovered from order history.
        orders = mt5.history_orders_get(
            start,
            end,
        )

        sl = None
        tp = None
        volume = float(
            getattr(op, "volume", 0.01) or 0.01
        )

        if orders:
            for o in orders:
                if int(getattr(o, "position_id", 0) or 0) != position_id:
                    continue

                if sl is None:
                    value = getattr(o, "sl", None)
                    if value:
                        sl = float(value)

                if tp is None:
                    value = getattr(o, "tp", None)
                    if value:
                        tp = float(value)

        if sl is None:
            continue

        result.append(
            {
                "position_id": position_id,
                "direction": direction,
                "entry": entry_price,
                "sl": sl,
                "tp": tp,
                "entry_time": int(getattr(op, "time", 0)),
                "exit_time": int(getattr(cl, "time", 0)),
                "exit_observed": exit_price,
                "profit_usd": float(
                    sum(
                        float(getattr(d, "profit", 0.0) or 0.0)
                        for d in ds
                    )
                ),
                "volume": volume,
                "contract_size": float(
                    getattr(
                        mt5.symbol_info(symbol),
                        "trade_contract_size",
                        100.0,
                    )
                    or 100.0
                ),
            }
        )

    return sorted(
        result,
        key=lambda x: x["entry_time"],
    )


def load_m1_fixture(path, start, end):
    """
    Load raw MT5 M1 CSV exported by scripts/export_m1_ps3.py.
    """
    start_ts = int(start.timestamp())
    end_ts = int(end.timestamp())

    rows = []

    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)

        required = {"time", "open", "high", "low", "close"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise RuntimeError(
                "M1 fixture missing required columns: "
                + ", ".join(sorted(missing))
            )

        for r in reader:
            raw_time = str(r["time"]).strip()
            try:
                ts = int(float(raw_time))
            except ValueError:
                ts = int(datetime.fromisoformat(raw_time.replace("Z", "+00:00")).timestamp())
            if ts < start_ts or ts > end_ts:
                continue

            rows.append(
                {
                    "time": ts,
                    "open": float(r["open"]),
                    "high": float(r["high"]),
                    "low": float(r["low"]),
                    "close": float(r["close"]),
                }
            )

    rows.sort(key=lambda x: x["time"])

    if not rows:
        raise RuntimeError(
            f"M1 fixture produced 0 bars: {path}"
        )

    print("M1_SOURCE=RAW_MT5_M1_CSV_FIXTURE")
    print(f"M1_FIXTURE_FILE={path}")
    print(f"M1_FIXTURE_BARS={len(rows)}")

    return rows

def m1(symbol, start, end):
    fixture_path = os.getenv("SP2L_MATRIX_M1_CSV", "").strip()

    if fixture_path:
        return load_m1_fixture(
            fixture_path,
            start,
            end,
        )

    rates = mt5.copy_rates_range(
        symbol,
        mt5.TIMEFRAME_M1,
        start,
        end,
    )

    if rates is None:
        raise RuntimeError(
            f"copy_rates_range failed: {mt5.last_error()}"
        )

    return [
        {
            "time": int(r["time"]),
            "open": float(r["open"]),
            "high": float(r["high"]),
            "low": float(r["low"]),
            "close": float(r["close"]),
        }
        for r in rates
    ]


# ---------------------------------------------------------------------
# Replay
# ---------------------------------------------------------------------

def replay(
    t,
    bars,
    rr,
    activation_pips,
    trail_pips,
    two_x,
):
    if not t["sl"]:
        return {
            "position_id": t["position_id"],
            "reason": "MISSING_INITIAL_SL",
            "realized_R": None,
            "realized_usd": None,
            "entry2_filled": False,
            "total_entries": 1,
        }

    t = dict(t)

    risk = abs(
        float(t["entry"]) - float(t["sl"])
    )

    if risk <= 0:
        return {
            "position_id": t["position_id"],
            "reason": "INVALID_RISK",
            "realized_R": None,
            "realized_usd": None,
            "entry2_filled": False,
            "total_entries": 1,
        }

    entry = float(t["entry"])

    # IMPORTANT:
    # TP is recalculated from the matrix RR.
    # We intentionally do NOT use the observed forward TP.
    if t["direction"] == "BUY":
        tp = entry + risk * rr
    else:
        tp = entry - risk * rr

    entry_minute = (
        int(t["entry_time"])
        - (int(t["entry_time"]) % 60)
    )

    exit_minute = (
        int(t["exit_time"])
        - (int(t["exit_time"]) % 60)
    )

    si = next(
        (
            i
            for i, b in enumerate(bars)
            if int(b["time"]) >= entry_minute
        ),
        None,
    )

    ei = next(
        (
            i
            for i, b in enumerate(bars)
            if int(b["time"]) >= exit_minute
        ),
        len(bars) - 1,
    )

    if si is None:
        return {
            "position_id": t["position_id"],
            "reason": "MISSING_M1_ENTRY",
            "realized_R": None,
            "realized_usd": None,
            "entry2_filled": False,
            "total_entries": 1,
        }

    trailing_enabled = trail_pips > 0

    trail_distance = trail_pips * PIP
    activation = activation_pips * PIP

    sl = float(t["sl"])
    active = False
    e2 = False
    mfe = 0.0

    e2p = (
        entry - 0.5 * risk
        if t["direction"] == "BUY"
        else entry + 0.5 * risk
    )

    for b in bars[
        si + 1 : min(ei + 1, len(bars))
    ]:
        hi = float(b["high"])
        lo = float(b["low"])

        if t["direction"] == "BUY":

            mfe = max(
                mfe,
                hi - entry,
            )

            if (
                two_x
                and not e2
                and lo <= e2p
            ):
                e2 = True

            if (
                trailing_enabled
                and hi - entry >= activation
            ):
                active = True
                sl = max(
                    sl,
                    hi - trail_distance,
                )

            hs = lo <= sl
            ht = hi >= tp

        else:

            mfe = max(
                mfe,
                entry - lo,
            )

            if (
                two_x
                and not e2
                and hi >= e2p
            ):
                e2 = True

            if (
                trailing_enabled
                and entry - lo >= activation
            ):
                active = True
                sl = min(
                    sl,
                    lo + trail_distance,
                )

            hs = hi >= sl
            ht = lo <= tp

        if hs and ht:
            return finish(
                t,
                "AMBIGUOUS",
                None,
                e2,
                active,
                sl,
                mfe,
                tp,
            )

        if hs:
            return finish(
                t,
                "TRAIL_SL" if active else "SL",
                sl,
                e2,
                active,
                sl,
                mfe,
                tp,
            )

        if ht:
            return finish(
                t,
                "TP",
                tp,
                e2,
                active,
                sl,
                mfe,
                tp,
            )

    return finish(
        t,
        "UNRESOLVED",
        None,
        e2,
        active,
        sl,
        mfe,
        tp,
    )


# ---------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------

def summary(rows):
    decisive = [
        x
        for x in rows
        if (
            x.get("realized_R") is not None
            and x["reason"] != "AMBIGUOUS"
        )
    ]

    wins = [
        x for x in decisive
        if x["realized_R"] > 0
    ]

    losses = [
        x for x in decisive
        if x["realized_R"] < 0
    ]

    gross_profit = sum(
        x["realized_R"]
        for x in wins
    )

    gross_loss = abs(
        sum(
            x["realized_R"]
            for x in losses
        )
    )

    equity_R = 0.0
    peak_R = 0.0
    dd_R = 0.0

    equity_USD = 0.0
    peak_USD = 0.0
    dd_USD = 0.0

    for x in sorted(
        decisive,
        key=lambda z: z["entry_time"],
    ):
        equity_R += x["realized_R"]
        peak_R = max(
            peak_R,
            equity_R,
        )
        dd_R = max(
            dd_R,
            peak_R - equity_R,
        )

        equity_USD += x["realized_usd"] or 0.0
        peak_USD = max(
            peak_USD,
            equity_USD,
        )
        dd_USD = max(
            dd_USD,
            peak_USD - equity_USD,
        )

    return {
        "trades": len(rows),
        "decisive": len(decisive),
        "wins": len(wins),
        "losses": len(losses),
        "ambiguous": len(rows) - len(decisive),

        "win_rate": (
            100.0 * len(wins) / len(decisive)
            if decisive
            else None
        ),

        "profit_factor": (
            gross_profit / gross_loss
            if gross_loss > 0
            else None
        ),

        "net_R": sum(
            x["realized_R"]
            for x in decisive
        ),

        "net_USD": sum(
            x["realized_usd"] or 0.0
            for x in decisive
        ),

        "max_DD_R": dd_R,
        "max_DD_USD": dd_USD,

        "avg_R": (
            sum(
                x["realized_R"]
                for x in decisive
            ) / len(decisive)
            if decisive
            else None
        ),
    }


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()

    ap.add_argument(
        "--mt5-path",
        required=True,
    )

    ap.add_argument(
        "--symbol",
        default="XAUUSD.ecn",
    )

    ap.add_argument(
        "--magic",
        type=int,
        default=DEFAULT_MAGIC,
    )

    ap.add_argument(
        "--start",
        default="2026-10-01T10:37:00+00:00",
    )

    ap.add_argument(
        "--end",
    )

    ap.add_argument(
        "--expected-trades",
        type=int,
        default=38,
    )

    args = ap.parse_args()

    start = utc(args.start)

    end = (
        utc(args.end)
        if args.end
        else datetime.now(timezone.utc)
    )

    if not mt5.initialize(
        path=args.mt5_path
    ):
        raise RuntimeError(
            f"MT5 initialize failed: {mt5.last_error()}"
        )

    try:

        ts = completed_trades(
            args.symbol,
            start,
            end,
            args.magic,
        )

        if len(ts) != args.expected_trades:
            raise RuntimeError(
                f"Expected {args.expected_trades} "
                f"completed positions, found {len(ts)}."
            )

        missing_sl = sum(
            not x["sl"]
            for x in ts
        )

        if missing_sl:
            raise RuntimeError(
                f"Initial-order data incomplete: "
                f"missing SL={missing_sl}."
            )

        bars = m1(
            args.symbol,
            datetime.fromtimestamp(
                min(
                    x["entry_time"]
                    for x in ts
                ),
                timezone.utc,
            ) - timedelta(minutes=2),
            datetime.fromtimestamp(
                max(
                    x["exit_time"]
                    for x in ts
                ),
                timezone.utc,
            ) + timedelta(minutes=2),
        )

        matrix = []

        # -------------------------------------------------------------
        # Baseline: observed no-trailing reference.
        # -------------------------------------------------------------

        baseline_rows = [
            replay(
                x,
                bars,
                FORWARD_RR,
                0,
                0,
                False,
            )
            for x in ts
        ]

        bs = summary(baseline_rows)

        matrix.append(
            {
                "variant": "BASELINE_NO_TRAILING",
                "RR": FORWARD_RR,
                "ACT": 0,
                "TRAIL": 0,
                "2X": "OFF",
                **bs,
            }
        )

        # -------------------------------------------------------------
        # 600-variant research matrix.
        # -------------------------------------------------------------

        for rr in RR_GRID:
            for act in ACTS:
                for trail in TRAILS:
                    for two_x in TWO_X_GRID:

                        rows = [
                            replay(
                                x,
                                bars,
                                rr,
                                act,
                                trail,
                                two_x,
                            )
                            for x in ts
                        ]

                        s = summary(rows)

                        variant = (
                            f"RR{rr}_"
                            f"ACT{act}_"
                            f"TRAIL{trail}_"
                            f"2X{'ON' if two_x else 'OFF'}"
                        )

                        matrix.append(
                            {
                                "variant": variant,
                                "RR": rr,
                                "ACT": act,
                                "TRAIL": trail,
                                "2X": (
                                    "ON"
                                    if two_x
                                    else "OFF"
                                ),
                                **s,
                            }
                        )

        # -------------------------------------------------------------
        # Compact ranking
        # -------------------------------------------------------------

        ranked = sorted(
            matrix[1:],
            key=lambda x: (
                float(
                    x["net_USD"]
                    if x["net_USD"] is not None
                    else -10**18
                ),
                float(
                    x["profit_factor"]
                    if x["profit_factor"] is not None
                    else -10**18
                ),
            ),
            reverse=True,
        )

        stamp = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%dT%H%M%SZ"
        )

        base = (
            OUT
            / f"SP2L_V3_ACTUAL_FORWARD_TRAILING_MATRIX_V3_{stamp}"
        )

        matrix_csv = base.with_suffix(
            ".csv"
        )

        top20_csv = base.with_name(
            base.name + "_TOP20.csv"
        )

        json_path = base.with_suffix(
            ".json"
        )

        snapshot = base.with_name(
            base.name + "_SNAPSHOT.md"
        )

        fields = [
            "variant",
            "RR",
            "ACT",
            "TRAIL",
            "2X",
            "trades",
            "win_rate",
            "profit_factor",
            "net_R",
            "net_USD",
            "max_DD_USD",
            "avg_R",
        ]

        with open(
            matrix_csv,
            "w",
            newline="",
            encoding="utf-8",
        ) as f:

            w = csv.DictWriter(
                f,
                fieldnames=fields,
            )

            w.writeheader()

            for row in matrix:
                w.writerow(
                    {
                        k: row.get(k)
                        for k in fields
                    }
                )

        with open(
            top20_csv,
            "w",
            newline="",
            encoding="utf-8",
        ) as f:

            w = csv.DictWriter(
                f,
                fieldnames=fields,
            )

            w.writeheader()

            for row in ranked[:20]:
                w.writerow(
                    {
                        k: row.get(k)
                        for k in fields
                    }
                )

        payload = {
            "version":
                "SP2L_V3_ACTUAL_FORWARD_TRAILING_MATRIX_20261005_V3",
            "research_only": True,
            "canonical": False,
            "symbol": args.symbol,
            "magic": args.magic,
            "start_utc": start.isoformat(),
            "end_utc": end.isoformat(),
            "actual_positions": len(ts),
            "m1_bars": len(bars),
            "pip_size_price": PIP,
            "rr_grid": RR_GRID,
            "activation_grid": ACTS,
            "trail_grid": TRAILS,
            "two_x": [False, True],
            "counterfactual_variants":
                EXPECTED_VARIANTS,
            "matrix_rows": len(matrix),
            "ranking":
                "net_USD_desc_then_profit_factor_desc",
            "two_x_semantics":
                "M1_TOUCH_COUNTERFACTUAL_UNRESOLVED_INTRABAR_ORDERING",
            "matrix": matrix,
        }

        raw = json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )

        json_path.write_text(
            raw,
            encoding="utf-8",
        )

        sha = hashlib.sha256(
            raw.encode()
        ).hexdigest()

        snapshot.write_text(
            "\n".join(
                [
                    "# SP2L V3 — Actual Forward Trailing Matrix V3",
                    "",
                    "Research-only. No canonical decision.",
                    "",
                    f"- Completed positions: {len(ts)}",
                    f"- M1 bars: {len(bars)}",
                    f"- Pip size price: {PIP}",
                    f"- RR grid: {list(RR_GRID)}",
                    f"- Activation grid: {list(ACTS)}",
                    f"- Trail grid: {list(TRAILS)}",
                    "- 2X: OFF / ON",
                    f"- Counterfactual variants: {EXPECTED_VARIANTS}",
                    "- Baseline: NO_TRAILING",
                    "- Ranking: Net USD descending, then PF",
                    "- 2X intrabar ordering: unresolved",
                    f"- JSON SHA256: {sha}",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        # -------------------------------------------------------------
        # Console: intentionally compact.
        # -------------------------------------------------------------

        print()
        print("=" * 105)
        print("SP2L V3 — ACTUAL FORWARD TRAILING MATRIX V3")
        print("=" * 105)

        print(
            f"Positions: {len(ts)} | "
            f"M1 bars: {len(bars)} | "
            f"Variants: {EXPECTED_VARIANTS}"
        )

        print()
        print(
            "TOP 20 — ranked by Net USD"
        )
        print("-" * 105)

        print(
            f"{'#':>3} "
            f"{'VARIANT':<29} "
            f"{'TR':>4} "
            f"{'WR%':>7} "
            f"{'PF':>7} "
            f"{'NET R':>9} "
            f"{'NET USD':>10} "
            f"{'DD USD':>10} "
            f"{'AVG R':>8}"
        )

        print("-" * 105)

        for i, row in enumerate(
            ranked[:20],
            start=1,
        ):

            pf = (
                f"{row['profit_factor']:.2f}"
                if row["profit_factor"] is not None
                else "INF"
            )

            print(
                f"{i:>3} "
                f"{row['variant']:<29} "
                f"{int(row['trades']):>4} "
                f"{row['win_rate']:>6.1f}% "
                f"{pf:>7} "
                f"{row['net_R']:>9.2f} "
                f"${row['net_USD']:>9.2f} "
                f"${row['max_DD_USD']:>9.2f} "
                f"{row['avg_R']:>8.3f}"
            )

        print()
        print("FILES")
        print(f"Full matrix : {matrix_csv}")
        print(f"Top 20      : {top20_csv}")
        print(f"JSON        : {json_path}")
        print(f"Snapshot    : {snapshot}")
        print(f"SHA256      : {sha}")
        print("=" * 105)

    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()






