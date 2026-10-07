from __future__ import annotations

"""Explicit research-stage handoff contract.

A handoff proves that a declared Factory job produced an identified artifact
at one research station and that the caller explicitly routed that artifact to
the next station. It does not judge performance, define Strategy A geometry,
or authorize production.
"""

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .job_events import FactoryJobEvent, FactoryJobEventLedger
from .research_record import ResearchRecord


HANDOFF_ROUTES = {
    ("discovery", "stability"),
    ("stability", "validation"),
    ("stability", "robustness"),
    ("robustness", "holdout"),
    ("holdout", "forward"),
}


class ResearchHandoffError(ValueError):
    """Raised when a research handoff is not provenance-complete."""


def _canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@dataclass(frozen=True)
class ResearchHandoff:
    handoff_revision: str
    handoff_id: str
    job_id: str
    job_fingerprint: str
    source_station: str
    destination_station: str
    output_artifact: str
    dataset_content_sha256: str
    dataset_artifact_id: str
    source_event_fingerprint: str
    detail: str
    fingerprint: str

    def as_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        value = {
            "handoff_revision": self.handoff_revision,
            "handoff_id": self.handoff_id,
            "job_id": self.job_id,
            "job_fingerprint": self.job_fingerprint,
            "source_station": self.source_station,
            "destination_station": self.destination_station,
            "output_artifact": self.output_artifact,
            "dataset_content_sha256": self.dataset_content_sha256,
            "dataset_artifact_id": self.dataset_artifact_id,
            "source_event_fingerprint": self.source_event_fingerprint,
            "detail": self.detail,
        }
        if include_fingerprint:
            value["fingerprint"] = self.fingerprint
        return value

    def validate(self) -> None:
        if not self.handoff_id or not self.job_id or not self.output_artifact:
            raise ResearchHandoffError("handoff identity is incomplete")
        if (self.source_station, self.destination_station) not in HANDOFF_ROUTES:
            raise ResearchHandoffError("research handoff route is not declared")
        if len(self.job_fingerprint) != 64 or len(self.source_event_fingerprint) != 64:
            raise ResearchHandoffError("handoff fingerprints must be SHA-256")
        expected = hashlib.sha256(
            _canonical(self.as_dict(include_fingerprint=False)).encode("utf-8")
        ).hexdigest()
        if self.fingerprint != expected:
            raise ResearchHandoffError("handoff fingerprint mismatch")


def validate_evidence_bound_handoff(*, handoff: ResearchHandoff, record: ResearchRecord, source_event: FactoryJobEvent, dataset_content_sha256: str | None = None, dataset_artifact_id: str | None = None) -> None:
    handoff.validate()
    record.validate()
    source_event.validate()
    if handoff.job_id != record.run_id:
        raise ResearchHandoffError("handoff job_id does not match research record run_id")
    if handoff.job_fingerprint != source_event.job_fingerprint:
        raise ResearchHandoffError("handoff job_fingerprint does not match source job event")
    if source_event.research_run_fingerprint != record.run_fingerprint:
        raise ResearchHandoffError("source event is not bound to research run")
    if handoff.output_artifact != record.evidence_id:
        raise ResearchHandoffError("handoff artifact does not match research evidence_id")
    if handoff.source_event_fingerprint != source_event.event_fingerprint:
        raise ResearchHandoffError("handoff source event does not match declared source event")
    if source_event.event_type != "COMPLETED":
        raise ResearchHandoffError("handoff source event must be COMPLETED")
    if source_event.job_id != record.run_id:
        raise ResearchHandoffError("source event job_id does not match research record run_id")
    if source_event.station != handoff.source_station:
        raise ResearchHandoffError("source event station does not match handoff source station")
    if source_event.output_artifact != record.evidence_id:
        raise ResearchHandoffError("source event artifact does not match research evidence_id")
    if dataset_content_sha256 is not None and handoff.dataset_content_sha256 != dataset_content_sha256:
        raise ResearchHandoffError("handoff dataset SHA does not match declared dataset SHA")
    if dataset_artifact_id is not None and handoff.dataset_artifact_id != dataset_artifact_id:
        raise ResearchHandoffError("handoff artifact id does not match declared dataset artifact")


def build_research_handoff(
    *,
    events: FactoryJobEventLedger,
    job_id: str,
    source_station: str,
    destination_station: str,
    handoff_id: str | None = None,
    detail: str = "Validated research artifact handoff",
    record: ResearchRecord | None = None,
    dataset_content_sha256: str = "",
    dataset_artifact_id: str = "",
) -> ResearchHandoff:
    if (source_station, destination_station) not in HANDOFF_ROUTES:
        raise ResearchHandoffError("research handoff route is not declared")

    candidates = [
        event
        for event in events.for_job(job_id)
        if event.event_type == "COMPLETED"
        and event.station == source_station
        and event.output_artifact
    ]
    if not candidates:
        raise ResearchHandoffError(
            "source station has no completed job event with an output artifact"
        )

    event = candidates[-1]
    handoff = ResearchHandoff(
        handoff_revision="RESEARCH-HANDOFF-1",
        handoff_id=handoff_id or f"HANDOFF-{job_id}-{destination_station.upper()}",
        job_id=event.job_id,
        job_fingerprint=event.job_fingerprint,
        source_station=source_station,
        destination_station=destination_station,
        output_artifact=str(event.output_artifact),
        dataset_content_sha256=dataset_content_sha256,
        dataset_artifact_id=dataset_artifact_id,
        source_event_fingerprint=event.event_fingerprint,
        detail=detail,
        fingerprint="",
    )
    fingerprint = hashlib.sha256(
        _canonical(handoff.as_dict(include_fingerprint=False)).encode("utf-8")
    ).hexdigest()
    final = ResearchHandoff(**handoff.as_dict(include_fingerprint=False), fingerprint=fingerprint)
    final.validate()
    if record is not None:
        validate_evidence_bound_handoff(handoff=final, record=record, source_event=event, dataset_content_sha256=dataset_content_sha256, dataset_artifact_id=dataset_artifact_id)
    return final
