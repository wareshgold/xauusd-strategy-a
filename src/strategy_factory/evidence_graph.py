"""Deterministic evidence graph and next-experiment planner.

The planner may propose work to reduce uncertainty, but cannot decide source
meaning, invent missing evidence, or promote canonical/production rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EdgeRelation(str, Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    DEPENDS_ON = "DEPENDS_ON"


class PlanActionKind(str, Enum):
    RESOLVE_CONTRADICTION = "RESOLVE_CONTRADICTION"
    COLLECT_MISSING_EVIDENCE = "COLLECT_MISSING_EVIDENCE"
    DESIGN_DISCRIMINATING_TEST = "DESIGN_DISCRIMINATING_TEST"
    HUMAN_SOURCE_REVIEW = "HUMAN_SOURCE_REVIEW"
    RESOLVE_SOURCE_AMBIGUITY = "RESOLVE_SOURCE_AMBIGUITY"


@dataclass(frozen=True)
class ClaimNode:
    claim_id: str
    statement: str
    required_roles: tuple[str, ...]
    canonical_rule_change: bool = False


@dataclass(frozen=True)
class EvidenceNode:
    evidence_id: str
    reference: str
    content_sha256: str
    role: str
    outcome: str


@dataclass(frozen=True)
class EvidenceEdge:
    evidence_id: str
    claim_id: str
    relation: EdgeRelation


@dataclass(frozen=True)
class EvidenceGraph:
    claims: tuple[ClaimNode, ...]
    evidence: tuple[EvidenceNode, ...]
    edges: tuple[EvidenceEdge, ...]


@dataclass(frozen=True)
class ResearchAction:
    action_id: str
    kind: PlanActionKind
    claim_id: str
    target: str
    reason: str
    expected_artifact: str
    canonical_authorized: bool = False
    production_decision_authorized: bool = False


@dataclass(frozen=True)
class ResearchPlan:
    actions: tuple[ResearchAction, ...]
    unresolved_claim_ids: tuple[str, ...]
    graph_valid: bool = True


def validate_graph(graph: EvidenceGraph) -> None:
    claim_ids = [node.claim_id for node in graph.claims]
    evidence_ids = [node.evidence_id for node in graph.evidence]
    if any(not value for value in claim_ids + evidence_ids):
        raise ValueError("graph node IDs must be non-empty")
    if len(claim_ids) != len(set(claim_ids)):
        raise ValueError("duplicate claim ID")
    if len(evidence_ids) != len(set(evidence_ids)):
        raise ValueError("duplicate evidence ID")
    claims = set(claim_ids)
    evidence = {node.evidence_id: node for node in graph.evidence}
    valid_roles = {"SOURCE", "DATA", "TEST", "EXECUTION", "STATISTICAL_VALIDATION"}
    valid_outcomes = {"SUPPORTS", "CONTRADICTS", "INCONCLUSIVE"}
    for node in graph.claims:
        if not node.statement.strip() or not node.required_roles:
            raise ValueError(f"claim {node.claim_id} needs a statement and required roles")
        if len(node.required_roles) != len(set(node.required_roles)):
            raise ValueError(f"claim {node.claim_id} repeats a required role")
        if any(role not in valid_roles for role in node.required_roles):
            raise ValueError(f"claim {node.claim_id} has an unknown required role")
    for node in graph.evidence:
        digest = node.content_sha256.lower()
        if (not node.reference or len(digest) != 64
                or any(char not in "0123456789abcdef" for char in digest)):
            raise ValueError(f"evidence {node.evidence_id} lacks valid provenance/hash")
        if node.role not in valid_roles or node.outcome not in valid_outcomes:
            raise ValueError(f"evidence {node.evidence_id} has unknown role/outcome")
    seen_edges: set[tuple[str, str, EdgeRelation]] = set()
    for edge in graph.edges:
        if edge.evidence_id not in evidence or edge.claim_id not in claims:
            raise ValueError("edge endpoint does not exist")
        if not isinstance(edge.relation, EdgeRelation):
            raise ValueError("edge relation must be a known EdgeRelation")
        key = (edge.evidence_id, edge.claim_id, edge.relation)
        if key in seen_edges:
            raise ValueError("duplicate evidence edge")
        seen_edges.add(key)
        if edge.relation is EdgeRelation.SUPPORTS and evidence[edge.evidence_id].outcome != "SUPPORTS":
            raise ValueError("SUPPORTS edge conflicts with evidence outcome")
        if edge.relation is EdgeRelation.CONTRADICTS and evidence[edge.evidence_id].outcome != "CONTRADICTS":
            raise ValueError("CONTRADICTS edge conflicts with evidence outcome")


def build_research_plan(graph: EvidenceGraph) -> ResearchPlan:
    """Return a stable list of next research actions from explicit graph gaps."""
    validate_graph(graph)
    evidence = {node.evidence_id: node for node in graph.evidence}
    edges_by_claim: dict[str, list[EvidenceEdge]] = {c.claim_id: [] for c in graph.claims}
    for edge in graph.edges:
        edges_by_claim[edge.claim_id].append(edge)

    actions: list[ResearchAction] = []
    unresolved: list[str] = []
    for claim in sorted(graph.claims, key=lambda item: item.claim_id):
        edges = sorted(edges_by_claim[claim.claim_id],
                       key=lambda edge: (edge.evidence_id, edge.relation.value))
        contradictions = [edge.evidence_id for edge in edges
                          if edge.relation is EdgeRelation.CONTRADICTS]
        contradicted_roles = {
            evidence[edge.evidence_id].role for edge in edges
            if edge.relation is EdgeRelation.CONTRADICTS
        }
        supported_roles = {
            evidence[edge.evidence_id].role for edge in edges
            if edge.relation is EdgeRelation.SUPPORTS
        } - contradicted_roles
        role_priority = {"SOURCE": 0, "DATA": 1, "TEST": 2, "EXECUTION": 3, "STATISTICAL_VALIDATION": 4}
        missing_roles = sorted(set(claim.required_roles) - supported_roles,
                               key=lambda role: (role_priority[role], role))
        claim_actions: list[ResearchAction] = []
        if contradictions:
            claim_actions.append(ResearchAction(
                action_id=f"{claim.claim_id}:reconcile",
                kind=PlanActionKind.RESOLVE_CONTRADICTION,
                claim_id=claim.claim_id,
                target=",".join(contradictions),
                reason="Contradictory evidence is explicitly linked to this claim.",
                expected_artifact="SOURCE_DIFF_OR_DISCRIMINATING_FIXTURE",
            ))
        for role in missing_roles:
            claim_actions.append(ResearchAction(
                action_id=f"{claim.claim_id}:collect:{role}",
                kind=PlanActionKind.COLLECT_MISSING_EVIDENCE,
                claim_id=claim.claim_id,
                target=role,
                reason="No linked supporting evidence currently covers this required role.",
                expected_artifact=f"PROVENANCE_BOUND_{role}_EVIDENCE",
            ))
        inconclusive_source = any(
            evidence[edge.evidence_id].role == "SOURCE"
            and evidence[edge.evidence_id].outcome == "INCONCLUSIVE"
            for edge in edges
        )
        if inconclusive_source:
            claim_actions.append(ResearchAction(
                action_id=f"{claim.claim_id}:resolve-source-ambiguity",
                kind=PlanActionKind.RESOLVE_SOURCE_AMBIGUITY,
                claim_id=claim.claim_id,
                target="INCONCLUSIVE_SOURCE_EVIDENCE",
                reason="Source meaning is inconclusive; resolve it before designing downstream tests.",
                expected_artifact="HUMAN_REVIEWED_SOURCE_EXCERPT_AND_INTERPRETATION_DIFF",
            ))
        elif any(evidence[eid].outcome == "INCONCLUSIVE"
                 for eid in (edge.evidence_id for edge in edges)):
            claim_actions.append(ResearchAction(
                action_id=f"{claim.claim_id}:discriminate",
                kind=PlanActionKind.DESIGN_DISCRIMINATING_TEST,
                claim_id=claim.claim_id,
                target="INCONCLUSIVE_EVIDENCE",
                reason="Linked non-source evidence is inconclusive; no outcome is presumed.",
                expected_artifact="FROZEN_INPUT_COUNTEREXAMPLE_FIXTURE",
            ))
        if claim.canonical_rule_change:
            claim_actions.append(ResearchAction(
                action_id=f"{claim.claim_id}:human-review",
                kind=PlanActionKind.HUMAN_SOURCE_REVIEW,
                claim_id=claim.claim_id,
                target="CANONICAL_RULE_DIFF",
                reason="Canonical changes require explicit human review of source meaning.",
                expected_artifact="REVIEWED_SOURCE_CITATION_AND_RULE_DIFF",
            ))
        if claim_actions:
            unresolved.append(claim.claim_id)
            actions.extend(claim_actions)

    return ResearchPlan(
        actions=tuple(actions),
        unresolved_claim_ids=tuple(sorted(set(unresolved))),
        graph_valid=True,
    )
