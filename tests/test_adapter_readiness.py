import pytest

from strategy_factory.adapter_readiness import (
    AdapterReadinessError,
    AdapterStatus,
    DataCapability,
    StrategyAdapterManifest,
    assess_adapter_readiness,
)


def manifest(
    strategy_id,
    *,
    required_data=DataCapability.M1_OHLC,
    forming=False,
    entry="bar-close-trigger",
    exit="SL-TP-M1-replay",
    cost="cost-model-v1",
    ledger=True,
    sha="a" * 40,
):
    return StrategyAdapterManifest(
        strategy_id=strategy_id,
        strategy_revision="revision-1",
        source_repository="owner/repo",
        source_path="strategy.py",
        source_blob_sha=sha,
        implementation_role="RESEARCH_REFERENCE",
        required_data=required_data,
        uses_forming_candle=forming,
        entry_semantics=entry,
        exit_semantics=exit,
        cost_model_fingerprint=cost,
        supports_trade_ledger=ledger,
    )


def test_alireza_live_semantics_are_blocked_on_m1_ohlc():
    report = assess_adapter_readiness(
        baseline=manifest("INTERNAL"),
        challenger=manifest(
            "ALIREZA",
            required_data=DataCapability.TICK_BID_ASK,
            forming=True,
            entry="forming-candle-low-high",
            exit="source-live-management",
            sha="b" * 40,
        ),
        dataset_capability=DataCapability.M1_OHLC,
        common_execution_fingerprint="same-profile",
    )
    assert report.status is AdapterStatus.BLOCKED
    assert "DATA_CAPABILITY_MISMATCH: tick Bid/Ask data required" in report.reasons
    assert "FORMING_CANDLE_PATH_UNAVAILABLE: M1 OHLC cannot reconstruct intrabar state" in report.reasons
    assert report.as_dict()["winner"] is None
    assert report.as_dict()["production_eligible"] is False


def test_adapter_readiness_blocks_mismatched_execution_costs_and_missing_ledger():
    report = assess_adapter_readiness(
        baseline=manifest("INTERNAL", cost="cost-a"),
        challenger=manifest("ALIREZA", entry="retrace-entry", exit="source-exit",
                            cost="cost-b", ledger=False, sha="b" * 40),
        dataset_capability=DataCapability.M1_OHLC,
        common_execution_fingerprint=None,
    )
    assert report.status is AdapterStatus.BLOCKED
    assert "COMMON_EXECUTION_PROFILE_MISSING" in report.reasons
    assert "ENTRY_SEMANTICS_DIFFER" in report.reasons
    assert "EXIT_SEMANTICS_DIFFER" in report.reasons
    assert "COST_MODELS_DIFFER" in report.reasons
    assert "TRADE_LEDGER_UNAVAILABLE" in report.reasons


def test_adapter_readiness_can_only_report_ready_when_contracts_match():
    report = assess_adapter_readiness(
        baseline=manifest("INTERNAL"),
        challenger=manifest("ALIREZA", sha="b" * 40),
        dataset_capability=DataCapability.M1_OHLC,
        common_execution_fingerprint="shared-frozen-profile",
    )
    assert report.status is AdapterStatus.READY
    assert report.reasons == ()
    assert report.allowed_use == "RESEARCH_PREFLIGHT_ONLY"


def test_adapter_manifest_rejects_missing_source_sha():
    bad = manifest("INTERNAL", sha="short")
    with pytest.raises(AdapterReadinessError, match="Git blob SHA"):
        bad.validate()
