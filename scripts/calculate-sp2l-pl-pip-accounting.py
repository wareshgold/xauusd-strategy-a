import argparse
import json
import math
from pathlib import Path

INPUT = Path("artifacts/SP2L_author_replica_2026-09-14_2026-09-18.json")
OUTPUT = Path("artifacts/SP2L_pl_pip_accounting_2026-09-14_2026-09-18.json")

parser = argparse.ArgumentParser(description="Research-only SP2L P/L and pip accounting.")
parser.add_argument("--pip-size", type=float, required=True, help="Accounting pip size in XAUUSD price units; supplied explicitly, not inferred.")
parser.add_argument("--tick-size", type=float, required=True, help="MT5 symbol tick size in price units.")
parser.add_argument("--tick-value", type=float, required=True, help="MT5 tick value in account currency for 1.00 lot.")
parser.add_argument("--lot", type=float, default=0.01, help="Lot size for the accounting view.")
args = parser.parse_args()

if min(args.pip_size, args.tick_size, args.tick_value, args.lot) <= 0:
    raise SystemExit("All accounting inputs must be > 0.")

p = json.loads(INPUT.read_text(encoding="utf-8"))
signals = p["signals"] if "signals" in p else p.get("trades", [])

rows = []
for s in signals:
    direction = s["direction"]
    entry = float(s["entry"])
    sl = float(s["sl"])
    tp = float(s["tp"])
    outcome = s["outcome"]

    if direction == "BUY":
        tp_move = tp - entry
        sl_move = sl - entry
    elif direction == "SELL":
        tp_move = entry - tp
        sl_move = entry - sl
    else:
        raise ValueError(f"Unsupported direction: {direction}")

    if outcome == "WIN":
        realized_price_move = tp_move
        realized_label = "TP"
    elif outcome == "LOSS":
        realized_price_move = sl_move
        realized_label = "SL"
    else:
        realized_price_move = None
        realized_label = None

    def money(price_move):
        return price_move / args.tick_size * args.tick_value * args.lot

    rows.append({
        "archived_signal_index": s.get("signal_index", s.get("archived_signal_index")),
        "signal_time_utc": s.get("signal_time_utc"),
        "direction": direction,
        "outcome": outcome,
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "lot": args.lot,
        "pip_size_price_units": args.pip_size,
        "tp_distance_price_units": tp_move,
        "sl_distance_price_units": sl_move,
        "tp_distance_pips": abs(tp_move) / args.pip_size,
        "sl_distance_pips": abs(sl_move) / args.pip_size,
        "realized_result_source": realized_label,
        "realized_price_move": realized_price_move,
        "realized_pips": (realized_price_move / args.pip_size) if realized_price_move is not None else None,
        "realized_pl_account_currency": money(realized_price_move) if realized_price_move is not None else None,
    })

decisive = [r for r in rows if r["realized_pl_account_currency"] is not None]
wins = [r for r in decisive if r["outcome"] == "WIN"]
losses = [r for r in decisive if r["outcome"] == "LOSS"]

gross_profit = sum(r["realized_pl_account_currency"] for r in wins)
gross_loss_abs = abs(sum(r["realized_pl_account_currency"] for r in losses))
net_pl = gross_profit - gross_loss_abs
net_pips = sum(r["realized_pips"] for r in decisive)
gross_profit_pips = sum(r["realized_pips"] for r in wins)
gross_loss_pips_abs = abs(sum(r["realized_pips"] for r in losses))

equity = 0.0
peak = 0.0
max_drawdown = 0.0
for r in rows:
    if r["realized_pl_account_currency"] is None:
        continue
    equity += r["realized_pl_account_currency"]
    peak = max(peak, equity)
    max_drawdown = max(max_drawdown, peak - equity)

out = {
    "research_only": True,
    "artifact_type": "SP2L_PL_PIP_ACCOUNTING",
    "input_artifact": str(INPUT),
    "accounting_inputs": {
        "pip_size_price_units": args.pip_size,
        "tick_size_price_units": args.tick_size,
        "tick_value_account_currency_per_1_lot": args.tick_value,
        "lot": args.lot,
    },
    "accounting_note": "Pip size and MT5 tick economics are accounting inputs only. They do not define Strategy A geometry, entry, SL, TP, fill semantics, or execution rules.",
    "signal_count": len(rows),
    "outcome_counts": {
        "WIN": len(wins),
        "LOSS": len(losses),
        "AMBIGUOUS": sum(r["outcome"] == "AMBIGUOUS" for r in rows),
    },
    "summary": {
        "gross_profit_pips": gross_profit_pips,
        "gross_loss_pips_abs": gross_loss_pips_abs,
        "net_pips": net_pips,
        "gross_profit_account_currency": gross_profit,
        "gross_loss_account_currency_abs": gross_loss_abs,
        "net_pl_account_currency": net_pl,
        "profit_factor": (gross_profit / gross_loss_abs) if gross_loss_abs else None,
        "max_drawdown_account_currency": max_drawdown,
    },
    "signals": rows,
    "canonicalization_guard": "ACCOUNTING_ONLY; NO_STRATEGY_RULE_PROMOTED",
}

OUTPUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({
    "status": "CALCULATED",
    "output": str(OUTPUT),
    "signals": len(rows),
    "outcome_counts": out["outcome_counts"],
    "summary": out["summary"],
    "accounting_inputs": out["accounting_inputs"],
}, ensure_ascii=False, indent=2))
