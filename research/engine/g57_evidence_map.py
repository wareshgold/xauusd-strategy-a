from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Resolution(str, Enum):
    SUPPORTED = "SUPPORTED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class EvidenceFixtureMap:
    blocker: str
    source_regions: tuple[str, ...]
    supported_claim: str
    falsification_fixtures: tuple[str, ...]
    resolution: Resolution


MAP = (
    EvidenceFixtureMap("B1", ("31:43-32:21", "34:25-35:35", "36:15-37:10"), "P-Gap is a named breakout/follow-through condition.", ("range_separation", "overlap", "generic_three_candle_imbalance"), Resolution.UNRESOLVED),
    EvidenceFixtureMap("B2", ("38:18-39:30", "54:10-54:29"), "Pending Limit is placed during correction at a relevant structural level.", ("original_spike_level", "latest_hl_lh", "alternative_structural_level"), Resolution.UNRESOLVED),
    EvidenceFixtureMap("B3", ("39:26-41:30", "55:02-55:22"), "Stop is tied to structural invalidation and distinct from Entry.", ("wick", "body", "structural_pivot"), Resolution.UNRESOLVED),
    EvidenceFixtureMap("B4", ("53:16-53:54", "53:54-55:02"), "One-, two-, three-candle and Key-Bar trigger forms are source-consistent.", ("one_candle", "two_candle", "three_candle", "key_bar", "market_reclaim_exclusion"), Resolution.UNRESOLVED),
    EvidenceFixtureMap("B5", ("36:15-37:10",), "AB=CD links Leg1 and Leg2 magnitude.", ("wick_endpoints", "body_endpoints", "pivot_endpoints", "mixed_endpoints"), Resolution.UNRESOLVED),
    EvidenceFixtureMap("B6", ("36:15-37:10", "42:26-42:37", "22:43", "53:32-54:29"), "Leg2 continuation, TP1 preference and 2X are source-supported concepts.", ("projection_model_a", "projection_model_b", "tp_endpoint_alternatives"), Resolution.UNRESOLVED),
)


def all_blockers_are_mapped() -> bool:
    return {item.blocker for item in MAP} == {"B1", "B2", "B3", "B4", "B5", "B6"}


def source_unique_resolution_exists() -> bool:
    return all(item.resolution is Resolution.SUPPORTED for item in MAP)
