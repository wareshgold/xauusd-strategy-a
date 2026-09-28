import argparse
import csv
import json
from pathlib import Path


def f(v, default=0.0):
    try:
        if v in ("", None):
            return default
        return float(v)
    except Exception:
        return default


def load_specs(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def estimate_xau(row, spec):
    trades = int(f(row.get("trades")))
    if trades <= 0:
        return None

    wins = int(f(row.get("wins")))
    losses = int(f(row.get("losses")))

    net_r = f(row.get("net_r"))
    win_rate = f(row.get("win_rate_pct"))
    pf = f(row.get("profit_factor"))
    dd = f(row.get("max_drawdown_r"))

    # Research estimate only.
    # Uses MT5 symbol properties, not FX pip assumptions.
    volume = 0.01

    tick_value = f(spec.get("tick_value"))
    tick_size = f(spec.get("tick_size"))

    result = dict(row)

    result.update({
        "symbol": "XAUUSD",
        "research_only": True,
        "volume_lot": volume,
        "tick_value": tick_value,
        "tick_size": tick_size,
        "wins": wins,
        "losses": losses,
        "win_rate_pct": win_rate,
        "net_r": net_r,
        "profit_factor": pf,
        "max_drawdown_r": dd,
    })

    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--symbol-spec", required=True)
    ap.add_argument("--output-json", required=True)
    args = ap.parse_args()

    specs = load_specs(args.symbol_spec)

    # accept XAUUSD.ecn or XAUUSD
    spec = None
    for k, v in specs.items():
        if k.startswith("XAUUSD"):
            spec = v
            break

    if spec is None:
        raise RuntimeError("XAUUSD symbol spec not found")

    rows = []

    with open(args.input, encoding="utf-8") as fh:
        reader = csv.DictReader(fh)

        for row in reader:
            r = estimate_xau(row, spec)
            if r:
                rows.append(r)

    rows.sort(key=lambda x: x["net_r"], reverse=True)

    out = {
        "status": "COMPLETE",
        "research_only": True,
        "symbol": "XAUUSD",
        "rows": rows,
        "notes": [
            "Separate XAU analyzer.",
            "Does not modify FX analyzer.",
            "Uses MT5 symbol specification."
        ]
    }

    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)

    with open(args.output_json, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)

    print(f"COMPLETE rows={len(rows)}")


if __name__ == "__main__":
    main()