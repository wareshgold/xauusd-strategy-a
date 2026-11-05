"""Read-only SP2L V3.1 daily performance diagnostics.

Standalone companion to the Trading Intelligence dashboard. Reads only the
existing filesystem monitor snapshot; never imports MetaTrader5 or accesses
broker/trading APIs. All classifications are descriptive, not causal.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone, timedelta
import json
import os

from flask import Flask, jsonify, Response, request

import sp2l_v31_trading_intelligence_dashboard as intelligence

APP = Flask(__name__)
PORT = int(os.getenv("SP2L_DIAGNOSTICS_PORT", "8796"))
DEFAULT_START = os.getenv("SP2L_DIAGNOSTICS_START", "2026-11-04")
DEFAULT_END = os.getenv("SP2L_DIAGNOSTICS_END", "2026-11-05")
TRAIL_ACTIVATION_PRICE = 0.40
TEHRAN = timezone(timedelta(hours=3, minutes=30))


def _num(value):
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _dt(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed
    except (TypeError, ValueError):
        return None


def _day(value):
    stamp = _dt(value)
    return stamp.astimezone(TEHRAN).date().isoformat() if stamp else None


def _side(event):
    for key in ("direction", "side"):
        value = event.get(key)
        if str(value).upper() in ("BUY", "SELL"):
            return str(value).upper()
    signal = event.get("signal_id")
    if isinstance(signal, str):
        suffix = signal.rsplit(":", 1)[-1].upper()
        if suffix in ("BUY", "SELL"):
            return suffix
    # POSITION_LIFECYCLE uses MT5 position type: 0=BUY, 1=SELL.
    if event.get("event") == "POSITION_LIFECYCLE":
        try:
            return {0: "BUY", 1: "SELL"}.get(int(event.get("type")))
        except (TypeError, ValueError):
            return None
    return None


def _build_diagnostics(events, start_date=DEFAULT_START, end_date=DEFAULT_END):
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    if end < start:
        raise ValueError("end_date must be on or after start_date")

    # Keep one Runner-recorded lifecycle row per broker deal identifier.
    unique_deals = {}
    for event in events:
        if event.get("event") != "TELEGRAM_DEAL_LIFECYCLE":
            continue
        deal_id = event.get("deal")
        if deal_id is not None:
            unique_deals.setdefault(str(deal_id), event)

    grouped = defaultdict(list)
    for event in unique_deals.values():
        position = event.get("position")
        if position is not None:
            grouped[str(position)].append(event)

    position_events = defaultdict(list)
    trail_events = defaultdict(list)
    for event in events:
        position = event.get("position")
        if position is None:
            continue
        key = str(position)
        if event.get("event") == "POSITION_LIFECYCLE":
            position_events[key].append(event)
        elif event.get("event") in ("TRAIL_UPDATE", "TRAIL_DEFERRED"):
            trail_events[key].append(event)

    trades = []
    for position_id, deals in grouped.items():
        deals.sort(key=lambda row: row.get("ts_utc") or "")
        exits = [d for d in deals if d.get("entry") in (1, 3)]
        if not exits:
            continue
        close_event = exits[-1]
        close_day = _day(close_event.get("ts_utc"))
        if not close_day or not (start <= date.fromisoformat(close_day) <= end):
            continue
        net_values = [_num(d.get("net")) for d in deals]
        known_net = [v for v in net_values if v is not None]
        net = round(sum(known_net), 2) if known_net else None
        side = next((_side(d) for d in deals if _side(d)), None)
        samples = position_events.get(position_id, [])
        entry_prices = [_num(d.get("entry_price")) for d in deals if d.get("entry") == 0]
        entry = next((v for v in entry_prices if v is not None), None)
        if entry is None:
            entry = next((_num(e.get("price_open")) for e in samples
                          if _num(e.get("price_open")) is not None), None)
        favorable = []
        adverse = []
        for sample in samples:
            px = _num(sample.get("price_current"))
            open_px = _num(sample.get("price_open"))
            ref = entry if entry is not None else open_px
            sample_side = _side(sample) or side
            if px is None or ref is None or sample_side not in ("BUY", "SELL"):
                continue
            move = px - ref if sample_side == "BUY" else ref - px
            favorable.append(max(0.0, move))
            adverse.append(max(0.0, -move))
        mfe = max(favorable) if favorable else None
        mae = max(adverse) if adverse else None

        t_events = trail_events.get(position_id, [])
        successful = [e for e in t_events if e.get("event") == "TRAIL_UPDATE" and e.get("success") is True]
        failed = [e for e in t_events if e.get("event") == "TRAIL_UPDATE" and e.get("success") is False]
        deferred = [e for e in t_events if e.get("event") == "TRAIL_DEFERRED"]
        success_keys = {
            str(e.get("completed_bar_time")) for e in successful
            if e.get("completed_bar_time") is not None
        }
        unresolved_deferred = [
            e for e in deferred
            if e.get("completed_bar_time") is None
            or str(e.get("completed_bar_time")) not in success_keys
        ]
        activated = any(
            (_num(e.get("favorable_move")) or 0) >= TRAIL_ACTIVATION_PRICE
            for e in successful + failed
        )
        trades.append({
            "position_id": position_id,
            "close_day_utc": close_day,
            "side": side or "UNKNOWN",
            "net": net,
            "deal_count": len(deals),
            "exit_deal_count": len(exits),
            "entry": entry,
            "sampled_mfe_price": round(mfe, 4) if mfe is not None else None,
            "sampled_mae_price": round(mae, 4) if mae is not None else None,
            "price_sample_count": len(favorable),
            "trail_success": len(successful),
            "trail_failed": len(failed),
            "trail_deferred": len(deferred),
            "trail_deferred_unrecovered_same_bar": len(unresolved_deferred),
            "trail_activation_observed": activated,
            "trail_evidence": "TRAIL_UPDATE favorable_move" if activated else (
                "sampled POSITION_LIFECYCLE excursion only" if mfe is not None and mfe >= TRAIL_ACTIVATION_PRICE
                else "not established from available events"
            ),
            "canonical": False,
        })

    def summarize(rows):
        known = [r for r in rows if r["net"] is not None]
        return {
            "closed_position_groups": len(rows),
            "net_sum_runner_recorded": round(sum(r["net"] for r in known), 2),
            "wins": sum(r["net"] > 0 for r in known),
            "losses": sum(r["net"] < 0 for r in known),
            "breakeven": sum(r["net"] == 0 for r in known),
            "unknown_net": len(rows) - len(known),
            "buy": summarize_side(rows, "BUY"),
            "sell": summarize_side(rows, "SELL"),
            "trailing": {
                "positions_with_success": sum(r["trail_success"] > 0 for r in rows),
                "positions_with_failed_update": sum(r["trail_failed"] > 0 for r in rows),
                "positions_with_deferred_update": sum(r["trail_deferred"] > 0 for r in rows),
                "positions_with_unrecovered_deferred_same_bar": sum(
                    r["trail_deferred_unrecovered_same_bar"] > 0 for r in rows
                ),
                "losses_with_unrecovered_deferred_same_bar": sum(
                    r["net"] is not None and r["net"] < 0
                    and r["trail_deferred_unrecovered_same_bar"] > 0 for r in rows
                ),
            },
            "sampled_excursions": {
                "positions_with_price_samples": sum(r["price_sample_count"] > 0 for r in rows),
                "positions_with_mfe_at_least_activation": sum(
                    r["sampled_mfe_price"] is not None and r["sampled_mfe_price"] >= TRAIL_ACTIVATION_PRICE
                    for r in rows
                ),
                "positions_with_mae_greater_than_mfe": sum(
                    r["sampled_mae_price"] is not None and r["sampled_mfe_price"] is not None
                    and r["sampled_mae_price"] > r["sampled_mfe_price"] for r in rows
                ),
            },
        }

    def summarize_side(rows, side):
        subset = [r for r in rows if r["side"] == side and r["net"] is not None]
        return {
            "positions": len(subset),
            "net": round(sum(r["net"] for r in subset), 2),
            "wins": sum(r["net"] > 0 for r in subset),
            "losses": sum(r["net"] < 0 for r in subset),
        }

    daily = []
    cursor = start
    while cursor <= end:
        day = cursor.isoformat()
        rows = [r for r in trades if r["close_day_utc"] == day]
        daily.append({"date_utc": day, **summarize(rows), "trades": rows})
        cursor = date.fromordinal(cursor.toordinal() + 1)

    return {
        "date_start_local": start.isoformat(),
        "date_end_local": end.isoformat(),
        "timezone": "Asia/Tehran (UTC+03:30 fixed offset)",
        "daily": daily,
        "overall": summarize(trades),
        "trades": sorted(trades, key=lambda r: (r["close_day_utc"], r["position_id"])),
        "data_limits": [
            "P&L is the sum of Runner-recorded TELEGRAM_DEAL_LIFECYCLE net fields, grouped by position; it is not broker-reconciled account equity.",
            "A position group is assigned to the UTC date of its last recorded OUT/OUT_BY deal. Multi-exit positions may span dates.",
            "MFE/MAE are sampled POSITION_LIFECYCLE price observations, not tick-complete excursions; absent samples mean unknown, not zero.",
            "Trailing counts are correlated by position. A deferred update is considered recovered only when a successful TRAIL_UPDATE for the same completed M1 bar is present in this event window.",
            "Direction comparison is descriptive. It cannot prove market trend or that an entry direction was wrong.",
            "No market tick/bar replay is included; exact counterfactual P&L with a different trailing rule is unavailable.",
        ],
        "thresholds": {"trailing_activation_price": TRAIL_ACTIVATION_PRICE},
        "mt5_queried": False,
        "broker_state_verified": False,
    }


@APP.get("/api/diagnostics")
def api_diagnostics():
    start = request.args.get("start", DEFAULT_START)
    end = request.args.get("end", DEFAULT_END)
    try:
        snapshot = intelligence.ops._snapshot()
        result = _build_diagnostics(snapshot["events"], start, end)
        result["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
        result["event_health"] = snapshot["health"]
        result["runner"] = snapshot["runner"]
        return jsonify(result)
    except (ValueError, KeyError) as exc:
        return jsonify({"error": str(exc)}), 400


HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SP2L Performance Diagnostics</title>
<style>
:root{color-scheme:dark;--bg:#0b1220;--panel:#121f31;--line:#2a3b52;--text:#edf3fb;--muted:#9eafc4;--blue:#8dbdff;--green:#5bd6a4;--red:#ff8294;--amber:#f2c66d}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px Segoe UI,Arial,sans-serif}main{max-width:1500px;margin:auto;padding:24px}
header{display:flex;justify-content:space-between;gap:16px;align-items:center;margin-bottom:18px}h1{font-size:24px;margin:5px 0}.muted,small{color:var(--muted)}.eyebrow{color:var(--blue);font-size:10px;letter-spacing:1.5px;font-weight:bold}
.controls{display:flex;gap:8px;flex-wrap:wrap}.controls input,.controls button{background:var(--panel);color:var(--text);border:1px solid var(--line);padding:9px;border-radius:7px}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.card{background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:15px;min-width:0}.k{font-size:11px;color:var(--muted)}.v{font-size:24px;font-weight:700;margin-top:8px}.green{color:var(--green)}.red{color:var(--red)}.amber{color:var(--amber)}
h2{font-size:15px;margin:22px 0 9px}.note{background:#18263a;border:1px solid var(--line);border-left:3px solid var(--amber);padding:12px;border-radius:8px;color:var(--muted);font-size:12px;line-height:1.6;margin:12px 0}
.two{display:grid;grid-template-columns:1fr 1fr;gap:10px}.tablewrap{overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:10px}
table{width:100%;border-collapse:collapse;white-space:nowrap;font-size:12px}th,td{text-align:left;padding:10px;border-bottom:1px solid var(--line)}th{font-size:10px;color:var(--muted);text-transform:uppercase}
ul{padding-left:18px;color:var(--muted);font-size:12px;line-height:1.65}.status{border:1px solid var(--line);padding:7px 10px;border-radius:20px;font-size:11px}
@media(max-width:850px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.two{grid-template-columns:1fr}}@media(max-width:520px){main{padding:14px}header{align-items:flex-start;flex-direction:column}.grid{grid-template-columns:1fr 1fr}}
</style></head><body><main>
<header><div><div class="eyebrow">SP2L / V3.1 · READ-ONLY</div><h1>Performance Diagnostics</h1><div class="muted">Daily comparison · Direction · Trailing · Sampled excursions · Tehran time</div></div>
<div class="controls"><label>From <input id="start" type="date" value="2026-11-04"></label><label>To <input id="end" type="date" value="2026-11-05"></label><button id="load">Refresh</button><span class="status" id="status">Loading…</span></div></header>
<div class="note">This report describes Runner-recorded evidence only. It does not connect to MT5, verify broker inventory, issue BUY/SELL decisions, or prove causality. Missing observations remain unknown.</div>
<div id="days"></div>
<h2>BUY vs SELL</h2><div class="two" id="direction"></div>
<h2>Trailing evidence</h2><div class="two" id="trailing"></div>
<h2>Closed position groups</h2><div class="tablewrap"><table><thead><tr><th>Tehran close day</th><th>Position</th><th>Side</th><th>Net</th><th>Sampled MFE</th><th>Sampled MAE</th><th>Price samples</th><th>Trail OK</th><th>Trail failed</th><th>Deferred</th><th>Unrecovered same-bar</th><th>Activation evidence</th></tr></thead><tbody id="trades"></tbody></table></div>
<h2>Interpretation limits</h2><ul id="limits"></ul>
</main><script>
const $=id=>document.getElementById(id), f=v=>v===null||v===undefined?"—":Number(v).toFixed(2), esc=v=>String(v??"—").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function card(k,v,n=""){return '<div class="card"><div class="k">'+k+'</div><div class="v">'+v+'</div><small>'+n+'</small></div>'}
function dayBlock(d){return '<h2>'+d.date_utc+'</h2><div class="grid">'+card("Closed position groups",d.closed_position_groups)+card("Recorded net",f(d.net_sum_runner_recorded), "Runner deal net; not equity")+card("Wins / losses",d.wins+" / "+d.losses)+card("Unknown net",d.unknown_net)+'</div><div class="grid" style="margin-top:9px">'+card("BUY net",f(d.buy.net),d.buy.positions+" positions · "+d.buy.wins+"W / "+d.buy.losses+"L")+card("SELL net",f(d.sell.net),d.sell.positions+" positions · "+d.sell.wins+"W / "+d.sell.losses+"L")+card("Losses with unrecovered deferred",d.trailing.losses_with_unrecovered_deferred_same_bar)+card("MFE ≥ $0.40 sampled",d.sampled_excursions.positions_with_mfe_at_least_activation)+'</div>'}
function render(d){$("status").textContent="Read-only · MT5 not queried";$("days").innerHTML=d.daily.map(dayBlock).join("");
const s=d.overall;$("direction").innerHTML=['BUY','SELL'].map(side=>{const x=s[side.toLowerCase()];return '<div class="card"><b>'+side+'</b><div class="grid" style="margin-top:12px">'+card("Positions",x.positions)+card("Net",f(x.net))+card("Wins",x.wins)+card("Losses",x.losses)+'</div></div>'}).join("");
const t=s.trailing,e=s.sampled_excursions;$("trailing").innerHTML='<div class="card"><b>Trailing event correlation</b><div class="grid" style="margin-top:12px">'+card("Positions with success",t.positions_with_success)+card("Positions with failed update",t.positions_with_failed_update)+card("Positions with deferred update",t.positions_with_deferred_update)+card("Deferred not recovered same bar",t.positions_with_unrecovered_deferred_same_bar)+card("Losing positions in that group",t.losses_with_unrecovered_deferred_same_bar)+'</div></div><div class="card"><b>Sampled post-entry price excursion</b><div class="grid" style="margin-top:12px">'+card("Positions with samples",e.positions_with_price_samples)+card("Sampled MFE ≥ activation",e.positions_with_mfe_at_least_activation)+card("MAE > MFE",e.positions_with_mae_greater_than_mfe)+'</div><small>Sampled price observations only; not tick-complete.</small></div>';
$("trades").innerHTML=d.trades.map(r=>'<tr><td>'+esc(r.close_day_utc)+'</td><td>'+esc(r.position_id)+'</td><td>'+esc(r.side)+'</td><td class="'+(r.net>0?"green":r.net<0?"red":"")+'">'+f(r.net)+'</td><td>'+f(r.sampled_mfe_price)+'</td><td>'+f(r.sampled_mae_price)+'</td><td>'+r.price_sample_count+'</td><td>'+r.trail_success+'</td><td>'+r.trail_failed+'</td><td>'+r.trail_deferred+'</td><td>'+r.trail_deferred_unrecovered_same_bar+'</td><td>'+esc(r.trail_evidence)+'</td></tr>').join("")||'<tr><td colspan="12">No closed position groups found for selected dates.</td></tr>';
$("limits").innerHTML=d.data_limits.map(x=>'<li>'+esc(x)+'</li>').join("")}
async function load(){try{const q=new URLSearchParams({start:$("start").value,end:$("end").value});const r=await fetch("/api/diagnostics?"+q,{cache:"no-store"});const d=await r.json();if(!r.ok)throw Error(d.error||r.status);render(d)}catch(e){$("status").textContent="Error: "+e.message}}
$("load").addEventListener("click",load);load();
</script></body></html>"""


@APP.get("/")
def index():
    return Response(HTML, mimetype="text/html")


def main():
    print(f"SP2L Performance Diagnostics: http://127.0.0.1:{PORT}", flush=True)
    APP.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
