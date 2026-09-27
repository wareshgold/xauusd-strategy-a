"""Deterministic research-only ledger for SP2L candidate runs.

This module does not choose strategy rules. It records the output of a
candidate detector/execution model so candidates can be compared without
re-running or interpreting aggregate metrics.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any, Iterable


@dataclass(frozen=True)
class CandidateManifest:
    candidate_id: str
    detector_sha: str
    configuration: dict[str, Any]
    dataset: dict[str, Any]
    execution_convention: dict[str, Any]
    canonical: bool = False

    def stable_id(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SignalRecord:
    candidate_id: str
    signal_id: str
    direction: str
    before_spike_time: int
    spike_time: int
    after_spike_time: int
    entry_time: int | None
    entry: float | None
    sl: float | None
    tp: float | None
    risk: float | None
    status: str
    rejection_reason: str | None = None

    @property
    def setup_key(self) -> tuple:
        return (
            self.direction,
            self.before_spike_time,
            self.spike_time,
            self.after_spike_time,
        )

    @property
    def signal_key(self) -> tuple:
        return self.setup_key + (self.entry_time,)


@dataclass(frozen=True)
class TradeRecord:
    candidate_id: str
    signal_id: str
    direction: str
    entry_time: int
    entry: float
    sl: float
    tp: float
    exit_time: int
    exit: float
    exit_reason: str
    realized_r: float
    completed: bool


def candidate_manifest(
    *,
    candidate_id: str,
    detector_sha: str,
    configuration: dict[str, Any],
    dataset: dict[str, Any],
    execution_convention: dict[str, Any],
) -> CandidateManifest:
    if not candidate_id or candidate_id.strip() == "":
        raise ValueError("candidate_id is required")
    if not detector_sha or detector_sha.strip() == "":
        raise ValueError("detector_sha is required")
    return CandidateManifest(
        candidate_id=candidate_id,
        detector_sha=detector_sha,
        configuration=dict(configuration),
        dataset=dict(dataset),
        execution_convention=dict(execution_convention),
        canonical=False,
    )


def signal_id(candidate_id: str, setup_key: tuple, entry_time: int | None) -> str:
    payload = json.dumps(
        [candidate_id, list(setup_key), entry_time],
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def record_signal(
    *,
    candidate_id: str,
    direction: str,
    before_spike_time: int,
    spike_time: int,
    after_spike_time: int,
    entry_time: int | None,
    entry: float | None,
    sl: float | None,
    tp: float | None,
    risk: float | None,
    status: str,
    rejection_reason: str | None = None,
) -> SignalRecord:
    setup_key = (direction, before_spike_time, spike_time, after_spike_time)
    return SignalRecord(
        candidate_id=candidate_id,
        signal_id=signal_id(candidate_id, setup_key, entry_time),
        direction=direction,
        before_spike_time=before_spike_time,
        spike_time=spike_time,
        after_spike_time=after_spike_time,
        entry_time=entry_time,
        entry=entry,
        sl=sl,
        tp=tp,
        risk=risk,
        status=status,
        rejection_reason=rejection_reason,
    )


def compare_signals(
    left: Iterable[SignalRecord],
    right: Iterable[SignalRecord],
) -> dict[str, Any]:
    """Compare candidates by immutable setup/signal keys, not aggregate WR."""
    left_by_key = {item.setup_key: item for item in left}
    right_by_key = {item.setup_key: item for item in right}

    left_keys = set(left_by_key)
    right_keys = set(right_by_key)
    common = left_keys & right_keys

    changed = []
    for key in sorted(common):
        a = left_by_key[key]
        b = right_by_key[key]
        if (
            a.entry_time != b.entry_time
            or a.entry != b.entry
            or a.sl != b.sl
            or a.tp != b.tp
            or a.status != b.status
        ):
            changed.append({
                "setup_key": list(key),
                "left": asdict(a),
                "right": asdict(b),
            })

    return {
        "left_total": len(left_by_key),
        "right_total": len(right_by_key),
        "common": len(common),
        "left_only": len(left_keys - right_keys),
        "right_only": len(right_keys - left_keys),
        "changed_common": len(changed),
        "changed": changed,
    }


def write_jsonl(path, records: Iterable[Any]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(asdict(record), ensure_ascii=False, sort_keys=True))
            handle.write("\n")
