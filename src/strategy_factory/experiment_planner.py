"""Stable research hypothesis/fixture registries and PLANNED-only experiment planner.

Registry entries identify questions and existing synthetic tests; they do not
assert source truth, SP2L geometry, broker semantics, or experiment outcomes.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from strategy_factory.research_ledger import (
    ZERO_HASH,
    EvidenceStatus,
    ExperimentRecord,
    ExperimentStatus,
    create_record,
)


@dataclass(frozen=True)
class HypothesisSpec:
    hypothesis_id: str
    version: str
    question: str
    source_status: str = "UNRESOLVED"
    canonical_authorized: bool = False

    def validate(self) -> None:
        if not self.hypothesis_id.strip() or not self.version.strip() or not self.question.strip():
            raise ValueError("hypothesis ID, version, and question are required")
        if self.source_status not in {"UNRESOLVED", "SOURCE_REVIEW_REQUIRED", "SOURCE_CITATION_RECORDED"}:
            raise ValueError("unsupported source status")
        if self.canonical_authorized:
            raise ValueError("registry cannot authorize canonical rules")


@dataclass(frozen=True)
class FixtureSpec:
    fixture_id: str
    hypothesis_id: str
    test_reference: str
    purpose: str

    def validate(self) -> None:
        if not all(value.strip() for value in (
            self.fixture_id, self.hypothesis_id, self.test_reference, self.purpose
        )):
            raise ValueError("fixture ID, hypothesis ID, test reference, and purpose are required")


# These are research questions about evidence handling, not candidate trading rules.
HYPOTHESIS_REGISTRY: tuple[HypothesisSpec, ...] = (
    HypothesisSpec(
        "H-TICK-ORDER-001", "v1",
        "Does preserving source-row order retain same-millisecond quote ordering without deduplication?",
    ),
    HypothesisSpec(
        "H-OHLC-ORDER-001", "v1",
        "Does OHLC-only contact with both SL and TP remain ambiguous without an explicit event sequence?",
    ),
    HypothesisSpec(
        "H-BAR-COMPLETION-001", "v1",
        "Is a forming bar excluded unless completion is explicitly asserted?",
    ),
)

FIXTURE_REGISTRY: tuple[FixtureSpec, ...] = (
    FixtureSpec(
        "FX-TICK-SAME-MS-ORDER-001", "H-TICK-ORDER-001",
        "tests/test_strategy_factory_synthetic_fixtures.py::test_equal_timestamp_quotes_preserve_input_order_without_deduplication",
        "Preserve same-millisecond source order and all rows.",
    ),
    FixtureSpec(
        "FX-OHLC-SL-TP-AMBIGUOUS-001", "H-OHLC-ORDER-001",
        "tests/test_strategy_factory_synthetic_fixtures.py::test_ohlc_touching_both_sl_and_tp_is_ambiguous_without_ordered_ticks",
        "Keep first-touch outcome unresolved when OHLC touches both levels.",
    ),
    FixtureSpec(
        "FX-FORMING-BAR-EXCLUDED-001", "H-BAR-COMPLETION-001",
        "tests/test_strategy_factory_synthetic_fixtures.py::test_forming_bar_is_not_selected_as_completed",
        "Reject a latest bar without explicit completed=true.",
    ),
)


def _unique_registry(items: Iterable[object], id_attr: str, label: str) -> dict[str, object]:
    rows = tuple(items)
    result: dict[str, object] = {}
    for item in rows:
        getattr(item, "validate")()
        item_id = getattr(item, id_attr)
        if item_id in result:
            raise ValueError(f"duplicate {label} ID: {item_id}")
        result[item_id] = item
    return result


def validate_registries(
    hypotheses: Iterable[HypothesisSpec] = HYPOTHESIS_REGISTRY,
    fixtures: Iterable[FixtureSpec] = FIXTURE_REGISTRY,
) -> tuple[dict[str, HypothesisSpec], dict[str, FixtureSpec]]:
    hypothesis_map = _unique_registry(hypotheses, "hypothesis_id", "hypothesis")
    fixture_map = _unique_registry(fixtures, "fixture_id", "fixture")
    for fixture in fixture_map.values():
        if fixture.hypothesis_id not in hypothesis_map:
            raise ValueError(f"fixture {fixture.fixture_id} references unknown hypothesis {fixture.hypothesis_id}")
    return hypothesis_map, fixture_map


def plan_experiments(
    *,
    fixture_ids: Iterable[str],
    input_sha256: str,
    code_sha256: str,
    first_sequence: int = 1,
    previous_record_sha256: str = ZERO_HASH,
    hypotheses: Iterable[HypothesisSpec] = HYPOTHESIS_REGISTRY,
    fixtures: Iterable[FixtureSpec] = FIXTURE_REGISTRY,
) -> tuple[ExperimentRecord, ...]:
    """Create deterministic PLANNED records only; never execute or infer results."""
    hypothesis_map, fixture_map = validate_registries(hypotheses, fixtures)
    selected = tuple(fixture_ids)
    if not selected:
        raise ValueError("at least one fixture ID is required")
    if len(set(selected)) != len(selected):
        raise ValueError("fixture IDs in a plan cannot repeat")
    unknown = [fixture_id for fixture_id in selected if fixture_id not in fixture_map]
    if unknown:
        raise ValueError(f"unknown fixture IDs: {', '.join(unknown)}")
    if first_sequence < 1:
        raise ValueError("first_sequence must be positive")

    records: list[ExperimentRecord] = []
    previous_hash = previous_record_sha256
    for offset, fixture_id in enumerate(selected):
        fixture = fixture_map[fixture_id]
        hypothesis = hypothesis_map[fixture.hypothesis_id]
        record = create_record(
            record_id=f"PLAN-{fixture.fixture_id}",
            sequence=first_sequence + offset,
            experiment_key=fixture.fixture_id,
            hypothesis_id=hypothesis.hypothesis_id,
            hypothesis_version=hypothesis.version,
            input_sha256=input_sha256,
            code_sha256=code_sha256,
            status=ExperimentStatus.PLANNED,
            evidence_status=EvidenceStatus.SYNTHETIC_ONLY,
            result_summary=(
                f"PLANNED only; not executed. Intended fixture: {fixture.test_reference}. "
                f"Question: {hypothesis.question} No source or canonical claim."
            ),
            evidence_refs=(f"fixture://{fixture.fixture_id}", fixture.test_reference),
            previous_record_sha256=previous_hash,
        )
        records.append(record)
        previous_hash = record.record_sha256
    return tuple(records)
