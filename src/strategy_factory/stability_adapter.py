from __future__ import annotations

"""Execution adapter for the existing SP2L controlled Stability Matrix.

Research-only. The adapter consumes an already-produced Discovery JSON and the
exact immutable M1 artifact identity bound to the upstream handoff. It never
queries MT5 and never changes Strategy A geometry.
"""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from .adapter import build_execution_receipt
from .execution import ExecutionReceipt
from .metrics import ResearchMetrics
from .test_contract import HistoricalTestSpec


class StabilityAdapterError(RuntimeError):
    """Raised when Stability cannot consume the declared Discovery artifact."""


@dataclass(frozen=True)
class StabilityMatrixAdapter:
    script_path: Path
    discovery_json_path: Path
    dataset_artifact_path: Path
    expected_dataset_content_sha256: str
    expected_dataset_artifact_id: str
    variant_name: str = "RR2_ACT10_D2"
    segments: int = 3
    python_executable: str = sys.executable
    engine_revision: str = "SP2L-V3-CONTROLLED-STABILITY-20261007"

    @property
    def observed_dataset_content_sha256(self) -> str:
        path = Path(self.dataset_artifact_path)
        if not path.is_file():
            raise StabilityAdapterError(f"dataset artifact not found: {path}")
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _validate_inputs(self) -> tuple[dict, str]:
        if not self.script_path.is_file():
            raise StabilityAdapterError(f"stability script not found: {self.script_path}")
        if not self.discovery_json_path.is_file():
            raise StabilityAdapterError(
                f"Discovery JSON not found: {self.discovery_json_path}"
            )
        actual_sha = self.observed_dataset_content_sha256
        if actual_sha != self.expected_dataset_content_sha256:
            raise StabilityAdapterError(
                "Stability dataset SHA does not match the handoff-bound dataset SHA"
            )
        payload = json.loads(
            self.discovery_json_path.read_text(encoding="utf-8")
        )
        dataset = payload.get("dataset_provenance") or {}
        if dataset.get("content_sha256") != actual_sha:
            raise StabilityAdapterError(
                "Discovery JSON is not bound to the exact immutable M1 artifact"
            )
        if dataset.get("artifact_id") != self.expected_dataset_artifact_id:
            raise StabilityAdapterError(
                "Discovery JSON artifact_id does not match the handoff-bound artifact"
            )
        if payload.get("research_only") is not True:
            raise StabilityAdapterError("Discovery JSON is not marked research_only")
        if not self.variant_name:
            raise StabilityAdapterError("variant_name is required")
        if self.segments < 2:
            raise StabilityAdapterError("segments must be >= 2")
        return payload, actual_sha

    def execute(self, spec: HistoricalTestSpec) -> ExecutionReceipt:
        spec.validate()
        payload, dataset_sha = self._validate_inputs()

        completed = subprocess.run(
            [
                self.python_executable,
                str(self.script_path),
                "--input",
                str(self.discovery_json_path),
                "--segments",
                str(self.segments),
            ],
            cwd=str(self.script_path.parent.parent),
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise StabilityAdapterError(
                "Stability Matrix failed: "
                + (completed.stderr.strip() or completed.stdout.strip())
            )

        try:
            completion = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise StabilityAdapterError(
                "Stability Matrix did not return valid JSON completion output"
            ) from exc
        if completion.get("status") != "COMPLETE":
            raise StabilityAdapterError("Stability Matrix did not report COMPLETE")

        result_path = Path(str(completion.get("json", "")))
        if not result_path.is_file():
            raise StabilityAdapterError(
                f"Stability output JSON not found: {result_path}"
            )
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if result.get("research_only") is not True:
            raise StabilityAdapterError("Stability output is not marked research_only")
        if result.get("governance", {}).get("production_eligible") is not False:
            raise StabilityAdapterError("Stability output is not production locked")
        if result.get("governance", {}).get("source_meaning_unchanged") is not True:
            raise StabilityAdapterError("Stability output does not preserve source meaning")

        matches = [
            row for row in result.get("matrix", [])
            if row.get("variant") == self.variant_name
        ]
        if len(matches) != 1:
            raise StabilityAdapterError(
                f"expected exactly one Stability variant {self.variant_name!r}, found {len(matches)}"
            )
        row = matches[0]
        overall = row["overall"]

        discovery_trades = [
            trade for trade in payload.get("trades", [])
            if trade.get("variant") == self.variant_name
            and not trade.get("ambiguous")
            and trade.get("realized_R") is not None
        ]
        gross_profit_r = sum(
            max(float(t["realized_R"]), 0.0) for t in discovery_trades
        )
        gross_loss_r = sum(
            min(float(t["realized_R"]), 0.0) for t in discovery_trades
        )

        metrics = ResearchMetrics(
            trades=int(overall["signals"]),
            decisive_trades=int(overall["decisive"]),
            wins=int(overall["wins"]),
            losses=int(overall["losses"]),
            ambiguous=int(overall["ambiguous"]),
            win_rate=(
                float(overall["wins"]) / int(overall["decisive"])
                if int(overall["decisive"]) else 0.0
            ),
            net_r=float(overall["net_R"]),
            profit_factor=(
                float(overall["profit_factor"])
                if overall["profit_factor"] is not None
                else None
            ),
            max_drawdown_r=float(overall["max_drawdown_R"]),
            gross_profit_r=gross_profit_r,
            gross_loss_r=gross_loss_r,
        )

        input_payload = {
            "spec": spec.as_dict(),
            "discovery_json": str(self.discovery_json_path),
            "discovery_sha256": hashlib.sha256(
                self.discovery_json_path.read_bytes()
            ).hexdigest(),
            "dataset_content_sha256": dataset_sha,
            "dataset_artifact_id": self.expected_dataset_artifact_id,
            "variant_name": self.variant_name,
            "segments": self.segments,
            "stability_json": str(result_path),
            "stability_sha256": hashlib.sha256(
                result_path.read_bytes()
            ).hexdigest(),
        }
        input_fingerprint = hashlib.sha256(
            json.dumps(
                input_payload,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        return build_execution_receipt(
            execution_id=f"STABILITY-{spec.test_id}-{self.variant_name}",
            spec=spec,
            engine_revision=self.engine_revision,
            input_fingerprint=input_fingerprint,
            metrics=metrics,
        )
