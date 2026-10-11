import hashlib
from dataclasses import replace

import pytest

from strategy_factory.candidate_lab import (
    CandidateLabError,
    CandidateObservation,
    CandidatePlan,
    assess_candidates,
    run_candidate_matrix,
)
from strategy_factory.test_contract import DatasetRole, ExecutionSemantics, TestDataset


def make_plan(*, role=DatasetRole.DEVELOPMENT, immutable=True, data_sha="a" * 64):
    return CandidatePlan(
        plan_id="EXIT-MATRIX-001",
        strategy_family="SP2L-V3-RR2-TRAIL4",
        base_revision="REV-FROZEN-1",
        dataset=TestDataset(
            dataset_id="XAU-M1-DEV-001",
            role=role,
            data_revision="XAU-M1-COPY-1",
            start="2026-10-01T00:00:00Z",
            end="2026-10-03T00:00:00Z",
            source="artifact://xau/m1/dev",
            immutable=immutable,
        ),
        dataset_content_sha256=data_sha,
        execution_semantics=ExecutionSemantics.TICK_FEASIBLE,
        execution_fingerprint="execution-profile-sha",
        fixed_parameters={"tp_r": 2.0, "sl_anchor_profile": "frozen-source-profile"},
        parameter_grid={
            "trailing_mode": ("OFF", "TRAIL"),
            "trailing_distance": (2, 4, 10),
        },
        geometry_fingerprint="frozen-geometry-sha",
        source_resolution_fingerprint="source-resolution-sha",
        max_candidates=8,
    )


def make_observation(candidate, *, pnl, wins=20, losses=10, ambiguous=0, trades=30, dd=5.0):
    return CandidateObservation(
        candidate=candidate,
        trades=trades,
        wins=wins,
        losses=losses,
        ambiguous=ambiguous,
        net_pnl_cash=pnl,
        profit_factor=1.5,
        max_drawdown_cash=dd,
        costs_included=True,
        result_fingerprint=f"result-{candidate.candidate_id}",
    )


def test_matrix_is_deterministic_and_explicitly_finite():
    plan = make_plan()
    first = plan.candidates()
    second = plan.candidates()
    assert len(first) == 6
    assert [c.candidate_fingerprint for c in first] == [
        c.candidate_fingerprint for c in second
    ]
    assert first[0].parameters["trailing_mode"] == "OFF"
    assert first[0].parameters["trailing_distance"] == 2
    assert all(c.geometry_fingerprint == "frozen-geometry-sha" for c in first)


def test_optimization_rejects_holdout_or_mutable_dataset():
    with pytest.raises(CandidateLabError, match="DEVELOPMENT"):
        make_plan(role=DatasetRole.FRESH_HOLDOUT).candidates()
    with pytest.raises(CandidateLabError, match="immutable"):
        make_plan(immutable=False).candidates()


def test_matrix_cap_rejects_unbounded_search():
    plan = make_plan()
    too_small = CandidatePlan(**{
        **plan.__dict__,
        "max_candidates": 5,
    })
    with pytest.raises(CandidateLabError, match="limit"):
        too_small.candidates()


def test_plan_rejects_non_hex_dataset_sha256():
    with pytest.raises(CandidateLabError, match="lowercase hexadecimal"):
        make_plan(data_sha="g" * 64).candidates()


def test_assessment_ranks_by_declared_objective_but_only_shortlists():
    candidates = make_plan().candidates()
    observations = [
        make_observation(candidates[0], pnl=12.0, trades=30),
        make_observation(candidates[1], pnl=20.0, wins=19, losses=10, trades=29),
        make_observation(candidates[2], pnl=16.0, wins=25, losses=10, trades=35),
    ]
    assessment = assess_candidates(
        observations,
        objective="NET_PNL_AFTER_COSTS",
        minimum_trades=30,
        validation_shortlist_size=2,
    )
    payload = assessment.as_dict()
    assert payload["candidate_rows"][0]["candidate_id"] == candidates[1].candidate_id
    assert payload["recommended_for_validation"] == [
        candidates[2].candidate_id,
        candidates[0].candidate_id,
    ]
    assert payload["winner"] is None
    assert payload["production_eligible"] is False
    assert payload["multiple_candidates_tested"] == 3


def test_assessment_fails_closed_on_mismatched_data_or_costs():
    candidates = make_plan().candidates()
    first = make_observation(candidates[0], pnl=10.0)
    other_plan = make_plan(data_sha="b" * 64)
    mismatched = make_observation(other_plan.candidates()[1], pnl=12.0)
    with pytest.raises(CandidateLabError, match="same dataset"):
        assess_candidates([first, mismatched], objective="NET_PNL_AFTER_COSTS")

    no_costs = CandidateObservation(
        candidate=candidates[1],
        trades=30,
        wins=20,
        losses=10,
        ambiguous=0,
        net_pnl_cash=11.0,
        profit_factor=1.2,
        max_drawdown_cash=6.0,
        costs_included=False,
        result_fingerprint="missing-costs",
    )
    with pytest.raises(CandidateLabError, match="net of"):
        assess_candidates([first, no_costs], objective="NET_PNL_AFTER_COSTS")



def _verified_dataset(tmp_path):
    payload = b"synthetic fixture bytes for dataset identity verification\n"
    artifact_path = tmp_path / "development-dataset.bin"
    artifact_path.write_bytes(payload)
    return artifact_path, hashlib.sha256(payload).hexdigest()


def test_matrix_runner_executes_every_candidate_in_stable_order(tmp_path):
    artifact_path, data_sha = _verified_dataset(tmp_path)
    plan = make_plan(data_sha=data_sha)
    seen = []

    def execute(candidate, dataset_bytes):
        assert dataset_bytes == artifact_path.read_bytes()
        seen.append(candidate.candidate_id)
        return make_observation(candidate, pnl=1.0)

    results = run_candidate_matrix(
        plan, execute, dataset_artifact_path=artifact_path
    )
    assert seen == [candidate.candidate_id for candidate in plan.candidates()]
    assert [row.candidate.candidate_id for row in results] == seen


def test_matrix_runner_rejects_dataset_artifact_sha_mismatch(tmp_path):
    artifact_path, _ = _verified_dataset(tmp_path)
    plan = make_plan(data_sha="b" * 64)

    with pytest.raises(CandidateLabError, match="bytes do not match"):
        run_candidate_matrix(
            plan, lambda candidate, dataset_bytes: make_observation(candidate, pnl=1.0),
            dataset_artifact_path=artifact_path,
        )


def test_matrix_runner_rejects_dataset_mutation_during_execution(tmp_path):
    artifact_path, data_sha = _verified_dataset(tmp_path)
    plan = make_plan(data_sha=data_sha)
    called = False

    def execute(candidate, dataset_bytes):
        nonlocal called
        if not called:
            artifact_path.write_bytes(b"mutated dataset bytes\n")
            called = True
        return make_observation(candidate, pnl=1.0)

    with pytest.raises(CandidateLabError, match="changed during candidate execution"):
        run_candidate_matrix(
            plan, execute, dataset_artifact_path=artifact_path
        )


def test_matrix_runner_rejects_adapter_result_for_another_candidate(tmp_path):
    artifact_path, data_sha = _verified_dataset(tmp_path)
    plan = make_plan(data_sha=data_sha)
    candidates = plan.candidates()

    def execute(candidate, dataset_bytes):
        return make_observation(candidates[-1], pnl=1.0)

    with pytest.raises(CandidateLabError, match="different candidate"):
        run_candidate_matrix(
            plan, execute, dataset_artifact_path=artifact_path
        )



@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("geometry_fingerprint", "tampered-geometry", "geometry fingerprint"),
        (
            "source_resolution_fingerprint",
            "tampered-source-resolution",
            "source-resolution fingerprint",
        ),
    ],
)
def test_matrix_runner_rejects_altered_geometry_or_source_provenance(
    tmp_path, field, value, message
):
    artifact_path, data_sha = _verified_dataset(tmp_path)
    plan = make_plan(data_sha=data_sha)

    def execute(candidate, dataset_bytes):
        altered_candidate = replace(candidate, **{field: value})
        return make_observation(altered_candidate, pnl=1.0)

    with pytest.raises(CandidateLabError, match=message):
        run_candidate_matrix(
            plan, execute, dataset_artifact_path=artifact_path
        )
