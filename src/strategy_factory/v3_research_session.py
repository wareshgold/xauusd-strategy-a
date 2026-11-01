from __future__ import annotations

"""Provenance-bound loader for an interactive, research-only V3 replay session.

No MT5 connection, signal generation, or entry-geometry calculation occurs here.
The caller must supply exact source hashes, the expected M1 identity/window,
and explicit broker contract metadata.
"""

import csv
import io
import json
from pathlib import Path
from typing import Any

from .frozen_entry_population import load_frozen_entry_population
from .m1_integrity import validate_m1_artifact
from .v3_exit_engine import V3ExitReplayEngine, V3ExitVariant
from .v3_trade_management import V3TradeManagementEngine


class V3ResearchSessionError(ValueError):
    """Raised when research session inputs cannot be provenance-bound."""


class V3ResearchSession:
    def __init__(
        self,
        *,
        m1_artifact: str | Path,
        entry_artifact: str | Path,
        expected_dataset_sha256: str,
        expected_entry_sha256: str,
        expected_symbol: str,
        expected_start_utc: str,
        expected_end_utc: str,
        mt5_point: float,
        contract_size: float,
        volume: float,
        engine_revision: str,
    ) -> None:
        self.m1_path = Path(m1_artifact).resolve()
        self.entry_path = Path(entry_artifact).resolve()
        for label, digest in (
            ("expected_dataset_sha256", expected_dataset_sha256),
            ("expected_entry_sha256", expected_entry_sha256),
        ):
            if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower()):
                raise V3ResearchSessionError(f"{label} must be a SHA-256 hex digest")
        try:
            integrity = validate_m1_artifact(
                self.m1_path,
                expected_symbol=expected_symbol,
                expected_start=expected_start_utc,
                expected_end=expected_end_utc,
            )
        except (OSError, ValueError) as exc:
            raise V3ResearchSessionError(f"M1 artifact validation failed: {exc}") from exc
        if integrity.content_sha256.lower() != expected_dataset_sha256.lower():
            raise V3ResearchSessionError("M1 artifact SHA-256 does not match expected dataset hash")

        raw = self.m1_path.read_bytes()
        if self.m1_path.suffix.lower() == ".csv":
            reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
            bars = tuple({
                "time": int(row["time_epoch_seconds"]),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "tick_volume": int(row["tick_volume"]),
                "spread": int(row["spread"]),
                "real_volume": int(row["real_volume"]),
            } for row in reader)
        else:
            payload = json.loads(raw.decode("utf-8"))
            bars = tuple(dict(row) for row in payload["bars"])
        population, entry_report = load_frozen_entry_population(
            self.entry_path,
            bars,
            expected_entry_sha256,
        )
        self.dataset_report = integrity.as_dict()
        self.entry_report = entry_report
        self.m1_metadata_provenance = (
            "EMBEDDED_JSON_METADATA"
            if self.m1_path.suffix.lower() != ".csv"
            else "CALLER_ASSERTED_CSV_IDENTITY_NO_EMBEDDED_SYMBOL_OR_WINDOW"
        )
        self.symbol_identity_verified = self.m1_path.suffix.lower() != ".csv"
        self.symbol = expected_symbol
        self.timeframe = "M1"
        self.window_utc = {
            "start": integrity.start_utc,
            "end": integrity.end_utc,
        }
        self.engine = V3ExitReplayEngine(
            bars=bars,
            population=population,
            mt5_point=mt5_point,
            contract_size=contract_size,
            volume=volume,
            engine_revision=engine_revision,
            dataset_sha256=integrity.content_sha256,
            entry_population_sha256=entry_report["content_sha256"],
        )
        self.management_engine = V3TradeManagementEngine(self.engine)
        self.session_fingerprint = self.engine.session_fingerprint
        self.engine_revision = engine_revision
        self.research_only = True

    @property
    def cache_entries(self) -> int:
        return self.engine.cache_entries + self.management_engine.cache_entries

    @property
    def population_size(self) -> int:
        return self.engine.population_size

    def evaluate(
        self,
        *,
        rr: float,
        activation_points: float | None,
        distance_points: float | None,
    ) -> V3ExitVariant:
        return self.engine.evaluate(
            rr=rr,
            activation_points=activation_points,
            distance_points=distance_points,
        )

    def evaluate_management(self, policy: dict[str, Any]) -> V3ExitVariant:
        return self.management_engine.evaluate(policy)

    def flat_spread_sensitivity(self, summary: dict[str, Any]) -> dict[str, Any]:
        """Return explicitly hypothetical one-full-spread-per-decisive-trade costs."""
        decisive = int(summary["decisive"])
        point = self.engine._mt5_point
        notional = self.engine._volume * self.engine._contract_size
        scenarios = {}
        for spread_points in (20, 23, 30):
            cost_per_trade = spread_points * point * notional
            total_cost = cost_per_trade * decisive
            scenarios[str(spread_points)] = {
                "spread_points": spread_points,
                "cost_per_trade_usd": cost_per_trade,
                "estimated_total_spread_cost_usd": total_cost,
                "estimated_net_after_spread_usd": float(summary["net_profit_usd"]) - total_cost,
            }
        return {
            "method": "FLAT_ONE_FULL_SPREAD_PER_DECISIVE_TRADE_PROXY",
            "not_actual_execution_cost": True,
            "commission_included": False,
            "slippage_included": False,
            "decisive_trades_charged": decisive,
            "scenarios": scenarios,
        }

    def compare(self, left: V3ExitVariant, right: V3ExitVariant) -> dict[str, Any]:
        return self.engine.compare(left, right)

    def manifest(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "research_only": True,
            "session_fingerprint": self.session_fingerprint,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "window_utc": dict(self.window_utc),
            "dataset": dict(self.dataset_report),
            "m1_metadata_provenance": self.m1_metadata_provenance,
            "symbol_identity_verified": self.symbol_identity_verified,
            "entry_population": dict(self.entry_report),
            "population_size": self.population_size,
            "engine_revision": self.engine_revision,
            "cache_entries": self.cache_entries,
            "canonical": False,
            "validation_status": "NOT_VALIDATED",
        }
