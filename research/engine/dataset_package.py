from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass(frozen=True)
class SplitSummary:
    name: str
    start_utc: str
    end_utc: str
    chunks: int
    rows: int
    quality_pass: bool


@dataclass(frozen=True)
class DatasetReadiness:
    dataset_sha256: str
    symbol: str
    interval: str
    source_timezone: str
    splits: tuple[SplitSummary, ...]

    @property
    def pass_gate(self) -> bool:
        return bool(self.splits) and all(s.quality_pass for s in self.splits) and _splits_are_contiguous(self.splits)


def load_readiness(manifest_path: str | Path) -> DatasetReadiness:
    payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    summaries = []
    for window in payload["windows"]:
        chunks = window["chunks"]
        summaries.append(SplitSummary(
            name=window["window"],
            start_utc=chunks[0]["start_utc"],
            end_utc=chunks[-1]["end_utc"],
            chunks=len(chunks),
            rows=sum(c["row_count"] for c in chunks),
            quality_pass=all(c["quality_status"] == "PASS" for c in chunks),
        ))
    return DatasetReadiness(payload["dataset_sha256"], payload["symbol"], payload["interval"], payload["source_timezone"], tuple(summaries))


def _splits_are_contiguous(splits: tuple[SplitSummary, ...]) -> bool:
    ordered = sorted(splits, key=lambda s: _parse(s.start_utc))
    for a, b in zip(ordered, ordered[1:]):
        if _parse(b.start_utc) != _parse(a.end_utc) + timedelta(minutes=1):
            return False
    return True


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(timezone.utc)
