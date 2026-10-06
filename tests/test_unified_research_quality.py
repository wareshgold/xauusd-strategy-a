from dataclasses import replace
import hashlib, json
import pytest

from strategy_factory.comparison_validation_gate import evaluate_comparison_validation_gate
from strategy_factory.multiple_comparison import adjust_p_values
from strategy_factory.research_comparison import ComparisonObservation, ResearchComparison
from strategy_factory.research_acceptance import evaluate_research_acceptance
from strategy_factory.research_evidence_bundle import bind_research_evidence_bundle
from strategy_factory.research_evidence_ledger import ResearchEvidenceLedger
from strategy_factory.research_record import ResearchRecord
from strategy_factory.statistical_comparison_evidence import bind_statistical_comparison_evidence
from strategy_factory.statistical_comparison_evidence_ledger import StatisticalComparisonEvidenceLedger
from strategy_factory.statistical_comparison_governance import StatisticalComparisonUsageLedger
from strategy_factory.statistical_evidence import bind_statistical_evidence
from strategy_factory.stability import evaluate_stability, StabilitySegment
from strategy_factory.stability_evidence import bind_stability_evidence
from strategy_factory.unified_research_quality import UnifiedResearchQualityError, evaluate_unified_research_quality
from strategy_factory.statistics import ResearchMetrics, evaluate_statistical_validation
from strategy_factory.test_contract import DatasetRole
from tests.test_research_record import chain


def comparison():
    base = ComparisonObservation("base", "r"*64, "b"*64, 10, .5, .2, None, .1, .3)
    cand = ComparisonObservation("candidate", "c"*64, "d"*64, 10, .6, .3, None, .2, .4)
    x = ResearchComparison("REV", "SP2L", "R1", "DEVELOPMENT", base, (cand,), 1, (.1,), (.1,), (None,), "")
    fp = hashlib.sha256(json.dumps(x._fingerprint_payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return replace(x, fingerprint=fp)


def full_chain():
    run, raw, snapshot, audit, provenance = chain("DEVELOPMENT")
    record = ResearchRecord.from_components(run, raw, snapshot, audit, provenance)
    stat = bind_statistical_evidence(record, evaluate_statistical_validation(raw.metrics, role=DatasetRole.DEVELOPMENT, trade_returns_r=(1.0,)))
    stability = bind_stability_evidence(record, evaluate_stability((StabilitySegment("S1","seg",1,1.0,1.0),)))
    bundle = bind_research_evidence_bundle(record, stat, stability)
    rledger = ResearchEvidenceLedger(); rledger.record(bundle)
    acceptance = evaluate_research_acceptance(record, stat, stability, bundle, rledger)
    comp = comparison(); adj = adjust_p_values((.01,), method="HOLM"); ce = bind_statistical_comparison_evidence(comp, adj)
    cledger = StatisticalComparisonEvidenceLedger(); cledger.record(ce)
    gate = evaluate_comparison_validation_gate(comp, adj, ce, cledger, StatisticalComparisonUsageLedger())
    return record, stat, stability, bundle, rledger, acceptance, gate


def test_unified_quality_passes():
    record, stat, stability, bundle, ledger, acceptance, gate = full_chain()
    result = evaluate_unified_research_quality(
        record, stat, stability, bundle, ledger, acceptance, gate
    )
    assert result.accepted is True
    assert result.comparison_validated is True
    result.validate()


def test_unified_quality_rejects_evidence_mismatch():
    record, _, _, bundle, ledger, acceptance, gate = full_chain()
    stat = bind_statistical_evidence(record, evaluate_statistical_validation(
        ResearchMetrics(
            trades=1, decisive_trades=1, wins=1, losses=0, ambiguous=0,
            win_rate=1.0, net_r=2.0, profit_factor=None, max_drawdown_r=0.0,
            gross_profit_r=2.0, gross_loss_r=0.0
        ),
        role=DatasetRole.DEVELOPMENT, trade_returns_r=(2.0,)
    ))
    stability = bind_stability_evidence(record, evaluate_stability((StabilitySegment("S1","seg",1,2.0,1.0),)))
    with pytest.raises(UnifiedResearchQualityError):
        evaluate_unified_research_quality(record, stat, stability, bundle, ledger, acceptance, gate)


def test_unified_quality_rejects_non_pass_comparison():
    record, _, _, bundle, ledger, acceptance, gate = full_chain()
    bad = replace(
        gate,
        status="BLOCKED",
        blocking_reasons=("blocked",),
    )
    with pytest.raises(UnifiedResearchQualityError):
        evaluate_unified_research_quality(record, None, None, bundle, ledger, acceptance, bad)
