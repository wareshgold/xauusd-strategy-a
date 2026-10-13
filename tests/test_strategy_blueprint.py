from dataclasses import replace
import hashlib
import json

import pytest

from strategy_factory.adapter_readiness import DataCapability
from strategy_factory.strategy_blueprint import (
    ExternalStrategyBlueprint,
    StrategyBlueprintError,
)
from strategy_factory.strategy_intake import StrategySourceIntake, StrategySourcePlatform
from strategy_factory.test_contract import DatasetRole, ExecutionSemantics, TestDataset


def make_intake():
    return StrategySourceIntake(
        intake_id="YT-GOLD-001",
        platform=StrategySourcePlatform.YOUTUBE,
        source_url="https://www.youtube.com/watch?v=abcdefghijk",
        source_title="Example strategy",
        publisher="Example channel",
        source_revision="video:abcdefghijk",
        captured_at_utc="2026-10-13T06:00:00Z",
        snapshot_uri="artifact://strategy-intake/YT-GOLD-001/transcript.txt",
        snapshot_sha256="a" * 64,
        strategy_claims=("Breakout entry after candle close",),
        unresolved_questions=(),
    )


def make_blueprint(**changes):
    base = ExternalStrategyBlueprint(
        blueprint_id="EXT-BREAKOUT-001",
        strategy_family="EXTERNAL_BREAKOUT",
        revision="R1",
        intake=make_intake(),
        rule_spec={
            "signal": "close_above_declared_range",
            "entry": "next_bar_open",
            "exit": "fixed_stop_and_target",
        },
        required_data=DataCapability.M1_OHLC,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        entry_semantics="NEXT_BAR_OPEN",
        exit_semantics="FIXED_STOP_TARGET",
        cost_model_fingerprint="cost-model-sha",
        fixed_parameters={"stop_multiple": 1.0},
        parameter_grid={"target_multiple": (1.0, 1.5, 2.0)},
        unresolved_questions=(),
        max_candidates=8,
    )
    return replace(base, **changes)


def make_dataset(role=DatasetRole.DEVELOPMENT, immutable=True):
    return TestDataset(
        dataset_id="EXT-M1-DEV-001",
        role=role,
        data_revision="DATA-REV-1",
        start="2026-01-01T00:00:00Z",
        end="2026-02-01T00:00:00Z",
        source="artifact://datasets/ext-m1-dev",
        immutable=immutable,
    )


def test_blueprint_fingerprint_is_deterministic_and_noncanonical():
    first = make_blueprint()
    second = make_blueprint()
    assert first.fingerprint == second.fingerprint
    payload = first.as_dict()
    assert payload["canonical"] is False
    assert payload["backtest_approved"] is False
    assert payload["forward_approved"] is False
    assert payload["production_eligible"] is False


def test_blueprint_fingerprint_binds_rule_spec_and_source_intake():
    first = make_blueprint()
    changed_rules = make_blueprint(rule_spec={"signal": "different"})
    changed_intake = make_blueprint(
        intake=replace(make_intake(), snapshot_sha256="b" * 64)
    )
    assert first.fingerprint != changed_rules.fingerprint
    assert first.fingerprint != changed_intake.fingerprint


def test_blueprint_creates_generic_external_candidate_plan_without_sp2l_source_resolution():
    blueprint = make_blueprint()
    plan = blueprint.to_candidate_plan(
        dataset=make_dataset(),
        dataset_content_sha256="c" * 64,
        execution_fingerprint="execution-sha",
    )
    candidates = plan.candidates()
    assert len(candidates) == 3
    assert plan.provenance_mode == "EXTERNAL"
    assert plan.source_resolution_fingerprint is None
    assert plan.external_source_fingerprint == blueprint.fingerprint
    assert all(candidate.provenance_mode == "EXTERNAL" for candidate in candidates)
    assert all(candidate.source_resolution_fingerprint is None for candidate in candidates)
    assert all(candidate.external_source_fingerprint == blueprint.fingerprint for candidate in candidates)


def test_unresolved_questions_block_plan_but_not_research_draft():
    blueprint = make_blueprint(
        unresolved_questions=("Stop placement is not specified",)
    )
    assert blueprint.research_draft_only
    assert blueprint.as_dict()["canonical"] is False
    with pytest.raises(StrategyBlueprintError, match="unresolved"):
        blueprint.to_candidate_plan(
            dataset=make_dataset(),
            dataset_content_sha256="c" * 64,
            execution_fingerprint="execution-sha",
        )


def test_candidate_plan_still_rejects_holdout_and_missing_execution_profile():
    blueprint = make_blueprint()
    with pytest.raises(StrategyBlueprintError, match="DEVELOPMENT"):
        blueprint.to_candidate_plan(
            dataset=make_dataset(role=DatasetRole.FRESH_HOLDOUT),
            dataset_content_sha256="c" * 64,
            execution_fingerprint="execution-sha",
        )
    with pytest.raises(StrategyBlueprintError, match="execution profile"):
        blueprint.to_candidate_plan(
            dataset=make_dataset(),
            dataset_content_sha256="c" * 64,
            execution_fingerprint="",
        )


def test_blueprint_parameter_grid_must_fit_declared_candidate_cap():
    blueprint = make_blueprint(
        parameter_grid={"target": tuple(range(10))},
        max_candidates=5,
    )
    with pytest.raises(StrategyBlueprintError, match="limit"):
        blueprint.to_candidate_plan(
            dataset=make_dataset(),
            dataset_content_sha256="c" * 64,
            execution_fingerprint="execution-sha",
        )


def test_external_candidate_matrix_still_requires_matching_dataset_bytes(tmp_path):
    blueprint = make_blueprint()
    data = b"external candidate development data\n"
    path = tmp_path / "dataset.bin"
    path.write_bytes(data)
    plan = blueprint.to_candidate_plan(
        dataset=make_dataset(),
        dataset_content_sha256=hashlib.sha256(data).hexdigest(),
        execution_fingerprint="execution-sha",
    )
    from strategy_factory.candidate_lab import CandidateObservation, run_candidate_matrix

    def execute(candidate, dataset_bytes):
        metrics = {
            "candidate_fingerprint": candidate.candidate_fingerprint,
            "trades": 30,
            "wins": 18,
            "losses": 12,
            "ambiguous": 0,
            "net_pnl_cash": 12.0,
            "profit_factor": 1.4,
            "max_drawdown_cash": 5.0,
            "costs_included": True,
        }
        result_fingerprint = hashlib.sha256(json.dumps(
            metrics, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")).hexdigest()
        return CandidateObservation(
            candidate=candidate, trades=30, wins=18, losses=12, ambiguous=0,
            net_pnl_cash=12.0, profit_factor=1.4, max_drawdown_cash=5.0,
            costs_included=True, result_fingerprint=result_fingerprint,
        )

    results = run_candidate_matrix(plan, execute, dataset_artifact_path=path)
    assert len(results) == 3
    assert all(row.candidate.provenance_mode == "EXTERNAL" for row in results)
    assert all(row.candidate.source_resolution_fingerprint is None for row in results)



def test_intake_uncertainty_cannot_be_silently_dropped_from_blueprint():
    intake = replace(
        make_intake(),
        unresolved_questions=("Stop anchor not specified",),
    )
    with pytest.raises(StrategyBlueprintError, match="must remain unresolved"):
        make_blueprint(intake=intake, unresolved_questions=())


def test_explicit_resolution_rationale_is_bound_into_blueprint_fingerprint():
    intake = replace(
        make_intake(),
        unresolved_questions=("Stop anchor not specified",),
    )
    resolved = make_blueprint(
        intake=intake,
        resolved_source_questions={
            "Stop anchor not specified": "A separately recorded research interpretation was selected."
        },
    )
    plan = resolved.to_candidate_plan(
        dataset=make_dataset(),
        dataset_content_sha256="c" * 64,
        execution_fingerprint="execution-sha",
    )
    changed = make_blueprint(
        intake=intake,
        resolved_source_questions={
            "Stop anchor not specified": "A different interpretation was selected."
        },
    )
    assert plan.provenance_mode == "EXTERNAL"
    assert resolved.fingerprint != changed.fingerprint
