from __future__ import annotations

from .manifest import (
    EvidenceRecord,
    EvidenceStatus,
    RuleAuthority,
    StrategyManifest,
    StrategyRule,
    UnresolvedQuestion,
)


def build_sp2l_research_manifest() -> StrategyManifest:
    """Source-aligned SP2L research manifest.

    This records source meaning and unresolved geometry only. It deliberately
    does not invent execution semantics or promote research parameters to
    canonical rules.
    """
    evidence = [
        EvidenceRecord(
            evidence_id="C01-PGAP",
            rule_id="SP2L.PGAP",
            status=EvidenceStatus.SOURCE_CONFIRMED,
            statement="P.GAP is distinct from a Common GAP; a valid BO is a P-Gap.",
            source_reference="C01",
        ),
        EvidenceRecord(
            evidence_id="F12-TRIGGER",
            rule_id="SP2L.F12",
            status=EvidenceStatus.PARTIALLY_RESOLVED,
            statement=(
                "BUY retraces to the previous candle Low; SELL retraces to "
                "the previous candle High."
            ),
            source_reference="F12",
            unresolved_questions=(
                "SP2L.F12.Q1",
                "SP2L.F12.Q2",
                "SP2L.F12.Q3",
                "SP2L.F12.Q4",
            ),
        ),
        EvidenceRecord(
            evidence_id="F13-2X",
            rule_id="SP2L.F13",
            status=EvidenceStatus.SOURCE_CONFIRMED,
            statement="2X is a secondary entry at 50% of the Entry-SL distance.",
            source_reference="F13",
        ),
        EvidenceRecord(
            evidence_id="F10-SL",
            rule_id="SP2L.F10",
            status=EvidenceStatus.PARTIALLY_RESOLVED,
            statement="The stop is behind the candle where the Spike started.",
            source_reference="F10",
            unresolved_questions=("SP2L.F10.Q1",),
        ),
        EvidenceRecord(
            evidence_id="C04-TEMPLATE",
            rule_id="SP2L.TRADE_TEMPLATE",
            status=EvidenceStatus.SOURCE_CONFIRMED,
            statement="The template shows SL, Entry, TP1, TP2 and 2X.",
            source_reference="C04",
        ),
        EvidenceRecord(
            evidence_id="C05-MA50",
            rule_id="SP2L.MA_FILTER",
            status=EvidenceStatus.SOURCE_CONFIRMED,
            statement="C05 references the 15-minute MA50.",
            source_reference="C05",
        ),
        EvidenceRecord(
            evidence_id="C06-PENDING",
            rule_id="SP2L.PENDING_LIFETIME",
            status=EvidenceStatus.PARTIALLY_RESOLVED,
            statement="C06 instructs deleting an unfilled Buy Limit within 1-2 candidate candles.",
            source_reference="C06",
            unresolved_questions=("SP2L.C06.Q1",),
        ),
    ]

    rules = [
        StrategyRule("SP2L.PGAP", "P.GAP / valid BO", RuleAuthority.NON_CANONICAL, EvidenceStatus.SOURCE_CONFIRMED, ("C01-PGAP",)),
        StrategyRule("SP2L.F12", "Retrace trigger", RuleAuthority.NON_CANONICAL, EvidenceStatus.PARTIALLY_RESOLVED, ("F12-TRIGGER",)),
        StrategyRule("SP2L.F13", "2X secondary entry", RuleAuthority.NON_CANONICAL, EvidenceStatus.SOURCE_CONFIRMED, ("F13-2X",)),
        StrategyRule("SP2L.F10", "Spike-start stop", RuleAuthority.NON_CANONICAL, EvidenceStatus.PARTIALLY_RESOLVED, ("F10-SL",)),
        StrategyRule("SP2L.TRADE_TEMPLATE", "Trade template", RuleAuthority.NON_CANONICAL, EvidenceStatus.SOURCE_CONFIRMED, ("C04-TEMPLATE",)),
        StrategyRule("SP2L.MA_FILTER", "15m MA50", RuleAuthority.NON_CANONICAL, EvidenceStatus.SOURCE_CONFIRMED, ("C05-MA50",)),
        StrategyRule("SP2L.PENDING_LIFETIME", "Pending-order lifetime", RuleAuthority.NON_CANONICAL, EvidenceStatus.PARTIALLY_RESOLVED, ("C06-PENDING",)),
    ]

    unresolved = [
        UnresolvedQuestion("SP2L.F12.Q1", "SP2L.F12", "Does retrace mean touch, penetration, or another price interaction?", True),
        UnresolvedQuestion("SP2L.F12.Q2", "SP2L.F12", "Is confirmation based on an intrabar event or candle close?", True),
        UnresolvedQuestion("SP2L.F12.Q3", "SP2L.F12", "What exact price becomes the executable entry?", True),
        UnresolvedQuestion("SP2L.F12.Q4", "SP2L.F12", "What fill semantics apply when price crosses the trigger?", True),
        UnresolvedQuestion("SP2L.F10.Q1", "SP2L.F10", "What exact candle extreme/anchor defines the stop?", True),
        UnresolvedQuestion("SP2L.C06.Q1", "SP2L.C06", "Does 1-2 candidate candles mean a fixed count or context-dependent lifetime?", True),
    ]

    return StrategyManifest(
        strategy_id="SP2L-A",
        revision="SOURCE-LEDGER-20261006-01",
        rules=rules,
        evidence=evidence,
        unresolved=unresolved,
    )
