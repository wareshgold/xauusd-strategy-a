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
    assert any(a.kind is PlanActionKind.RESOLVE_SOURCE_AMBIGUITY for a in plan.actions)
    assert not any(a.kind is PlanActionKind.DESIGN_DISCRIMINATING_TEST for a in plan.actions)
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


def test_unknown_role_and_outcome_fail_closed():
    bad_role = EvidenceGraph(
        claims=(ClaimNode("C1", "Claim", ("MAGIC",)),), evidence=(), edges=())
    with pytest.raises(ValueError, match="unknown required role"):
        validate_graph(bad_role)
    bad_outcome = EvidenceGraph(
        claims=(ClaimNode("C1", "Claim", ("SOURCE",)),),
        evidence=(EvidenceNode("x", "fixture://x", sha256(b"x").hexdigest(),
                               "SOURCE", "PROBABLY_TRUE"),), edges=())
    with pytest.raises(ValueError, match="unknown role/outcome"):
        validate_graph(bad_outcome)


def test_unknown_edge_relation_fails_closed():
    graph = EvidenceGraph(
        claims=(ClaimNode("C1", "Claim", ("SOURCE",)),),
        evidence=(ev("source", "SOURCE"),),
        edges=(EvidenceEdge("source", "C1", "RELATED"),))
    with pytest.raises(ValueError, match="known EdgeRelation"):
        validate_graph(graph)


def test_source_evidence_is_prioritized_before_downstream_roles():
    graph = EvidenceGraph(
        claims=(ClaimNode("C-SOURCE-FIRST", "Research-first claim",
                          ("STATISTICAL_VALIDATION", "TEST", "DATA", "SOURCE", "EXECUTION")),),
        evidence=(), edges=(),
    )
    plan = build_research_plan(graph)
    assert [action.target for action in plan.actions] == [
        "SOURCE", "DATA", "TEST", "EXECUTION", "STATISTICAL_VALIDATION"
    ]


def test_inconclusive_source_requests_source_resolution_before_downstream_test():
    graph = EvidenceGraph(
        claims=(ClaimNode("C-SOURCE-AMBIGUOUS", "Unresolved source meaning", ("SOURCE", "TEST")),),
        evidence=(ev("source-maybe", "SOURCE", "INCONCLUSIVE"),),
        edges=(EvidenceEdge("source-maybe", "C-SOURCE-AMBIGUOUS", EdgeRelation.DEPENDS_ON),),
    )
    plan = build_research_plan(graph)
    assert plan.actions[0].kind is PlanActionKind.COLLECT_MISSING_EVIDENCE
    assert plan.actions[0].target == "SOURCE"
    assert any(action.kind is PlanActionKind.RESOLVE_SOURCE_AMBIGUITY for action in plan.actions)
    assert not any(action.kind is PlanActionKind.DESIGN_DISCRIMINATING_TEST for action in plan.actions)
    assert all(action.canonical_authorized is False for action in plan.actions)

def test_many_statistical_supports_never_outvote_linked_source_contradiction():
    graph = EvidenceGraph(
        claims=(ClaimNode("C-SOURCE-CONFLICT", "Source-defined claim",
                          ("SOURCE", "DATA", "TEST", "STATISTICAL_VALIDATION"), True),),
        evidence=(
            ev("source-counterexample", "SOURCE", "CONTRADICTS"),
            ev("data-support", "DATA"),
            ev("test-support", "TEST"),
            ev("stats-support-1", "STATISTICAL_VALIDATION"),
            ev("stats-support-2", "STATISTICAL_VALIDATION"),
            ev("stats-support-3", "STATISTICAL_VALIDATION"),
        ),
        edges=(
            EvidenceEdge("source-counterexample", "C-SOURCE-CONFLICT", EdgeRelation.CONTRADICTS),
            EvidenceEdge("data-support", "C-SOURCE-CONFLICT", EdgeRelation.SUPPORTS),
            EvidenceEdge("test-support", "C-SOURCE-CONFLICT", EdgeRelation.SUPPORTS),
            EvidenceEdge("stats-support-1", "C-SOURCE-CONFLICT", EdgeRelation.SUPPORTS),
            EvidenceEdge("stats-support-2", "C-SOURCE-CONFLICT", EdgeRelation.SUPPORTS),
            EvidenceEdge("stats-support-3", "C-SOURCE-CONFLICT", EdgeRelation.SUPPORTS),
        ),
    )
    plan = build_research_plan(graph)
    assert any(action.kind is PlanActionKind.RESOLVE_CONTRADICTION for action in plan.actions)
    assert any(action.target == "SOURCE" for action in plan.actions)
    assert all(action.canonical_authorized is False for action in plan.actions)
    assert all(action.production_decision_authorized is False for action in plan.actions)


def test_contradictory_source_does_not_satisfy_required_source_role():
    graph = EvidenceGraph(
        claims=(ClaimNode("C-SOURCE-REQUIRED", "Source must support this claim",
                          ("SOURCE", "STATISTICAL_VALIDATION")),),
        evidence=(
            ev("source-no", "SOURCE", "CONTRADICTS"),
            ev("stats-yes", "STATISTICAL_VALIDATION", "SUPPORTS"),
        ),
        edges=(
            EvidenceEdge("source-no", "C-SOURCE-REQUIRED", EdgeRelation.CONTRADICTS),
            EvidenceEdge("stats-yes", "C-SOURCE-REQUIRED", EdgeRelation.SUPPORTS),
        ),
    )
    plan = build_research_plan(graph)
    assert any(action.kind is PlanActionKind.COLLECT_MISSING_EVIDENCE
               and action.target == "SOURCE" for action in plan.actions)
    assert any(action.kind is PlanActionKind.RESOLVE_CONTRADICTION for action in plan.actions)


def test_inconclusive_test_cannot_be_attached_as_support():
    graph = EvidenceGraph(
        claims=(ClaimNode("C-INCONCLUSIVE-TEST", "A test with unresolved result",
                          ("SOURCE", "TEST")),),
        evidence=(
            ev("source", "SOURCE"),
            ev("test-maybe", "TEST", "INCONCLUSIVE"),
        ),
        edges=(
            EvidenceEdge("source", "C-INCONCLUSIVE-TEST", EdgeRelation.SUPPORTS),
            EvidenceEdge("test-maybe", "C-INCONCLUSIVE-TEST", EdgeRelation.SUPPORTS),
        ),
    )
    with pytest.raises(ValueError, match="conflicts with evidence outcome"):
        build_research_plan(graph)


def test_inconclusive_non_source_evidence_stays_unresolved_and_non_authorizing():
    graph = EvidenceGraph(
        claims=(ClaimNode("C-TEST-MAYBE", "Unresolved test outcome",
                          ("SOURCE", "TEST", "STATISTICAL_VALIDATION"), True),),
        evidence=(
            ev("source", "SOURCE"),
            ev("test-maybe", "TEST", "INCONCLUSIVE"),
        ),
        edges=(
            EvidenceEdge("source", "C-TEST-MAYBE", EdgeRelation.SUPPORTS),
            EvidenceEdge("test-maybe", "C-TEST-MAYBE", EdgeRelation.DEPENDS_ON),
        ),
    )
    plan = build_research_plan(graph)
    assert any(action.kind is PlanActionKind.DESIGN_DISCRIMINATING_TEST
               for action in plan.actions)
    assert any(action.target == "STATISTICAL_VALIDATION" for action in plan.actions)
    assert all(action.canonical_authorized is False for action in plan.actions)
    assert all(action.production_decision_authorized is False for action in plan.actions)

def test_contradiction_keeps_same_role_open_even_if_other_evidence_supports_it():
    graph = EvidenceGraph(
        claims=(ClaimNode("C-SAME-ROLE-CONFLICT", "Conflicting source evidence",
                          ("SOURCE", "STATISTICAL_VALIDATION")),),
        evidence=(
            ev("source-support", "SOURCE", "SUPPORTS"),
            ev("source-counterexample", "SOURCE", "CONTRADICTS"),
            ev("stats-support", "STATISTICAL_VALIDATION", "SUPPORTS"),
        ),
        edges=(
            EvidenceEdge("source-support", "C-SAME-ROLE-CONFLICT", EdgeRelation.SUPPORTS),
            EvidenceEdge("source-counterexample", "C-SAME-ROLE-CONFLICT", EdgeRelation.CONTRADICTS),
            EvidenceEdge("stats-support", "C-SAME-ROLE-CONFLICT", EdgeRelation.SUPPORTS),
        ),
    )
    plan = build_research_plan(graph)
    assert any(action.kind is PlanActionKind.RESOLVE_CONTRADICTION for action in plan.actions)
    assert any(action.kind is PlanActionKind.COLLECT_MISSING_EVIDENCE
               and action.target == "SOURCE" for action in plan.actions)
    assert "C-SAME-ROLE-CONFLICT" in plan.unresolved_claim_ids
    assert all(action.canonical_authorized is False for action in plan.actions)
    assert all(action.production_decision_authorized is False for action in plan.actions)


def test_canonical_review_is_retained_even_when_other_actions_exist():
    graph = EvidenceGraph(
        claims=(ClaimNode("C-CANONICAL-GAP", "Potential canonical change",
                          ("SOURCE", "DATA"), True),),
        evidence=(ev("source", "SOURCE"),),
        edges=(EvidenceEdge("source", "C-CANONICAL-GAP", EdgeRelation.SUPPORTS),),
    )
    plan = build_research_plan(graph)
    assert any(action.kind is PlanActionKind.COLLECT_MISSING_EVIDENCE
               and action.target == "DATA" for action in plan.actions)
    assert any(action.kind is PlanActionKind.HUMAN_SOURCE_REVIEW for action in plan.actions)
    assert all(action.canonical_authorized is False for action in plan.actions)
    assert all(action.production_decision_authorized is False for action in plan.actions)
