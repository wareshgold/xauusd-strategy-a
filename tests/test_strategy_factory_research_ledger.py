from dataclasses import replace
from hashlib import sha256

import pytest

from strategy_factory.research_ledger import (
    ZERO_HASH,
    EvidenceStatus,
    ExperimentStatus,
    create_record,
    verify_ledger,
)


def digest(value):
    return sha256(value.encode()).hexdigest()


def record(record_id="r1", sequence=1, previous=ZERO_HASH, **kwargs):
    defaults = dict(
        record_id=record_id,
        sequence=sequence,
        experiment_key="fixture-pair-01",
        hypothesis_id="H-ENTRY-01",
        hypothesis_version="v1",
        input_sha256=digest("frozen-inputs"),
        code_sha256=digest("code"),
        status=ExperimentStatus.PLANNED,
        evidence_status=EvidenceStatus.SYNTHETIC_ONLY,
        result_summary="Synthetic fixture result; not source confirmation.",
        evidence_refs=("fixture://input",),
        counterexample_refs=(),
        prior_failure_refs=(),
        previous_record_sha256=previous,
    )
    defaults.update(kwargs)
    return create_record(**defaults)


def test_record_hash_and_chain_are_deterministic():
    first = record()
    again = record()
    assert first == again
    assert verify_ledger([first], expected_tip_sha256=first.record_sha256, expected_record_count=1) == first.record_sha256


def test_append_links_to_previous_record_hash():
    first = record()
    second = record(
        record_id="r2", sequence=2, previous=first.record_sha256,
        status=ExperimentStatus.FAIL, result_summary="Counterexample disproved this candidate interpretation.",
        counterexample_refs=("fixture://counterexample-1",))
    assert verify_ledger([first, second]) == second.record_sha256


def test_failure_must_remain_referenced_in_later_retest():
    first = record(status=ExperimentStatus.FAIL, result_summary="Prior test failed.")
    second = record(
        record_id="r2", sequence=2, previous=first.record_sha256,
        status=ExperimentStatus.PASS, result_summary="New run passed; prior failure retained.",
        prior_failure_refs=("r1",))
    assert verify_ledger([first, second]) == second.record_sha256


def test_prior_failure_reference_cannot_point_to_success():
    first = record(status=ExperimentStatus.PASS, result_summary="Pass.")
    second = record(record_id="r2", sequence=2, previous=first.record_sha256,
                    prior_failure_refs=("r1",))
    with pytest.raises(ValueError, match="prior non-success"):
        verify_ledger([first, second])


def test_broken_previous_hash_fails_closed():
    first = record()
    second = record(record_id="r2", sequence=2, previous=digest("wrong"))
    with pytest.raises(ValueError, match="append-only chain"):
        verify_ledger([first, second])


def test_modified_result_without_rehash_is_detected():
    first = record()
    tampered = replace(first, result_summary="edited after the run")
    with pytest.raises(ValueError, match="does not match"):
        verify_ledger([tampered])


def test_pinned_tip_detects_truncated_ledger():
    first = record()
    second = record(record_id="r2", sequence=2, previous=first.record_sha256)
    with pytest.raises(ValueError, match="pinned tip"):
        verify_ledger([first], expected_tip_sha256=second.record_sha256)


def test_pinned_count_detects_truncated_ledger():
    first = record()
    second = record(record_id="r2", sequence=2, previous=first.record_sha256)
    with pytest.raises(ValueError, match="pinned count"):
        verify_ledger([first], expected_record_count=2)


def test_sequence_gap_is_rejected():
    first = record(sequence=2)
    with pytest.raises(ValueError, match="contiguous"):
        verify_ledger([first])


def test_canonical_or_production_authority_is_rejected():
    first = record()
    with pytest.raises(ValueError, match="cannot authorize"):
        verify_ledger([replace(first, canonical_authorized=True)])


def test_input_hash_must_be_sha256():
    with pytest.raises(ValueError, match="input_sha256"):
        record(input_sha256="not-a-hash")


def test_counterexamples_are_part_of_hashed_record():
    first = record(counterexample_refs=("fixture://counterexample-a",))
    changed = replace(first, counterexample_refs=("fixture://counterexample-b",))
    with pytest.raises(ValueError, match="does not match"):
        verify_ledger([changed])
