# SP2L Batch 40 — P-Gap Canonical Contamination Audit

Date: 2026-09-21

## Objective

Verify that the repository's existing three-candle P-Gap research heuristic is
not being treated as canonical Strategy A geometry.

## Audited implementation

File:

`src/domain/strategy-a/PGAPResearch.ts`

The implementation:

- is explicitly named `PGAPResearch`;
- returns `PGAPObservation` records with `CANDIDATE`,
  `NOT_CANDIDATE`, or `UNKNOWN`;
- compares candle `i-2` with candle `i`;
- records bullish `right.low > left.high`;
- records bearish `right.high < left.low`;
- explicitly describes the result as a "three-candle ... imbalance candidate";
- explicitly states that it is **not yet validated as P-GAP**;
- does not expose itself as a canonical/frozen detector.

## Source comparison

The 2026-09-20 primary gap-video audit establishes P-Gap conceptually as
Pressure Gap (`گپ فشار`):

`10–30 candles of trend pressure → pressure pauses → trend-bar →
continuation expectation`.

The same source audit explicitly states that it does **not** provide an
executable P-Gap OHLC formula, candle indices, endpoints, or deterministic
classifier.

Therefore the existing three-candle imbalance heuristic is **not equivalent
to the source-confirmed P-Gap concept**.

## Contamination result

**PASS — no canonical contamination identified in the audited file.**

The research heuristic remains correctly isolated as an observation/candidate
layer. It must not be promoted, renamed, or silently reused as canonical
P-Gap geometry.

## Required guard

Any future promotion must require a primary-source gate that uniquely
specifies:

1. P-Gap type classification;
2. development/window semantics;
3. OHLC fields/endpoints;
4. candle indexing;
5. bullish/bearish mirror;
6. boundary/threshold;
7. activation relationship to valid BO.

Until those are source-resolved, Frozen Geometry remains blocked.

## Decision

No code change is made by this audit.

No backtest result is used to redefine P-Gap.

No author implementation formula is substituted for missing primary-source
geometry.

**Frozen Geometry: BLOCKED.**
