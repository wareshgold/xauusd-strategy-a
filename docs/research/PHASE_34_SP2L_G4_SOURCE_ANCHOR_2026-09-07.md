# Phase 34 — SP2L G4 Source Anchor

**Date:** 2026-09-07  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Status:** Research-only — no production Strategy A changes

## Objective

Continue G4 (Leg 1 endpoints) using the preserved Poorsamadi source itself, rather than selecting an endpoint model from historical performance.

The raw source transcript is authoritative for semantic intent. Chart coordinates that are only visible in the video remain visual evidence and are not invented from transcript text.

## Source evidence recovered

The preserved `POORSAMADI_SP2L_SOURCE.txt` contains a direct SP2L worked example around 1:02:41–1:04:32.

### 1:02:41–1:03:32 — outer leg and nested leg

The teacher describes a sequence of lower highs and says he is looking for Leg 2. He then explicitly distinguishes an outer leg from a nested 2-Leg structure inside it.

Important semantic facts:

- the outer move is treated as Leg 1 / Leg 2;
- the same move can contain its own nested 2-Leg structure;
- therefore Leg 1 boundaries are scenario-dependent structural boundaries, not automatically the entire visible spike or an arbitrary candle-window boundary.

### 1:04:00–1:04:32 — explicit deep-leg example

The teacher says that when uncertain, he waits for a **deep leg** and identifies its start visually: "لگ عمیق من از کجا شروع شده؟ از اینجا".

He then describes a sequence of lower highs, places the order at the shown level, and says that the first leg is the segment between the two chart locations he points to: "لگ اول من که از اینجا تا اینجا بوده".

He then states that TP1 for this position is based on that Leg 1 reference.

The transcript does not encode the chart pixel coordinates/candle indices of those two visual points. Therefore the exact OHLC endpoint mapping cannot honestly be recovered from transcript text alone.

## G4 conclusion

The source evidence **does resolve an important part of G4**:

> Leg 1 is a source-selected structural price segment between two visual structural points in the specific SP2L scenario.

This makes the following implementation assumptions unsafe as canonical semantics:

- fixed `first.open -> last.close` candle-window geometry;
- automatic `spike-origin -> spike-extreme` for every scenario;
- automatic `breakout-level -> spike-extreme` for every scenario.

The strongest remaining candidate family is therefore:

```text
STRUCTURAL POINT A -> STRUCTURAL POINT B
```

where A and B are selected from the source-described SP2L structure for the active scenario.

This does **not** yet justify a numeric algorithm for selecting A/B. In particular, we must not invent:

- pivot lookback/lookforward counts;
- minimum number of lower highs/higher lows;
- exact candle index for A;
- exact candle index for B;
- whether B is always the pending-limit level, correction extreme, or another structural point;
- any equality tolerance for Leg 2.

## Relationship to G2/G3

G2 currently has a research candidate of HL low / LH high as the pending limit level.  
G3 currently has a research candidate of the spike-origin candle directional extreme as the structural stop reference, with executable buffer still TBD.

G4 must not silently reuse either G2 or G3 as a Leg 1 endpoint unless the source example proves that relationship.

## 37:22 / P-GAP evidence

The same source section establishes that two spike branches are treated as the same SP2L concept:

1. breakout first, followed by P-GAP / higher-lows or lower-highs;
2. structural continuation first, followed by P-GAP.

Therefore P-GAP timing relative to breakout does not by itself define the Leg 1 endpoint.

The source also explicitly states that a breakout can occur with P-GAP evidence and a follow-through candle. This is semantic evidence for the spike-family branch, not a numeric P-GAP formula.

## What is now safe to codify

For a future SP2L V2 semantic engine:

```text
SP2L scenario
  -> identify source-valid structural sequence
  -> identify source-valid Leg 1 A/B points
  -> project Leg 2 from the separately resolved G5 origin
  -> compare |Leg2| with |Leg1|
```

Leg 1 should therefore be represented as explicit structural endpoints, not hidden inside a generic candle-range helper.

Suggested research representation:

```text
leg1 = {
  start: StructuralPoint | TBD,
  end: StructuralPoint | TBD,
  sourceBasis: "POORSAMADI_EXAMPLE_1_04_00_1_04_32",
  resolutionStatus: "SEMANTIC_RESOLVED_GEOMETRY_TBD"
}
```

This is a research schema only, not production code.

## Next step — G5

G4 now has a source-anchored semantic direction: **structural point → structural point**.

The next question is G5: exactly where Leg 2 starts in the same source example, and whether that origin is:

- correction extreme;
- pending-limit level;
- actual fill;
- first structural HL/LH point;
- or another explicitly shown structural point.

Only after G5 is resolved should we define a deterministic A/B/C geometry fixture and test it against the source example.

## Protected boundaries

- Fresh Holdout remains LOCKED.
- Phase 13–30 historical evidence remains immutable.
- Production Strategy A remains unchanged.
- No historical performance is used to choose semantic geometry.
- No P-GAP threshold is invented.
- No 2X logic is introduced into the single-position baseline.
