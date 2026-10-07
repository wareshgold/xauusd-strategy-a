from __future__ import annotations

"""Execution adapter for the existing SP2L controlled Discovery Matrix.

This adapter does not implement discovery geometry or optimization. It invokes
the existing research script, then binds one explicitly declared matrix variant
to the Factory's single-result execution contract.
"""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from .adapter import build_execution_receipt
from .execution import ExecutionReceipt
from .metrics import ResearchMetrics
from .test_contract import HistoricalTestSpec


class DiscoveryAdapterError(RuntimeError):
    """Raised when the existing Discovery Matrix cannot be consumed safely."""


@dataclass(frozen=True)
class DiscoveryMatrixAdapter:
    """Run the repository's existing Discovery Matrix for one declared variant."""

    script_path: Path
    mt5_path: str
    symbol: str = "XAUUSD.ecn"
    start: str = "2026-10-05T00:00:00+00:00"
    end: str = "2026-10-07T05:30:00+00:00"
    variant_name: str = "RR2_ACT10_D2"
    bars_artifact_path: Path | None = None
    python_executable: str = sys.executable
    engine_revision: str = "SP2L-V3-CONTROLLED-DISCOVERY-20261007"

    @property
    def observed_dataset_content_sha256(self) -> str:
        """Return the exact SHA-256 of the immutable M1 artifact used by Discovery."""
        if self.bars_artifact_path is None:
            raise DiscoveryAdapterError(
                "bars_artifact_path is required for Factory dataset provenance"
            )
        path = Path(self.bars_artifact_path)
        if not path.is_file():
            raise DiscoveryAdapterError(f"M1 dataset artifact not found: {path}")
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _command(self) -> list[str]:
        command = [
            self.python_executable,
            str(self.script_path),
            "--mt5-path",
            self.mt5_path,
            "--symbol",
            self.symbol,
            "--start",
            self.start,
            "--end",
            self.end,
        ]
        if self.bars_artifact_path is not None:
            command.extend(["--bars-artifact", str(self.bars_artifact_path)])
        return command

    def execute(self, spec: HistoricalTestSpec) -> ExecutionReceipt:
        spec.validate()
        if not self.script_path.is_file():
            raise DiscoveryAdapterError(f"discovery script not found: {self.script_path}")
        if not self.mt5_path:
            raise DiscoveryAdapterError("mt5_path is required")
        if not self.variant_name:
            raise DiscoveryAdapterError("variant_name is required")
        expected_dataset_sha256 = self.observed_dataset_content_sha256

        completed = subprocess.run(
            self._command(),
            cwd=str(self.script_path.parent.parent),
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise DiscoveryAdapterError(
                "Discovery Matrix failed: "
                + (completed.stderr.strip() or completed.stdout.strip())
            )

        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise DiscoveryAdapterError(
                "Discovery Matrix did not return a valid JSON completion payload"
            ) from exc

        if payload.get("status") != "COMPLETE":
            raise DiscoveryAdapterError("Discovery Matrix did not report COMPLETE")

        json_path = Path(str(payload.get("json", "")))
        if not json_path.is_file():
            raise DiscoveryAdapterError(f"Discovery output JSON not found: {json_path}")

        result = json.loads(json_path.read_text(encoding="utf-8"))
        if result.get("research_only") is not True:
            raise DiscoveryAdapterError("Discovery output is not marked research_only")

        dataset = result.get("dataset_provenance") or {}
        if dataset.get("content_sha256") != expected_dataset_sha256:
            raise DiscoveryAdapterError(
                "Discovery did not consume the declared M1 dataset artifact"
            )

        matches = [
            row for row in result.get("matrix", [])
            if row.get("name") == self.variant_name
        ]
        if len(matches) != 1:
            raise DiscoveryAdapterError(
                f"expected exactly one Discovery variant {self.variant_name!r}, found {len(matches)}"
            )
        row = matches[0]

        # Gross R is reconstructable from the variant summary's PF/net-R only
        # when losses are available. The Discovery matrix currently does not
        # expose gross R directly, so use decisive trade replay rows as the
        # authoritative source for the Factory metrics.
        trades = [
            trade for trade in result.get("trades", [])
            if trade.get("variant") == self.variant_name
            and not trade.get("ambiguous")
            and trade.get("realized_R") is not None
        ]
        gross_profit_r = sum(max(float(t["realized_R"]), 0.0) for t in trades)
        gross_loss_r = sum(min(float(t["realized_R"]), 0.0) for t in trades)

        metrics = ResearchMetrics(
            trades=int(row["signals"]),
            decisive_trades=int(row["decisive"]),
            wins=int(row["wins"]),
            losses=int(row["losses"]),
            ambiguous=int(row["ambiguous"]),
            win_rate=(float(row["wins"]) / int(row["decisive"])) if int(row["decisive"]) else 0.0,
            net_r=float(row["net_R"]),
            profit_factor=float(row["profit_factor"] or 0.0),
            max_drawdown_r=float(row["max_drawdown_R"]),
            gross_profit_r=gross_profit_r,
            gross_loss_r=gross_loss_r,
        )

        content = json.dumps(
            {
                "spec": spec.as_dict(),
                "script": str(self.script_path),
                "symbol": self.symbol,
                "start": self.start,
                "end": self.end,
                "variant_name": self.variant_name,
                "matrix_json": str(json_path),
                "matrix_sha256": payload.get("sha256"),
                "dataset_content_sha256": expected_dataset_sha256,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        input_fingerprint = hashlib.sha256(content).hexdigest()

        return build_execution_receipt(
            execution_id=f"DISCOVERY-{spec.test_id}-{self.variant_name}",
            spec=spec,
            engine_revision=self.engine_revision,
            input_fingerprint=input_fingerprint,
            metrics=metrics,
        )
