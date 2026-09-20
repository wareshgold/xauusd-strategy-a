"""Deterministic SP2L report engine over the live journal.

Reporting/infrastructure only:
- does not define or modify SP2L geometry (P-Gap, AB=CD, Leg1/Leg2, fill
  semantics, entry/SL/TP rules);
- does not generate trading signals and does not enable live trading;
- every number is derived from recorded journal rows plus explicit
  configuration; nothing is inferred from broker data.

Determinism contract:
- Aggregation functions are pure: (journal records, period bounds, explicit
  configuration) -> report dict. No wall-clock reads inside the engine.
- Rows are sorted by a stable key before any fold/aggregation, so record
  order in the JSONL files cannot change results.
- Floats are rounded at the schema boundary only (R: 4 decimals, pips: 2).
- Missing inputs produce None/n-a values, never invented substitutes.

Reporting classification (not strategy semantics):
- WIN/LOSS come from journal records already written by the gateway or the
  MT5 reconciliation process (`result` field on CLOSED trade records).
- AMBIGUOUS means the journal does not deterministically resolve the
  outcome (no CLOSED record, or CLOSED with a result that is not
  WIN/LOSS). It is a journal-state label, not a fill-semantics decision.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "sp2l.live_report.v1"

# Env-var defaults. These are echoes of configuration, not new rules.
DEFAULT_GEOMETRY_STATUS = "UNRESOLVED_FROZEN_GEOMETRY_GATE"

_R_DP = 4
_PIPS_DP = 2


@dataclass(frozen=True)
class ReportConfig:
    """Explicit configuration for one report build.

    geometry_status / live_trading_enabled are echoed verbatim into the
    System section; the engine never decides them.
    pip_size: XAUUSD price units per pip. Repository convention
    (scripts/calculate-sp2l-pl-pip-accounting.py) requires the pip size to
    be supplied explicitly and never inferred. When None, net pips are
    reported as None with basis NOT_CONFIGURED.
    session_timezone: IANA name used only to group breakdown rows; falls
    back to canonical UTC day keys when the zone database is unavailable.
    """

    geometry_status: str = DEFAULT_GEOMETRY_STATUS
    live_trading_enabled: bool = False
    pip_size: float | None = None
    session_timezone: str = "America/New_York"
    journal_source: str = "runtime/journal"
    period_basis: str = "EXPLICIT_PERIOD_BOUNDS"


def load_report_config(env: dict | None = None) -> ReportConfig:
    import os

    source = os.environ if env is None else env
    pip_raw = (source.get("REPORT_PIP_SIZE") or "").strip()
    pip_size = float(pip_raw) if pip_raw else None
    return ReportConfig(
        geometry_status=(source.get("SP2L_GEOMETRY_STATUS") or DEFAULT_GEOMETRY_STATUS).strip(),
        live_trading_enabled=(source.get("LIVE_TRADING_ENABLE", "false").lower() == "true"),
        pip_size=pip_size,
        session_timezone=(source.get("REPORT_SESSION_TIMEZONE") or "America/New_York").strip(),
        period_basis=(source.get("REPORT_PERIOD_BASIS") or "EXPLICIT_PERIOD_BOUNDS").strip(),
    )


# ---------------------------------------------------------------------------
# Record parsing helpers
# ---------------------------------------------------------------------------

_TS_KEYS = ("closed_at_utc", "execution_timestamp_utc", "timestamp_utc", "recorded_at_utc")


def record_timestamp_utc(row: dict[str, Any]) -> datetime | None:
    """Resolve a record's canonical UTC timestamp.

    Fallback chain (documented): closed_at_utc -> execution_timestamp_utc ->
    timestamp_utc -> recorded_at_utc. Rows without any parsable timestamp
    are excluded from period metrics and counted as unclassified.
    """
    for key in _TS_KEYS:
        raw = row.get(key)
        if raw is None:
            continue
        try:
            parsed = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    return None


def _in_period(row: dict[str, Any], start: datetime, end: datetime) -> bool:
    ts = record_timestamp_utc(row)
    if ts is None:
        return False
    return start <= ts < end


def _sort_key(row: dict[str, Any]) -> tuple:
    ts = record_timestamp_utc(row)
    return (
        ts.isoformat() if ts else "",
        str(row.get("signal_id", "")),
        str(row.get("deal_id", "")),
    )


def _round(value: float | None, digits: int) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


# ---------------------------------------------------------------------------
# Journal loading
# ---------------------------------------------------------------------------


def load_journal(journal_dir: Path):
    """Read signals/trades JSONL via the existing live_journal module."""
    try:
        from live_journal import read_jsonl
    except ModuleNotFoundError:
        from scripts.live_journal import read_jsonl

    signals = read_jsonl(Path(journal_dir) / "signals.jsonl")
    trades = read_jsonl(Path(journal_dir) / "trades.jsonl")
    return signals, trades


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def _signal_id(row: dict[str, Any]) -> str | None:
    value = row.get("signal_id")
    return str(value) if value is not None else None


def classify_signals(signals: list[dict], trades: list[dict]) -> dict[str, int]:
    """Reporting-only classification of journal signal records.

    - duplicates_rejected: signal rows already recorded as DUPLICATE_REJECTED.
    - For each accepted signal, outcome is WIN/LOSS when a CLOSED trade with
      that result exists; otherwise AMBIGUOUS (journal state unresolved).
    """
    trades_by_signal: dict[str, list[dict]] = {}
    for trade in trades:
        sid = _signal_id(trade)
        if sid is not None:
            trades_by_signal.setdefault(sid, []).append(trade)

    wins = losses = ambiguous = duplicates = 0
    for signal in signals:
        status = str(signal.get("status", "")).upper()
        if status == "DUPLICATE_REJECTED":
            duplicates += 1
            continue
        sid = _signal_id(signal)
        closed = [
            t for t in trades_by_signal.get(sid, [])
            if str(t.get("status", "")).upper() == "CLOSED"
        ]
        results = {str(t.get("result", "")).upper() for t in closed}
        if "WIN" in results:
            wins += 1
        elif "LOSS" in results:
            losses += 1
        else:
            ambiguous += 1

    return {
        "total": wins + losses + ambiguous,
        "win": wins,
        "loss": losses,
        "ambiguous": ambiguous,
        "duplicates_rejected": duplicates,
    }


# ---------------------------------------------------------------------------
# Performance metrics (R-basis; pips only with explicit pip size)
# ---------------------------------------------------------------------------


def _closed_trades(trades: list[dict]) -> list[dict]:
    return sorted(
        (t for t in trades if str(t.get("status", "")).upper() == "CLOSED"),
        key=_sort_key,
    )


def _trade_r(row: dict[str, Any]) -> float | None:
    value = row.get("r_multiple")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _trade_pips(row: dict[str, Any], pip_size: float | None) -> float | None:
    if pip_size is None or pip_size <= 0:
        return None
    entry = row.get("signal_entry")
    exit_price = row.get("broker_price")
    direction = str(row.get("direction", "")).upper()
    if entry is None or exit_price is None or direction not in {"BUY", "SELL"}:
        return None
    move = (float(exit_price) - float(entry)) if direction == "BUY" else (float(entry) - float(exit_price))
    return move / pip_size


def performance_metrics(closed: list[dict], pip_size: float | None) -> dict[str, Any]:
    """Deterministic R-basis metrics over sorted CLOSED trade records.

    Max drawdown: peak-to-trough on the cumulative-R curve that starts at 0
    and folds the sorted R sequence. Reporting statistic only.
    """
    r_values = [r for r in (_trade_r(t) for t in closed) if r is not None]
    missing_r = len(closed) - len(r_values)

    wins = sum(1 for t in closed if str(t.get("result", "")).upper() == "WIN")
    losses = sum(1 for t in closed if str(t.get("result", "")).upper() == "LOSS")

    net_r = sum(r_values)
    positive_r = sum(r for r in r_values if r > 0.0)
    negative_r = -sum(r for r in r_values if r < 0.0)

    cumulative = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for r in r_values:
        cumulative += r
        peak = max(peak, cumulative)
        max_drawdown = max(max_drawdown, peak - cumulative)

    pips_values = [p for p in (_trade_pips(t, pip_size) for t in closed) if p is not None]

    return {
        "net_pips": _round(sum(pips_values), _PIPS_DP) if pips_values else None,
        "net_r": _round(net_r, _R_DP),
        "profit_factor": _round(positive_r / negative_r, _R_DP) if negative_r > 0.0 else None,
        "win_rate_pct": _round(100.0 * wins / (wins + losses), 2) if (wins + losses) else None,
        "max_drawdown_r": _round(max_drawdown, _R_DP),
        "closed_with_r": len(r_values),
        "closed_missing_r": missing_r,
        "pips_basis": "EXPLICIT_PIP_SIZE" if (pip_size is not None and pip_size > 0) else "NOT_CONFIGURED",
    }


def equity_summary(closed: list[dict]) -> dict[str, Any]:
    """R-basis equity curve summary (start 0, fold sorted R sequence)."""
    r_values = [r for r in (_trade_r(t) for t in closed) if r is not None]
    cumulative = 0.0
    peak = 0.0
    trough = 0.0
    max_drawdown = 0.0
    for r in r_values:
        cumulative += r
        peak = max(peak, cumulative)
        trough = min(trough, cumulative)
        max_drawdown = max(max_drawdown, peak - cumulative)
    return {
        "equity_start_r": 0.0,
        "equity_end_r": _round(cumulative, _R_DP),
        "equity_peak_r": _round(peak, _R_DP),
        "equity_trough_r": _round(trough, _R_DP),
        "max_drawdown_r": _round(max_drawdown, _R_DP),
    }


# ---------------------------------------------------------------------------
# Execution / system sections
# ---------------------------------------------------------------------------


def execution_section(trades: list[dict]) -> dict[str, Any]:
    statuses = [str(t.get("status", "")).upper() for t in trades]
    closed = [t for t, s in zip(trades, statuses) if s == "CLOSED"]
    open_trades = sum(1 for s in statuses if s == "OPEN")
    dry_run = sum(1 for s in statuses if s == "DRY_RUN")
    failed = sum(1 for s in statuses if s == "EXECUTION_FAILED")

    if closed:
        fully_broker_tagged = all(
            t.get("broker_net") is not None and t.get("broker_price") is not None
            for t in closed
        )
        reconciliation = "RECONCILED" if fully_broker_tagged else "PARTIAL"
    elif open_trades or dry_run:
        reconciliation = "NOT_RUN"
    else:
        reconciliation = "NO_DATA"

    return {
        "open_trades": open_trades,
        "closed_trades": len(closed),
        "dry_run_trades": dry_run,
        "execution_failed": failed,
        "broker_reconciliation_status": reconciliation,
    }


def system_section(config: ReportConfig) -> dict[str, Any]:
    return {
        "geometry_status": config.geometry_status,
        "live_trading_status": (
            "ENABLED" if config.live_trading_enabled
            else "DISABLED (LIVE_TRADING_ENABLE=false)"
        ),
        "journal_source": config.journal_source,
    }


# ---------------------------------------------------------------------------
# Breakdowns
# ---------------------------------------------------------------------------


def _zone(name: str):
    try:
        from zoneinfo import ZoneInfo

        return ZoneInfo(name)
    except Exception:
        return None


def _period_key(ts: datetime, zone_name: str, granularity: str) -> tuple[str, str]:
    zone = _zone(zone_name)
    if zone is not None:
        local = ts.astimezone(zone)
        tz_label = zone_name
    else:
        local = ts.astimezone(timezone.utc)
        tz_label = "UTC (session timezone unavailable)"
    iso = local.isocalendar()
    if granularity == "day":
        return local.date().isoformat(), tz_label
    return f"{iso[0]}-W{iso[1]:02d}", tz_label


def daily_breakdown(signals: list[dict], trades: list[dict], config: ReportConfig) -> dict[str, Any]:
    zone_name = config.session_timezone
    closed = _closed_trades(trades)
    buckets: dict[str, dict[str, Any]] = {}

    def bucket(ts: datetime) -> dict[str, Any]:
        key, _ = _period_key(ts, zone_name, "day")
        if key not in buckets:
            buckets[key] = {"signals": 0, "win": 0, "loss": 0, "ambiguous": 0, "net_r": 0.0}
        return buckets[key]

    for signal in signals:
        ts = record_timestamp_utc(signal)
        if ts is None:
            continue
        status = str(signal.get("status", "")).upper()
        if status == "DUPLICATE_REJECTED":
            continue
        bucket(ts)["signals"] += 1

    for trade in closed:
        ts = record_timestamp_utc(trade)
        if ts is None:
            continue
        entry = bucket(ts)
        result = str(trade.get("result", "")).upper()
        if result == "WIN":
            entry["win"] += 1
        elif result == "LOSS":
            entry["loss"] += 1
        else:
            entry["ambiguous"] += 1
        r = _trade_r(trade)
        if r is not None:
            entry["net_r"] += r

    rows = [
        {
            "date": key,
            "signals": entry["signals"],
            "win": entry["win"],
            "loss": entry["loss"],
            "ambiguous": entry["ambiguous"],
            "net_r": _round(entry["net_r"], _R_DP),
        }
        for key, entry in sorted(buckets.items())
    ]
    _, tz_label = _period_key(datetime(2026, 1, 1, tzinfo=timezone.utc), zone_name, "day")
    return {"timezone": tz_label, "rows": rows}


def weekly_breakdown(signals: list[dict], trades: list[dict], config: ReportConfig) -> dict[str, Any]:
    zone_name = config.session_timezone
    closed = _closed_trades(trades)
    buckets: dict[str, dict[str, Any]] = {}

    def bucket(ts: datetime) -> dict[str, Any]:
        key, _ = _period_key(ts, zone_name, "week")
        if key not in buckets:
            buckets[key] = {"signals": 0, "win": 0, "loss": 0, "ambiguous": 0, "net_r": 0.0}
        return buckets[key]

    for signal in signals:
        ts = record_timestamp_utc(signal)
        if ts is None:
            continue
        if str(signal.get("status", "")).upper() == "DUPLICATE_REJECTED":
            continue
        bucket(ts)["signals"] += 1

    for trade in closed:
        ts = record_timestamp_utc(trade)
        if ts is None:
            continue
        entry = bucket(ts)
        result = str(trade.get("result", "")).upper()
        if result == "WIN":
            entry["win"] += 1
        elif result == "LOSS":
            entry["loss"] += 1
        else:
            entry["ambiguous"] += 1
        r = _trade_r(trade)
        if r is not None:
            entry["net_r"] += r

    rows = [
        {
            "week": key,
            "signals": entry["signals"],
            "win": entry["win"],
            "loss": entry["loss"],
            "ambiguous": entry["ambiguous"],
            "net_r": _round(entry["net_r"], _R_DP),
        }
        for key, entry in sorted(buckets.items())
    ]
    return {"timezone": config.session_timezone if _zone(zone_name) else "UTC (session timezone unavailable)", "rows": rows}


def trade_list_summary(signals: list[dict], trades: list[dict], pip_size: float | None) -> list[dict[str, Any]]:
    """One deterministic row per signal record in the period."""
    trades_by_signal: dict[str, list[dict]] = {}
    for trade in trades:
        sid = _signal_id(trade)
        if sid is not None:
            trades_by_signal.setdefault(sid, []).append(trade)

    rows: list[dict[str, Any]] = []
    for signal in sorted(signals, key=_sort_key):
        if str(signal.get("status", "")).upper() == "DUPLICATE_REJECTED":
            continue
        sid = _signal_id(signal) or ""
        related = sorted(trades_by_signal.get(sid, []), key=_sort_key)
        closed = [t for t in related if str(t.get("status", "")).upper() == "CLOSED"]
        if closed:
            latest = closed[-1]
            result = str(latest.get("result", "")).upper() or "AMBIGUOUS"
            r_value = _round(_trade_r(latest), _R_DP)
            pips = _round(_trade_pips(latest, pip_size), _PIPS_DP)
            status = "CLOSED"
        elif related:
            latest = related[-1]
            result = "AMBIGUOUS"
            r_value = None
            pips = None
            status = str(latest.get("status", "")).upper() or "UNKNOWN"
        else:
            result = "AMBIGUOUS"
            r_value = None
            pips = None
            status = "NO_TRADE_RECORD"

        rows.append({
            "signal_id": sid,
            "direction": signal.get("direction"),
            "timestamp_utc": (record_timestamp_utc(signal).isoformat() if record_timestamp_utc(signal) else None),
            "status": status,
            "result": result,
            "r_multiple": r_value,
            "pips": pips,
        })
    return rows


# ---------------------------------------------------------------------------
# Report builders
# ---------------------------------------------------------------------------


def _period_slice(signals: list[dict], trades: list[dict], start: datetime, end: datetime):
    period_signals = sorted((s for s in signals if _in_period(s, start, end)), key=_sort_key)
    period_trades = sorted((t for t in trades if _in_period(t, start, end)), key=_sort_key)
    unclassified = sum(1 for row in signals + trades if record_timestamp_utc(row) is None)
    return period_signals, period_trades, unclassified


def _base_report(
    report_type: str,
    start: datetime,
    end: datetime,
    generated_at_utc: str,
    signals: list[dict],
    trades: list[dict],
    config: ReportConfig,
) -> dict[str, Any]:
    period_signals, period_trades, unclassified = _period_slice(signals, trades, start, end)
    closed = _closed_trades(period_trades)
    return {
        "schema": SCHEMA,
        "report_type": report_type,
        "generated_at_utc": generated_at_utc,
        "period": {
            "start_utc": start.astimezone(timezone.utc).isoformat(),
            "end_utc": end.astimezone(timezone.utc).isoformat(),
            "session_timezone": config.session_timezone,
            "basis": config.period_basis,
        },
        "signals": classify_signals(period_signals, period_trades),
        "performance": performance_metrics(closed, config.pip_size),
        "execution": execution_section(period_trades),
        "system": system_section(config),
        "determinism": {
            "input_signal_records": len(signals),
            "input_trade_records": len(trades),
            "period_signal_records": len(period_signals),
            "period_trade_records": len(period_trades),
            "unclassified_records": unclassified,
            "sorted_by": "timestamp_utc,signal_id,deal_id",
        },
        "_period_rows": (period_signals, period_trades),
    }


def build_report(
    report_type: str,
    start: datetime,
    end: datetime,
    generated_at_utc: str,
    signals: list[dict],
    trades: list[dict],
    config: ReportConfig | None = None,
) -> dict[str, Any]:
    """Build one daily/weekly/monthly report dict (pure function)."""
    if report_type not in {"daily", "weekly", "monthly"}:
        raise ValueError(f"unsupported report type: {report_type}")
    config = config or ReportConfig()

    report = _base_report(report_type, start, end, generated_at_utc, signals, trades, config)
    period_signals, period_trades = report.pop("_period_rows")
    closed = _closed_trades(period_trades)

    if report_type in {"weekly", "monthly"}:
        report["daily_breakdown"] = daily_breakdown(period_signals, period_trades, config)
        report["trade_list_summary"] = trade_list_summary(period_signals, period_trades, config.pip_size)
    if report_type == "monthly":
        report["weekly_breakdown"] = weekly_breakdown(period_signals, period_trades, config)
        report["equity_summary"] = equity_summary(closed)

    return report


def report_to_json(report: dict[str, Any]) -> str:
    """Canonical deterministic JSON serialization (sorted keys, fixed indent)."""
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False)


def period_csv_rows(trades: list[dict], start: datetime, end: datetime) -> list[dict]:
    """Period-filtered trade rows for CSV export (existing CSV conventions)."""
    return sorted((t for t in trades if _in_period(t, start, end)), key=_sort_key)
