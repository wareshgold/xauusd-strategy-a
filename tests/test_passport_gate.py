from strategy_factory.manifest import StrategyManifest
from strategy_factory.models import StrategyPassport
from strategy_factory.passport_gate import evaluate_passport_eligibility
from strategy_factory.source_ledger import SourceResolutionLedger
from strategy_factory.sp2l_manifest import build_sp2l_research_manifest


def make_passport(manifest: StrategyManifest) -> StrategyPassport:
    return StrategyPassport(
        strategy_id=manifest.strategy_id,
        source_revision=manifest.revision,
        geometry_revision="GEOMETRY-PENDING",
        code_revision="CODE-PENDING",
        data_revision="DATA-PENDING",
        execution_model="TICK_FEASIBLE_RESEARCH_ONLY",
        parameter_set={"canonical": False},
    )


def test_sp2l_passport_is_not_eligible_while_source_is_blocked():
    manifest = build_sp2l_research_manifest()
    result = evaluate_passport_eligibility(
        make_passport(manifest),
        manifest,
        SourceResolutionLedger(),
    )

    assert result.source_status == "BLOCKED"
    assert result.frozen_geometry == "BLOCKED"
    assert result.canonical_strategy == "NOT_ELIGIBLE"
    assert result.production == "NOT_ELIGIBLE"
    assert result.blocking_reasons == (
        "SOURCE_READINESS_BLOCKED",
        "FROZEN_GEOMETRY_BLOCKED",
        "MANIFEST_NOT_CANONICAL_READY",
    )


def test_passport_gate_does_not_mutate_manifest_or_passport():
    manifest = build_sp2l_research_manifest()
    passport = make_passport(manifest)

    before_manifest = manifest.as_dict()
    before_passport = passport.as_dict()

    evaluate_passport_eligibility(
        passport,
        manifest,
        SourceResolutionLedger(),
    )

    assert manifest.as_dict() == before_manifest
    assert passport.as_dict() == before_passport
