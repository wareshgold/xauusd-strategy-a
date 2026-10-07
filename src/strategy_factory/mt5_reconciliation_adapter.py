from __future__ import annotations

"""Research-only adapter for the existing SP2L to MT5 reconciliation report."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable


class MT5ReconciliationAdapterError(RuntimeError):
    """Raised when the existing reconciliation report is incomplete."""


@dataclass(frozen=True)
class MT5ReconciliationObservation:
    reconciliation_id: str
    broker_server: str
    symbol: str
    observed_positions: int
    matched_positions: int
    mismatched_positions: int
    detail: str


def normalize_existing_reconciliation_report(
    report: dict[str, Any],
    *,
    reconciliation_id: str,
) -> MT5ReconciliationObservation:
    """Normalize facts emitted by scripts.reconcile_sp2l_forward_mt5."""
    required = {
        "symbol",
        "mt5_closed_position_count",
        "common_positions",
        "event_only_positions",
        "mt5_only_positions",
        "position_mismatches",
        "account",
    }
    missing = sorted(required.difference(report))
    if missing:
        raise MT5ReconciliationAdapterError(
            "existing MT5 reconciliation report omitted required fields: "
            + ", ".join(missing)
        )

    account = report["account"]
    if not isinstance(account, dict) or not account.get("server"):
        raise MT5ReconciliationAdapterError(
            "existing MT5 reconciliation report omitted account.server"
        )

    common = int(report["common_positions"])
    pnl_mismatches = len(report["position_mismatches"])
    event_only = len(report["event_only_positions"])
    mt5_only = len(report["mt5_only_positions"])

    if min(common, pnl_mismatches, event_only, mt5_only) < 0:
        raise MT5ReconciliationAdapterError("negative reconciliation count")
    if pnl_mismatches > common:
        raise MT5ReconciliationAdapterError(
            "P&L mismatch count exceeds common position count"
        )

    matched = common - pnl_mismatches
    mismatched = event_only + mt5_only + pnl_mismatches
    observed = int(report["mt5_closed_position_count"])

    if observed < mt5_only:
        raise MT5ReconciliationAdapterError(
            "MT5-only position count exceeds observed MT5 closed positions"
        )

    return MT5ReconciliationObservation(
        reconciliation_id=str(reconciliation_id),
        broker_server=str(account["server"]),
        symbol=str(report["symbol"]),
        observed_positions=observed,
        matched_positions=matched,
        mismatched_positions=mismatched,
        detail=(
            "Normalized from existing read-only SP2L to MT5 reconciliation: "
            f"common={common}, event_only={event_only}, mt5_only={mt5_only}, "
            f"pnl_mismatches={pnl_mismatches}"
        ),
    )


def build_existing_mt5_reconciliation(
    *,
    event_file: Path,
    symbol: str,
    magic: int,
    reconciliation_id: str,
    day: date | None = None,
    mt5_path: Path | None = None,
    report_builder: Callable[..., dict[str, Any]] | None = None,
) -> MT5ReconciliationObservation:
    """Run the existing read-only reconciliation and normalize its facts.

    report_builder is injectable for deterministic tests. Production callers
    use the existing script's build_report implementation unchanged.
    """
    import argparse

    args = argparse.Namespace(
        date=day.isoformat() if day else None,
        event_file=event_file,
        symbol=symbol,
        magic=int(magic),
        mt5_path=mt5_path
        or Path(r"C:\Program Files\Otet Group MT5 Terminal\terminal64.exe"),
        as_json=True,
    )

    if report_builder is None:
        from scripts.reconcile_sp2l_forward_mt5 import build_report
        report_builder = build_report

    try:
        report = report_builder(args)
    except Exception as exc:
        raise MT5ReconciliationAdapterError(
            f"existing MT5 reconciliation failed: {exc}"
        ) from exc

    return normalize_existing_reconciliation_report(
        report,
        reconciliation_id=reconciliation_id,
    )


def as_factory_reconciliation_dict(
    observation: MT5ReconciliationObservation,
) -> dict[str, object]:
    """Return exactly the observed-fields contract required by the Factory."""
    return {
        "reconciliation_id": observation.reconciliation_id,
        "broker_server": observation.broker_server,
        "symbol": observation.symbol,
        "observed_positions": observation.observed_positions,
        "matched_positions": observation.matched_positions,
        "mismatched_positions": observation.mismatched_positions,
        "detail": observation.detail,
    }
