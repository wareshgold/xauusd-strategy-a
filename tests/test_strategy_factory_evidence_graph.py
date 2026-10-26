from hashlib import sha256

import pytest

from strategy_factory.evidence_graph import (
    ClaimNode,
    EdgeRelation,
    EvidenceEdge,
    EvidenceGraph,
    EvidenceNode,
    PlanActionKind,
    build_research_plan,
    validate_graph,
)


def ev(eid, role, outcome="SUPPORTS"):
    return EvidenceNode(eid, f"fixture://{eid}", sha256(eid.encode()).hexdigest(), role, outcome)


def test_missing_roles_generate_stable_evidence_collection_actions():
    graph = EvidenceGraph(
        claims=(ClaimNode("C1", "Test claim", ("SOURCE", "DATA", "TEST")),),
        evidence=(ev("source", "SOURCE"),),
        edges=(EvidenceEdge("source", "C1", EdgeRelation.SUPPORTS),),
    )
    plan = build_research_plan(graph)
    assert [a.target for a in plan.actions] == ["DATA", "TEST"]
    assert [a.kind for a in plan.actions] == [
        PlanActionKind.COLLECT_MISSING_EVIDENCE, PlanActionKind.COLLECT_MISSING_EVIDENCE
    ]
    assert build_research_plan(graph) == plan


def test_contradiction_is_preserved_and_generates_reconciliation_action():
    graph = EvidenceGraph(
        claims=(ClaimNode("C1", "Test claim", ("SOURCE",)),),
        evidence=(ev("source", "SOURCE"), ev("counterexample", "DATA", "CONTRADICTS")),
        edges=(EvidenceEdge("source", "C1", EdgeRelation.SUPPORTS),
               EvidenceEdge("counterexample", "C1", EdgeRelation.CONTRADICTS)),
    )
    plan = build_research_plan(graph)
    assert plan.actions[0].kind is PlanActionKind.RESOLVE_CONTRADICTION
    assert plan.actions[0].target == "counterexample"


def test_canonical_change_always_requires_human_review_when_no_gaps():
    graph = EvidenceGraph(
        claims=(ClaimNode("C1", "Change source rule", ("SOURCE",), True),),
        evidence=(ev("source", "SOURCE"),),
        edges=(EvidenceEdge("source", "C1", EdgeRelation.SUPPORTS),),
    )
    plan = build_research_plan(graph)
    assert len(plan.actions) == 1
    assert plan.actions[0].kind is PlanActionKind.HUMAN_SOURCE_REVIEW
    assert plan.actions[0].canonical_authorized is False
    assert plan.actions[0].production_decision_authorized is False


def test_inconclusive_evidence_proposes_discriminating_fixture_not_a_result():
    graph = EvidenceGraph(
        claims=(ClaimNode("C1", "Unresolved geometry", ("SOURCE",)),),
        evidence=(ev("maybe", "SOURCE", "INCONCLUSIVE"),),
        edges=(EvidenceEdge("maybe", "C1", EdgeRelation.DEPENDS_ON),),
    )
    plan = build_research_plan(graph)
    assert any(a.kind is PlanActionKind.DESIGN_DISCRIMINATING_TEST for a in plan.actions)
    assert all(a.canonical_authorized is False for a in plan.actions)


def test_support_edge_cannot_hide_contradictory_outcome():
    graph = EvidenceGraph(
        claims=(ClaimNode("C1", "Test claim", ("SOURCE",)),),
        evidence=(ev("counterexample", "SOURCE", "CONTRADICTS"),),
        edges=(EvidenceEdge("counterexample", "C1", EdgeRelation.SUPPORTS),),
    )
    with pytest.raises(ValueError, match="conflicts with evidence outcome"):
        validate_graph(graph)


def test_duplicate_evidence_ids_and_orphan_edges_fail_closed():
    duplicate = EvidenceGraph(
        claims=(ClaimNode("C1", "Test claim", ("SOURCE",)),),
        evidence=(ev("x", "SOURCE"), ev("x", "SOURCE")),
        edges=(),
    )
    with pytest.raises(ValueError, match="duplicate evidence ID"):
        validate_graph(duplicate)
    orphan = EvidenceGraph(
        claims=(ClaimNode("C1", "Test claim", ("SOURCE",)),),
        evidence=(ev("x", "SOURCE"),),
        edges=(EvidenceEdge("missing", "C1", EdgeRelation.SUPPORTS),),
    )
    with pytest.raises(ValueError, match="endpoint"):
        validate_graph(orphan)


def test_bad_hash_is_rejected_before_planning():
    graph = EvidenceGraph(
        claims=(ClaimNode("C1", "Test claim", ("SOURCE",)),),
        evidence=(EvidenceNode("x", "fixture://x", "bad", "SOURCE", "SUPPORTS"),),
        edges=(),
    )
    with pytest.raises(ValueError, match="provenance/hash"):
        build_research_plan(graph)
