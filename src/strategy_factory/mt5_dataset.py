from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from .datasets import DatasetArtifact, DatasetRegistry, DatasetRegistryError
from .test_contract import HistoricalTestSpec


class MT5DatasetPreparationError(ValueError):
    """Raised when an MT5 M1 research snapshot cannot be prepared safely."""


@dataclass(frozen=True)
class MT5M1Snapshot:
    """Immutable M1 artifact exported from MT5 for one research job."""

    artifact: DatasetArtifact
    dataset_content_sha256: str
    payload: dict[str, Any]

    def validate(self) -> None:
        self.artifact.validate()
        if self.dataset_content_sha256 != self.artifact.content_sha256:
            raise MT5DatasetPreparationError("snapshot hash does not match artifact hash")
        if self.payload.get("status") != "COMPLETE":
            raise MT5DatasetPreparationError("MT5 snapshot exporter did not complete")
        if self.payload.get("symbol") != "XAUUSD.ecn":
            raise MT5DatasetPreparationError("MT5 snapshot symbol is not XAUUSD.ecn")
        if self.payload.get("timeframe") != "M1":
            raise MT5DatasetPreparationError("MT5 snapshot timeframe is not M1")

    def register(self, registry: DatasetRegistry, spec: HistoricalTestSpec, *, lock: bool = True) -> None:
        self.validate()
        try:
            registry.register(
                spec.dataset,
                self.dataset_content_sha256,
                lock=lock,
                artifact=self.artifact,
            )
        except DatasetRegistryError as exc:
            raise MT5DatasetPreparationError("MT5 dataset could not be registered immutably") from exc


@dataclass(frozen=True)
class MT5M1ArtifactExporter:
    """Research-only bridge from MT5 history to an immutable M1 artifact.

    This component does not detect signals, replay trades, rank variants,
    define geometry, or make production decisions.
    """

    script_path: Path
    mt5_path: str
    output_path: Path
    symbol: str = "XAUUSD.ecn"
    start: str = "2026-10-05T00:00:00+00:00"
    end: str = "2026-10-07T05:30:00+00:00"
    python_executable: str = "python"

    def _command(self) -> list[str]:
        return [
            self.python_executable,
            str(self.script_path),
            "--mt5-path", self.mt5_path,
            "--symbol", self.symbol,
            "--start", self.start,
            "--end", self.end,
            "--output", str(self.output_path),
        ]

    def export(self) -> MT5M1Snapshot:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        completed = subprocess.run(
            self._command(),
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise MT5DatasetPreparationError(
                f"MT5 M1 exporter failed: {completed.stderr.strip() or completed.stdout.strip()}"
            )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise MT5DatasetPreparationError("MT5 M1 exporter returned invalid JSON") from exc

        payload_path = Path(str(payload.get("artifact", self.output_path)))
        if not payload_path.is_file():
            raise MT5DatasetPreparationError(f"MT5 M1 artifact not found: {payload_path}")

        raw = payload_path.read_bytes()
        import hashlib
        observed_sha = hashlib.sha256(raw).hexdigest()
        declared_sha = str(payload.get("sha256", ""))
        if observed_sha != declared_sha:
            raise MT5DatasetPreparationError("MT5 M1 artifact SHA-256 mismatch")

        artifact = DatasetArtifact(
            artifact_id=f"MT5-M1-{observed_sha[:16]}",
            location=str(payload_path.resolve()),
            content_sha256=observed_sha,
            byte_size=len(raw),
            format="json",
        )
        snapshot = MT5M1Snapshot(
            artifact=artifact,
            dataset_content_sha256=observed_sha,
            payload=payload,
        )
        snapshot.validate()
        return snapshot
