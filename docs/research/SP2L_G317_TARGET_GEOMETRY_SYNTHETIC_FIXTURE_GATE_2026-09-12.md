# SP2L G317 — Target Geometry Synthetic Fixture Gate

**Date:** 2026-09-12
**Status:** `SYNTHETIC_FIXTURE_GATE_PREPARED__NO_CANONICAL_SELECTION`

## Purpose

Before any historical optimization, competing target mappings must be represented as deterministic synthetic fixtures. The fixtures test whether an implementation can distinguish the source hypotheses without using market performance to choose the meaning.

## Required fixture families

1. **C1 equal-ladder:** risk-side interval = 500 points; Entry→TP1 = 250; Entry→TP2 = 500.
2. **C2 sequential:** each 250/500 annotation interpreted as adjacent intervals.
3. **C3 shifted anchors:** 250/500/1000 assigned to alternative structural intervals.
4. **Round-Level override:** target candidate selected by a Round-Level rule (kept hypothetical).
5. **AB=CD projection:** target derived from explicit A/B/C/D candidates (kept hypothetical).

## Required assertions

Fixtures must verify that each candidate produces a distinct, inspectable target and that no candidate silently falls back to another interpretation.

No historical result may be used to select the canonical fixture.
