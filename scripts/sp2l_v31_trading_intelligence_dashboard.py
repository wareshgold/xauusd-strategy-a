"""SP2L V3.1 Trading Intelligence Dashboard.

Read-only presentation layer over the existing V3.1 monitor's filesystem evidence.
No MetaTrader5 import, terminal lifecycle calls, order APIs, or Runner writes.
This dashboard distinguishes last-observed snapshots from verified live inventory.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import os

from flask import Flask, jsonify, Response

import sp2l_v31_local_monitoring_dashboard_v3 as ops

APP = Flask(__name__)
PORT = int(os.getenv("SP2L_INTELLIGENCE_PORT", "8795"))
REFRESH_SECONDS = 10

# MetaTrader 5 ENUM_DEAL_ENTRY identifiers. Unknown values remain explicitly unknown.
DEAL_ENTRY_LABELS = {0: "IN", 1: "OUT", 2: "INOUT", 3: "OUT_BY"}
POSITION_TYPE_LABELS = {0: "BUY", 1: "SELL"}


def _number(value):
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _deal_rows(events: list[dict]) -> list[dict]:
    unique = {}
    for event in events:
        if event.get("event") != "TELEGRAM_DEAL_LIFECYCLE":
            continue
        deal_id = event.get("deal")
        if deal_id is None:
            continue
        unique.setdefault(str(deal_id), event)

    rows = []
    for deal_id, event in unique.items():
        stamp = ops._stamp(event)
        entry_code = event.get("entry")
        try:
            entry_code = int(entry_code) if entry_code is not None else None
        except (TypeError, ValueError):
            entry_code = None
        signal_id = event.get("signal_id")
        side = None
        if isinstance(signal_id, str):
            suffix = signal_id.rsplit(":", 1)[-1].upper()
            if suffix in ("BUY", "SELL"):
                side = suffix
        rows.append({
            "deal_id": deal_id,
            "position_id": str(event.get("position") or ""),
            "order_id": str(event.get("order") or ""),
            "signal_id": signal_id,
            "side": side,
            "entry_code": entry_code,
            "entry_label": DEAL_ENTRY_LABELS.get(entry_code, f"UNKNOWN({entry_code})"),
            "entry_price": _number(event.get("entry_price")),
            "exit_price": _number(event.get("exit_price")),
            "profit": _number(event.get("profit")),
            "commission": _number(event.get("commission")),
            "swap": _number(event.get("swap")),
            "net": _number(event.get("net")),
            "reason_code": event.get("reason"),
            "time_utc": event.get("ts_utc"),
            "time_local": ops._tehran_time(event),
            "telegram_delivered": (
                event.get("telegram", {}).get("success")
                if isinstance(event.get("telegram"), dict) else None
            ),
            "theoretical_entry": _number(event.get("theoretical_entry")),
            "theoretical_sl": _number(event.get("theoretical_sl")),
            "theoretical_tp": _number(event.get("theoretical_tp")),
            "canonical": event.get("canonical"),
        })
    rows.sort(key=lambda row: row.get("time_utc") or "")
    return rows


def _position_journal(deals: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for deal in deals:
        if deal["position_id"]:
            grouped[deal["position_id"]].append(deal)

    rows = []
    for position_id, items in grouped.items():
        items.sort(key=lambda row: row.get("time_utc") or "")
        entries = [x for x in items if x["entry_code"] == 0]
        exits = [x for x in items if x["entry_code"] in (1, 3)]
        reversals = [x for x in items if x["entry_code"] == 2]
        known_nets = [x["net"] for x in items if x["net"] is not None]
        sides = list(dict.fromkeys(x["side"] for x in items if x["side"]))
        rows.append({
            "position_id": position_id,
            "side": sides[-1] if sides else "—",
            "signal_id": next((x.get("signal_id") for x in items if x.get("signal_id")), None),
            "first_time": items[0]["time_local"],
            "last_time": items[-1]["time_local"],
            "deal_count": len(items),
            "entry_deals": len(entries),
            "exit_deals": len(exits),
            "reversal_deals": len(reversals),
            "observed_net": round(sum(known_nets), 2) if known_nets else None,
            "status": (
                "EXIT_OBSERVED" if exits else
                "REVERSAL_OBSERVED" if reversals else
                "ENTRY_ONLY" if entries else "ENTRY_TYPE_UNKNOWN"
            ),
            "deals": items,
        })
    rows.sort(key=lambda row: row["last_time"], reverse=True)
    return rows


def _position_snapshots(events: list[dict], journal: list[dict]) -> list[dict]:
    latest = {}
    for event in events:
        if event.get("event") != "POSITION_LIFECYCLE" or event.get("position") is None:
            continue
        key = str(event["position"])
        stamp = ops._stamp(event)
        if key not in latest or (stamp and (ops._stamp(latest[key]) is None or stamp >= ops._stamp(latest[key]))):
            latest[key] = event

    journal_by_id = {row["position_id"]: row for row in journal}
    rows = []
    for key, event in latest.items():
        stamp = ops._stamp(event)
        rows.append({
            "position_id": key,
            "side": POSITION_TYPE_LABELS.get(event.get("type"), f"TYPE_{event.get('type')}"),
            "volume": _number(event.get("volume")),
            "entry_price": _number(event.get("price_open")),
            "last_price": _number(event.get("price_current")),
            "sl": _number(event.get("sl")),
            "tp": _number(event.get("tp")),
            "profit_snapshot": _number(event.get("profit")),
            "time_local": ops._tehran_time(event),
            "time_utc": event.get("ts_utc"),
            "observed_age_seconds": (
                max(0, (datetime.now(timezone.utc) - stamp).total_seconds()) if stamp else None
            ),
            "journal_status": journal_by_id.get(key, {}).get("status", "NO_DEAL_LINK"),
            "source": "POSITION_LIFECYCLE event; last observation only",
        })
    rows.sort(key=lambda row: row.get("time_utc") or "", reverse=True)
    return rows


def _order_journal(events: list[dict], state: dict) -> list[dict]:
    grouped = defaultdict(list)
    for event in events:
        result = event.get("result") if isinstance(event.get("result"), dict) else {}
        order_id = event.get("order") or event.get("tracked_order") or event.get("ticket") or result.get("order")
        if order_id not in (None, "", 0, "0"):
            grouped[str(order_id)].append(event)

    orders = state.get("orders", []) if isinstance(state, dict) else []
    if isinstance(orders, dict):
        orders = list(orders.values())
    if isinstance(orders, list):
        for item in orders:
            if not isinstance(item, dict):
                continue
            order_id = next((item.get(k) for k in ("ticket", "order", "order_id", "tracked_order")
                             if item.get(k) not in (None, "", 0, "0")), None)
            if order_id is not None:
                grouped.setdefault(str(order_id), [])

    rows = []
    for order_id, items in grouped.items():
        items.sort(key=lambda e: ops._stamp(e) or datetime.min.replace(tzinfo=timezone.utc))
        last = items[-1] if items else {}
        lifecycle = next((e for e in reversed(items) if e.get("event") == "PENDING_ORDER_LIFECYCLE"), None)
        result = last.get("result") if isinstance(last.get("result"), dict) else {}
        rows.append({
            "order_id": order_id,
            "status": (lifecycle or {}).get("state") or last.get("state") or last.get("event") or "RECORDED_ONLY",
            "last_event": last.get("event", "STATE_ONLY"),
            "last_time": ops._tehran_time(last) if last else "—",
            "symbol": last.get("symbol", "XAUUSD.ecn"),
            "position_id": (lifecycle or {}).get("position_id") or last.get("position"),
            "volume_initial": (lifecycle or {}).get("volume_initial"),
            "volume_current": (lifecycle or {}).get("volume_current"),
            "price": (lifecycle or {}).get("price_open"),
            "sl": (lifecycle or {}).get("sl"),
            "tp": (lifecycle or {}).get("tp"),
            "retcode": result.get("retcode", last.get("retcode")),
            "event_count": len(items),
            "event_types": [e.get("event") for e in items],
        })
    rows.sort(key=lambda row: row["last_time"], reverse=True)
    return rows


def _performance(deals: list[dict]) -> dict:
    # This is a cumulative sum of Runner-recorded deal-net fields, not account equity.
    running = 0.0
    curve = []
    daily = defaultdict(float)
    gross_positive = 0.0
    gross_negative = 0.0
    positive = negative = 0
    for row in deals:
        net = row["net"]
        if net is None:
            continue
        running += net
        curve.append({"time": row["time_local"], "net": round(net, 2), "cumulative": round(running, 2)})
        day = (row.get("time_utc") or "")[:10]
        if day:
            daily[day] += net
        if net > 0:
            positive += 1
            gross_positive += net
        elif net < 0:
            negative += 1
            gross_negative += abs(net)
    return {
        "deal_count": len(deals),
        "net_sum": round(sum(x["net"] for x in deals if x["net"] is not None), 2),
        "positive_deals": positive,
        "negative_deals": negative,
        "gross_positive_deal_net": round(gross_positive, 2),
        "gross_negative_deal_net": round(gross_negative, 2),
        "daily": [{"date": day, "net": round(value, 2)} for day, value in sorted(daily.items())],
        "curve": curve,
        "metric_label": "Cumulative Runner-recorded deal net; not account equity or a validated trade-level backtest",
    }


def _payload() -> dict:
    snap = ops._snapshot()
    deals = _deal_rows(snap["events"])
    journal = _position_journal(deals)
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "runner": snap["runner"],
        "state_age_seconds": snap["state_age_seconds"],
        "event_meta": snap["event_meta"],
        "event_health": snap["health"],
        "diagnostics": snap["diagnostics"],
        "latest_event": snap["latest"],
        "metrics": snap["metrics"],
        "deals": deals,
        "positions": _position_snapshots(snap["events"], journal),
        "journal": journal,
        "orders": _order_journal(snap["events"], snap["state"]),
        "performance": _performance(deals),
        "signals": {
            "signals": sum(e.get("event") == "TELEGRAM_SIGNAL" for e in snap["events"]),
            "order_attempts": sum(e.get("event") == "ORDER_ATTEMPT" for e in snap["events"]),
            "order_results": sum(e.get("event") == "ORDER_RESULT" for e in snap["events"]),
            "execution_blocked": sum(e.get("event") == "EXECUTION_BLOCKED" for e in snap["events"]),
        },
        "broker_state_verified": False,
        "mt5_queried": False,
    }


@APP.get("/api/dashboard")
def api_dashboard():
    return jsonify(_payload())


@APP.get("/api/health")
def api_health():
    data = _payload()
    return jsonify({
        "runner": data["runner"],
        "state_age_seconds": data["state_age_seconds"],
        "event_meta": data["event_meta"],
        "event_health": data["event_health"],
        "mt5_queried": False,
        "broker_state_verified": False,
    })


HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SP2L Trading Intelligence</title>
<style>
:root{color-scheme:dark;--bg:#0b1220;--side:#0e1929;--panel:#121f31;--panel2:#17263a;--line:#2a3b52;--text:#edf3fb;--muted:#9eafc4;--blue:#8dbdff;--green:#5bd6a4;--red:#ff8294;--amber:#f2c66d}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px Inter,Segoe UI,Arial,sans-serif}
.app{display:grid;grid-template-columns:230px minmax(0,1fr);min-height:100vh}.side{background:var(--side);border-right:1px solid var(--line);padding:22px 14px;position:sticky;top:0;height:100vh}
.brand{font-size:17px;font-weight:800;letter-spacing:.3px;padding:4px 10px 24px}.brand small{display:block;color:var(--muted);font-size:10px;font-weight:500;margin-top:5px;letter-spacing:1.2px}
.nav{display:grid;gap:6px}.nav button{background:transparent;border:0;color:var(--muted);text-align:left;padding:12px;border-radius:9px;cursor:pointer;font-size:13px}.nav button.active,.nav button:hover{background:var(--panel2);color:var(--text)}.nav button span{display:inline-block;width:26px;color:var(--blue)}
.sidefoot{position:absolute;bottom:18px;left:22px;right:18px;color:var(--muted);font-size:11px;line-height:1.6}
main{min-width:0;padding:25px 30px 40px;max-width:1700px;width:100%;margin:0 auto}
.top{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:22px}.eyebrow{font-size:10px;letter-spacing:1.6px;color:var(--blue);font-weight:700}.top h1{font-size:25px;margin:6px 0}.sub{color:var(--muted);font-size:12px}.status{border:1px solid var(--line);border-radius:30px;padding:9px 13px;font-size:11px;font-weight:800}
.page{display:none}.page.active{display:block}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.card{background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:16px;min-width:0}.kpi-label{color:var(--muted);font-size:11px}.kpi-value{font-size:25px;font-weight:750;margin-top:8px;overflow-wrap:anywhere}.kpi-note{color:var(--muted);font-size:10px;margin-top:7px}.green{color:var(--green)}.red{color:var(--red)}.amber{color:var(--amber)}.muted{color:var(--muted)}
.section-head{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:22px 0 11px}.section-head h2{font-size:15px;margin:0}.section-head p{font-size:11px;color:var(--muted);margin:4px 0 0}
.split{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(260px,1fr);gap:12px;margin-top:12px}.chartbox{height:265px;position:relative}.chartbox svg{width:100%;height:100%;overflow:visible}.chartlabel{font-size:10px;fill:var(--muted)}
table{border-collapse:collapse;width:100%;font-size:12px;white-space:nowrap}th{text-align:left;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.6px;font-weight:650;padding:11px 10px;border-bottom:1px solid var(--line)}td{padding:12px 10px;border-bottom:1px solid rgba(42,59,82,.65)}tr.data-row{cursor:pointer}tr.data-row:hover{background:var(--panel2)}.tablewrap{overflow:auto;max-height:570px}
.pill{display:inline-block;border:1px solid var(--line);border-radius:20px;padding:4px 8px;font-size:10px;color:var(--muted)}.pill.good{color:var(--green);border-color:#28674f}.pill.warn{color:var(--amber);border-color:#66552e}.pill.bad{color:var(--red);border-color:#713746}
.toolbar{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.toolbar input,.toolbar select{background:var(--side);border:1px solid var(--line);color:var(--text);padding:10px;border-radius:8px;min-width:150px}
.detail{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:14px;margin-top:12px;display:none}.detail.show{display:block}.detail-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.detail-item small{display:block;color:var(--muted);font-size:10px}.detail-item b{display:block;margin-top:5px;overflow-wrap:anywhere}
.notice{padding:11px 13px;background:#18263a;border:1px solid var(--line);border-left:3px solid var(--amber);border-radius:8px;color:var(--muted);font-size:11px;line-height:1.6;margin:12px 0}
.empty{padding:30px;text-align:center;color:var(--muted)}.refresh{background:var(--panel2);border:1px solid var(--line);border-radius:8px;color:var(--text);padding:8px 11px;cursor:pointer}
@media(max-width:1050px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.split{grid-template-columns:1fr}}
@media(max-width:700px){.app{grid-template-columns:1fr}.side{height:auto;position:static;padding:12px}.brand{padding:4px 8px 12px}.nav{display:flex;overflow:auto}.nav button{white-space:nowrap;padding:9px}.sidefoot{display:none}main{padding:16px}.top h1{font-size:21px}.detail-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style></head><body>
<div class="app">
<aside class="side"><div class="brand">SP2L <span style="color:var(--blue)">/</span> INTELLIGENCE<small>V3.1 · XAUUSD FORWARD</small></div>
<nav class="nav">
<button class="active" data-page="overview"><span>◫</span>Overview</button>
<button data-page="positions"><span>◎</span>Positions & Orders</button>
<button data-page="journal"><span>▤</span>Deal Journal</button>
<button data-page="performance"><span>⌁</span>Performance</button>
<button data-page="execution"><span>⌘</span>Execution & Risk</button>
<button data-page="evidence"><span>◈</span>Evidence & Health</button>
</nav>
<div class="sidefoot">Read-only observer<br>Runner evidence · no MT5 session access<br><span id="last-refresh">Waiting for data…</span></div></aside>
<main>
<header class="top"><div><div class="eyebrow">FORWARD OPERATIONS CENTER</div><h1 id="page-title">Overview</h1><div class="sub">Research monitoring · Runner-recorded evidence · Tehran time</div></div><div style="display:flex;align-items:center;gap:9px"><div id="runner-status" class="status">Checking Runner…</div><button id="refresh" class="refresh">Refresh ↻</button></div></header>

<section class="page active" id="page-overview">
<div class="grid">
<div class="card"><div class="kpi-label">Recorded deal net</div><div class="kpi-value" id="k-net">—</div><div class="kpi-note">Sum of unique lifecycle deal events</div></div>
<div class="card"><div class="kpi-label">Deal records</div><div class="kpi-value" id="k-deals">—</div><div class="kpi-note">Unique deal IDs in readable event window</div></div>
<div class="card"><div class="kpi-label">Position groups</div><div class="kpi-value" id="k-positions">—</div><div class="kpi-note">Grouped by position identifier</div></div>
<div class="card"><div class="kpi-label">Runner process</div><div class="kpi-value" id="k-runner">—</div><div class="kpi-note" id="k-state-age">State freshness —</div></div>
</div>
<div class="split">
<div class="card"><div class="section-head" style="margin:0 0 8px"><div><h2>Recorded deal-net curve</h2><p>Running sum of deal net fields · not account equity</p></div><span class="pill" id="curve-count">0 points</span></div><div class="chartbox"><svg id="curve" viewBox="0 0 800 250" role="img" aria-label="Cumulative recorded deal net"></svg></div></div>
<div class="card"><div class="section-head" style="margin:0 0 8px"><div><h2>Signal & execution funnel</h2><p>Counts from Runner events; not conversion rates</p></div></div><div id="funnel"></div></div>
</div>
<div class="section-head"><div><h2>Latest position observations</h2><p>Last recorded snapshots, not confirmed current open positions</p></div><button class="refresh" data-goto="positions">View all</button></div>
<div class="card tablewrap"><table><thead><tr><th>Position</th><th>Side</th><th>Volume</th><th>Entry</th><th>Last price</th><th>SL</th><th>TP</th><th>Observed</th></tr></thead><tbody id="overview-positions"></tbody></table></div>
<div class="section-head"><div><h2>Latest alerts</h2><p>Warnings and errors in the readable event window</p></div><button class="refresh" data-goto="execution">Inspect</button></div>
<div class="card" id="overview-alerts"></div>
</section>

<section class="page" id="page-positions">
<div class="notice">The Runner's POSITION_LIFECYCLE and PENDING_ORDER_LIFECYCLE events are snapshots. They are not a live broker inventory query. A stale snapshot must not be interpreted as an open position or active pending order.</div>
<div class="section-head"><div><h2>Position snapshots</h2><p>Latest observed broker values recorded by the Runner</p></div></div>
<div class="card tablewrap"><table><thead><tr><th>Position</th><th>Side</th><th>Volume</th><th>Entry</th><th>Last price</th><th>SL</th><th>TP</th><th>Profit snapshot</th><th>Age</th><th>Journal status</th></tr></thead><tbody id="positions-table"></tbody></table></div>
<div class="section-head"><div><h2>Pending order lifecycle</h2><p>Last Runner-recorded status per order identifier</p></div></div>
<div class="card tablewrap"><table><thead><tr><th>Order</th><th>Status</th><th>Last event</th><th>Time</th><th>Position</th><th>Volume</th><th>Price</th><th>SL</th><th>TP</th><th>Retcode</th></tr></thead><tbody id="orders-table"></tbody></table></div>
</section>

<section class="page" id="page-journal">
<div class="toolbar"><input id="journal-search" placeholder="Search position, signal, deal…"><select id="journal-status"><option value="">All recorded states</option><option>EXIT_OBSERVED</option><option>REVERSAL_OBSERVED</option><option>ENTRY_ONLY</option><option>ENTRY_TYPE_UNKNOWN</option></select></div>
<div class="card tablewrap"><table><thead><tr><th>Position</th><th>Side</th><th>Signal ID</th><th>First seen</th><th>Last seen</th><th>Deals</th><th>IN</th><th>OUT</th><th>Net sum</th><th>Evidence status</th></tr></thead><tbody id="journal-table"></tbody></table></div>
<div class="detail" id="journal-detail"><div class="section-head" style="margin:0 0 8px"><h2 id="detail-title">Position detail</h2><span class="pill">Runner deal events</span></div><div class="detail-grid" id="detail-grid"></div><div class="tablewrap" style="margin-top:12px"><table><thead><tr><th>Time</th><th>Deal</th><th>Entry code</th><th>Entry price</th><th>Exit price</th><th>Profit</th><th>Commission</th><th>Swap</th><th>Net</th></tr></thead><tbody id="detail-deals"></tbody></table></div></div>
</section>

<section class="page" id="page-performance">
<div class="notice">These figures summarize unique Runner-recorded deal events. They are not a broker-reconciled account statement, trade-level expectancy, R-multiple analysis, or validated strategy backtest. Partial exits and reversals remain separately visible in the journal.</div>
<div class="grid">
<div class="card"><div class="kpi-label">Recorded deal net sum</div><div class="kpi-value" id="p-net">—</div></div>
<div class="card"><div class="kpi-label">Positive deal records</div><div class="kpi-value" id="p-positive">—</div></div>
<div class="card"><div class="kpi-label">Negative deal records</div><div class="kpi-value" id="p-negative">—</div></div>
<div class="card"><div class="kpi-label">Gross positive / negative</div><div class="kpi-value" id="p-gross" style="font-size:18px">—</div></div>
</div>
<div class="section-head"><div><h2>Daily recorded deal net</h2><p>Daily aggregation of deal-net events by UTC event date</p></div></div>
<div class="card tablewrap"><table><thead><tr><th>Date UTC</th><th>Recorded deal net</th></tr></thead><tbody id="daily-table"></tbody></table></div>
</section>

<section class="page" id="page-execution">
<div class="grid">
<div class="card"><div class="kpi-label">Signal events</div><div class="kpi-value" id="s-signals">—</div></div>
<div class="card"><div class="kpi-label">Order attempts</div><div class="kpi-value" id="s-attempts">—</div></div>
<div class="card"><div class="kpi-label">Order result events</div><div class="kpi-value" id="s-results">—</div></div>
<div class="card"><div class="kpi-label">Execution blocked</div><div class="kpi-value" id="s-blocked">—</div></div>
</div>
<div class="section-head"><div><h2>Diagnostics</h2><p>Correlated Runner observations; classification does not change Runner behavior</p></div></div>
<div class="card tablewrap"><table><thead><tr><th>Level</th><th>Time</th><th>Code</th><th>Message</th><th>Detail</th></tr></thead><tbody id="diagnostics-table"></tbody></table></div>
</section>

<section class="page" id="page-evidence">
<div class="grid">
<div class="card"><div class="kpi-label">Runner</div><div class="kpi-value" id="e-runner">—</div><div class="kpi-note" id="e-pids">—</div></div>
<div class="card"><div class="kpi-label">Event records</div><div class="kpi-value" id="e-events">—</div><div class="kpi-note" id="e-malformed">—</div></div>
<div class="card"><div class="kpi-label">Event file</div><div class="kpi-value" id="e-bytes">—</div><div class="kpi-note" id="e-age">—</div></div>
<div class="card"><div class="kpi-label">State file</div><div class="kpi-value" id="e-state">—</div><div class="kpi-note" id="e-state-age">—</div></div>
</div>
<div class="notice">This application does not import MetaTrader5 or query, initialize, or shut down the terminal. Broker reconciliation is intentionally false. SHA-256 fingerprints remain available in the separate read-only Ops dashboard.</div>
<div class="card"><div class="section-head" style="margin:0"><h2>Data provenance</h2></div><div id="provenance" class="muted" style="line-height:1.9;font-size:12px"></div></div>
</section>
</main></div>
<script>
let DATA=null;
const $=id=>document.getElementById(id);
const fmt=(v,d=2)=>v===null||v===undefined||v===""?"—":Number(v).toFixed(d);
const esc=v=>String(v??"—").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function pill(status){let cls=status==="EXIT_OBSERVED"?"good":status==="ENTRY_ONLY"?"warn":"";
return '<span class="pill '+cls+'">'+esc(status)+'</span>'}
function nav(page){document.querySelectorAll(".nav button").forEach(b=>b.classList.toggle("active",b.dataset.page===page));
document.querySelectorAll(".page").forEach(p=>p.classList.toggle("active",p.id==="page-"+page));
$("page-title").textContent=({overview:"Overview",positions:"Positions & Orders",journal:"Deal Journal",performance:"Performance",execution:"Execution & Risk",evidence:"Evidence & Health"})[page]||page}
document.querySelectorAll(".nav button").forEach(b=>b.addEventListener("click",()=>nav(b.dataset.page)));
document.querySelectorAll("[data-goto]").forEach(b=>b.addEventListener("click",()=>nav(b.dataset.goto)));
function drawCurve(points){const svg=$("curve");svg.replaceChildren();$("curve-count").textContent=points.length+" points";
if(!points.length){svg.innerHTML='<text x="400" y="125" text-anchor="middle" class="chartlabel">No deal-net observations yet</text>';return}
const ns="http://www.w3.org/2000/svg",W=800,H=250,L=42,R=18,T=18,B=30;
const vals=points.map(p=>p.cumulative),min=Math.min(0,...vals),max=Math.max(0,...vals),span=max-min||1;
const x=i=>L+(points.length===1?0:i*(W-L-R)/(points.length-1)),y=v=>T+(max-v)*(H-T-B)/span;
const line=document.createElementNS(ns,"polyline");line.setAttribute("fill","none");line.setAttribute("stroke","#8dbdff");line.setAttribute("stroke-width","3");line.setAttribute("stroke-linejoin","round");line.setAttribute("points",points.map((p,i)=>x(i)+","+y(p.cumulative)).join(" "));svg.appendChild(line);
[0,.25,.5,.75,1].forEach(fr=>{const v=max-(max-min)*fr,yy=y(v),g=document.createElementNS(ns,"g"),ln=document.createElementNS(ns,"line"),tx=document.createElementNS(ns,"text");ln.setAttribute("x1",L);ln.setAttribute("x2",W-R);ln.setAttribute("y1",yy);ln.setAttribute("y2",yy);ln.setAttribute("stroke","#2a3b52");ln.setAttribute("stroke-dasharray","4 5");tx.setAttribute("x",L-8);tx.setAttribute("y",yy+3);tx.setAttribute("text-anchor","end");tx.setAttribute("class","chartlabel");tx.textContent=v.toFixed(2);g.append(ln,tx);svg.appendChild(g)});
}
function renderJournal(){const q=$("journal-search").value.toLowerCase(),s=$("journal-status").value;
const rows=DATA.journal.filter(r=>(!s||r.status===s)&&JSON.stringify(r).toLowerCase().includes(q));
$("journal-table").innerHTML=rows.map((r,i)=>'<tr class="data-row" data-journal="'+i+'"><td>'+esc(r.position_id)+'</td><td>'+esc(r.side)+'</td><td>'+esc(r.signal_id)+'</td><td>'+esc(r.first_time)+'</td><td>'+esc(r.last_time)+'</td><td>'+r.deal_count+'</td><td>'+r.entry_deals+'</td><td>'+r.exit_deals+'</td><td>'+fmt(r.observed_net)+'</td><td>'+pill(r.status)+'</td></tr>').join("")||'<tr><td colspan="10" class="empty">No matching position groups</td></tr>';
$("journal-table").querySelectorAll("[data-journal]").forEach(tr=>tr.addEventListener("click",()=>showDetail(rows[Number(tr.dataset.journal)])));
}
function showDetail(r){$("journal-detail").classList.add("show");$("detail-title").textContent="Position "+r.position_id;
const vals=[["Side",r.side],["Signal",r.signal_id],["Observed net",fmt(r.observed_net)],["Deal events",r.deal_count],["Entry events",r.entry_deals],["Exit events",r.exit_deals],["Reversal events",r.reversal_deals],["Evidence status",r.status]];
$("detail-grid").innerHTML=vals.map(v=>'<div class="detail-item"><small>'+esc(v[0])+'</small><b>'+esc(v[1])+'</b></div>').join("");
$("detail-deals").innerHTML=r.deals.map(d=>'<tr><td>'+esc(d.time_local)+'</td><td>'+esc(d.deal_id)+'</td><td>'+esc(d.entry_label)+'</td><td>'+fmt(d.entry_price,3)+'</td><td>'+fmt(d.exit_price,3)+'</td><td>'+fmt(d.profit)+'</td><td>'+fmt(d.commission)+'</td><td>'+fmt(d.swap)+'</td><td>'+fmt(d.net)+'</td></tr>').join("");
$("journal-detail").scrollIntoView({behavior:"smooth",block:"nearest"});
}
function render(d){DATA=d;
const runner=d.runner||{},alive=runner.alive===true;
$("runner-status").textContent=alive?"RUNNER ACTIVE":runner.alive===false?"RUNNER NOT FOUND":"RUNNER UNVERIFIED";
$("runner-status").className="status "+(alive?"green":runner.alive===false?"red":"amber");
$("k-net").textContent=fmt(d.performance.net_sum);$("k-net").className="kpi-value "+(d.performance.net_sum>=0?"green":"red");
$("k-deals").textContent=d.deals.length;$("k-positions").textContent=d.journal.length;$("k-runner").textContent=alive?"ACTIVE":runner.alive===false?"MISSING":"UNKNOWN";
$("k-state-age").textContent="State freshness "+fmt(d.state_age_seconds,0)+"s";
drawCurve(d.performance.curve);
const f=d.signals;$("funnel").innerHTML=[["Signal events",f.signals],["Order attempts",f.order_attempts],["Order results",f.order_results],["Execution blocked",f.execution_blocked]].map(x=>'<div style="display:flex;justify-content:space-between;padding:13px 2px;border-bottom:1px solid var(--line)"><span class="muted">'+x[0]+'</span><b>'+x[1]+'</b></div>').join("");
const pos=d.positions;
const posHtml=pos.slice(0,8).map(p=>'<tr><td>'+esc(p.position_id)+'</td><td>'+esc(p.side)+'</td><td>'+fmt(p.volume,2)+'</td><td>'+fmt(p.entry_price,3)+'</td><td>'+fmt(p.last_price,3)+'</td><td>'+fmt(p.sl,3)+'</td><td>'+fmt(p.tp,3)+'</td><td>'+fmt(p.observed_age_seconds,0)+'s</td></tr>').join("")||'<tr><td colspan="8" class="empty">No position snapshots recorded</td></tr>';
$("overview-positions").innerHTML=posHtml;
$("positions-table").innerHTML=pos.map(p=>'<tr><td>'+esc(p.position_id)+'</td><td>'+esc(p.side)+'</td><td>'+fmt(p.volume,2)+'</td><td>'+fmt(p.entry_price,3)+'</td><td>'+fmt(p.last_price,3)+'</td><td>'+fmt(p.sl,3)+'</td><td>'+fmt(p.tp,3)+'</td><td>'+fmt(p.profit_snapshot)+'</td><td>'+fmt(p.observed_age_seconds,0)+'s</td><td>'+pill(p.journal_status)+'</td></tr>').join("")||'<tr><td colspan="10" class="empty">No position snapshots recorded</td></tr>';
$("orders-table").innerHTML=d.orders.map(o=>'<tr><td>'+esc(o.order_id)+'</td><td>'+esc(o.status)+'</td><td>'+esc(o.last_event)+'</td><td>'+esc(o.last_time)+'</td><td>'+esc(o.position_id)+'</td><td>'+fmt(o.volume_current,2)+'</td><td>'+fmt(o.price,3)+'</td><td>'+fmt(o.sl,3)+'</td><td>'+fmt(o.tp,3)+'</td><td>'+esc(o.retcode)+'</td></tr>').join("")||'<tr><td colspan="10" class="empty">No order lifecycle events recorded</td></tr>';
$("overview-alerts").innerHTML=(d.diagnostics||[]).filter(x=>["ERROR","WARNING"].includes(x.level)).slice(-8).reverse().map(x=>'<div style="padding:10px 0;border-bottom:1px solid var(--line)"><span class="pill '+(x.level==="ERROR"?"bad":"warn")+'">'+esc(x.level)+'</span> <b>'+esc(x.code)+'</b><div class="muted" style="margin-top:5px">'+esc(x.message)+' · '+esc(x.time)+'</div></div>').join("")||'<div class="empty">No warning/error in current event window</div>';
renderJournal();
$("p-net").textContent=fmt(d.performance.net_sum);$("p-positive").textContent=d.performance.positive_deals;$("p-negative").textContent=d.performance.negative_deals;
$("p-gross").textContent=fmt(d.performance.gross_positive_deal_net)+" / -"+fmt(d.performance.gross_negative_deal_net);
$("daily-table").innerHTML=d.performance.daily.map(x=>'<tr><td>'+esc(x.date)+'</td><td>'+fmt(x.net)+'</td></tr>').join("")||'<tr><td colspan="2" class="empty">No daily data</td></tr>';
$("s-signals").textContent=f.signals;$("s-attempts").textContent=f.order_attempts;$("s-results").textContent=f.order_results;$("s-blocked").textContent=f.execution_blocked;
$("diagnostics-table").innerHTML=(d.diagnostics||[]).map(x=>'<tr><td><span class="pill '+(x.level==="ERROR"?"bad":x.level==="WARNING"?"warn":"")+'">'+esc(x.level)+'</span></td><td>'+esc(x.time)+'</td><td>'+esc(x.code)+'</td><td>'+esc(x.message)+'</td><td>'+esc(x.detail)+'</td></tr>').join("")||'<tr><td colspan="5" class="empty">No diagnostics</td></tr>';
$("e-runner").textContent=alive?"ACTIVE":runner.alive===false?"NOT FOUND":"UNKNOWN";$("e-pids").textContent="PID(s): "+(runner.pids||[]).join(", ");
$("e-events").textContent=d.event_health.total_lines;$("e-malformed").textContent="Malformed lines: "+d.event_health.malformed_lines;
$("e-bytes").textContent=d.event_meta.bytes??"—";$("e-age").textContent="Updated "+fmt(d.event_meta.age_seconds,0)+"s ago";
$("e-state").textContent=d.state_age_seconds===null?"UNAVAILABLE":"READABLE";$("e-state-age").textContent="Updated "+fmt(d.state_age_seconds,0)+"s ago";
$("provenance").innerHTML="Generated UTC: "+esc(d.generated_at_utc)+"<br>Event file: "+esc(d.event_health.path)+"<br>Event lines: "+esc(d.event_health.total_lines)+"<br>Malformed: "+esc(d.event_health.malformed_lines)+"<br>Runner process source: "+esc(runner.source)+"<br>MT5 queried: NO<br>Broker state verified: NO";
$("last-refresh").textContent="Updated "+new Date().toLocaleTimeString();
}
async function refresh(){try{const r=await fetch("/api/dashboard",{cache:"no-store"});if(!r.ok)throw Error("HTTP "+r.status);render(await r.json())}catch(e){$("runner-status").textContent="DATA ERROR: "+e.message;$("runner-status").className="status red"}}
$("refresh").addEventListener("click",refresh);$("journal-search").addEventListener("input",renderJournal);$("journal-status").addEventListener("change",renderJournal);
refresh();setInterval(refresh,10000);
</script></body></html>"""


@APP.get("/")
def index():
    return Response(HTML, mimetype="text/html")


def main():
    print(f"SP2L Trading Intelligence Dashboard: http://127.0.0.1:{PORT}", flush=True)
    APP.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
