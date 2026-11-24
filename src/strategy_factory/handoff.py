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
    ("validation", "robustness"),
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
    source_output_artifact_id: str | None = None
    source_output_artifact_role: str | None = None
    source_output_artifact_sha256: str | None = None
    source_output_artifact_byte_size: int | None = None

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
        if self.source_output_artifact_id is not None:
            value.update({
                "source_output_artifact_id": self.source_output_artifact_id,
                "source_output_artifact_role": self.source_output_artifact_role,
                "source_output_artifact_sha256": self.source_output_artifact_sha256,
                "source_output_artifact_byte_size": self.source_output_artifact_byte_size,
            })
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
        output_values = (self.source_output_artifact_id, self.source_output_artifact_role,
                         self.source_output_artifact_sha256, self.source_output_artifact_byte_size)
        if any(value is not None for value in output_values):
            if any(value is None for value in output_values):
                raise ResearchHandoffError("handoff source output artifact binding is incomplete")
            if not self.source_output_artifact_id or not self.source_output_artifact_role:
                raise ResearchHandoffError("handoff source output artifact identity is invalid")
            if (not isinstance(self.source_output_artifact_sha256, str) or
                    len(self.source_output_artifact_sha256) != 64 or
                    any(ch not in "0123456789abcdef" for ch in self.source_output_artifact_sha256)):
                raise ResearchHandoffError("handoff source output artifact SHA-256 is invalid")
            if (isinstance(self.source_output_artifact_byte_size, bool) or
                    not isinstance(self.source_output_artifact_byte_size, int) or self.source_output_artifact_byte_size < 0):
                raise ResearchHandoffError("handoff source output artifact byte size is invalid")
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
    if record.output_artifact_id is not None:
        if handoff.source_output_artifact_id != record.output_artifact_id:
            raise ResearchHandoffError("handoff output artifact id does not match research record")
        if handoff.source_output_artifact_role != record.output_artifact_role:
            raise ResearchHandoffError("handoff output artifact role does not match research record")
        if handoff.source_output_artifact_sha256 != record.output_artifact_sha256:
            raise ResearchHandoffError("handoff output artifact SHA does not match research record")
        if handoff.source_output_artifact_byte_size != record.output_artifact_byte_size:
            raise ResearchHandoffError("handoff output artifact size does not match research record")
    elif any(value is not None for value in (
        handoff.source_output_artifact_id, handoff.source_output_artifact_role,
        handoff.source_output_artifact_sha256, handoff.source_output_artifact_byte_size,
    )):
        raise ResearchHandoffError("handoff declares an output artifact absent from research record")
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
    if record.record_revision == "RESEARCH-RECORD-2":
        if handoff.dataset_content_sha256 != record.dataset_content_sha256:
            raise ResearchHandoffError("handoff dataset SHA does not match research record binding")
        if handoff.dataset_artifact_id != record.dataset_artifact_id:
            raise ResearchHandoffError("handoff artifact id does not match research record binding")
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

    if record is not None:
        record.validate()
        if record.run_id != job_id:
            raise ResearchHandoffError("handoff job_id does not match research record run_id")
        if record.record_revision == "RESEARCH-RECORD-2":
            if dataset_content_sha256 and dataset_content_sha256 != record.dataset_content_sha256:
                raise ResearchHandoffError("declared handoff dataset SHA conflicts with research record binding")
            if dataset_artifact_id and dataset_artifact_id != record.dataset_artifact_id:
                raise ResearchHandoffError("declared handoff artifact id conflicts with research record binding")
            dataset_content_sha256 = record.dataset_content_sha256
            dataset_artifact_id = record.dataset_artifact_id

    job_events = events.for_job(job_id)
    # A contradictory terminal history must never be promoted through a
    # handoff, even if one of its events looks like a successful completion.
    if any(event.event_type == "FAILED" for event in job_events) and any(
        event.event_type == "COMPLETED" for event in job_events
    ):
        raise ResearchHandoffError(
            "source job has conflicting terminal events; manual reconciliation required"
        )

    source_completions = [
        event
        for event in job_events
        if event.event_type == "COMPLETED" and event.station == source_station
    ]
    if len(source_completions) > 1:
        raise ResearchHandoffError(
            "source job has duplicate completion events for the declared station; "
            "manual reconciliation required"
        )

    candidates = [
        event
        for event in source_completions
        if event.output_artifact
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
        source_output_artifact_id=record.output_artifact_id if record is not None else None,
        source_output_artifact_role=record.output_artifact_role if record is not None else None,
        source_output_artifact_sha256=record.output_artifact_sha256 if record is not None else None,
        source_output_artifact_byte_size=record.output_artifact_byte_size if record is not None else None,
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
