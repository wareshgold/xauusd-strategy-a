# SP2L F8–F15 Source Adjudication Ledger — 2026-09-14

## Purpose

This ledger records source-only adjudication of synthetic fixtures F8–F15.

It is a research evidence artifact, not a canonical strategy specification. Historical profitability, backtest performance, parameter optimization, and implementation convenience are explicitly excluded from adjudication.

## Evidence hierarchy

- Tier 1: direct source statement/transcript.
- Tier 2: direct source visual/chart example.
- Tier 3: official related source.
- Tier 4: secondary implementation/reference.

Only Tier 1/2 evidence can directly establish source meaning for canonical geometry. Lower tiers may generate hypotheses but cannot canonicalize them.

## Result vocabulary

- `SOURCE-DISCRIMINATED`: source evidence eliminates the competing interpretation(s) at the stated semantic level.
- `SOURCE-DOES-NOT-DISCRIMINATE`: source evidence is insufficient to choose among remaining interpretations.
- `BLOCKED`: adjudication cannot proceed without additional source evidence.
- `REJECTED`: an interpretation is contradicted by source evidence; reason must be explicit.

## F8 — Dynamic relevant-low / pending-limit refresh

### Question

Which correction low governs the pending entry when the Spike produces multiple completed higher lows before correction?

### Source evidence

Tier 1/2 evidence is recorded in the source geometry matrix and visual triangulation. The 38:40–39:50 sequence shows a bullish higher-low chain and the Buy Limit reference moving upward to the most recent completed higher-low immediately before correction. The same record states that the transcript permits order update as new candles form. The source also keeps the stop/invalidation below the deeper/base structural level.

The visual record therefore strongly supports the demonstrated variant as:

`Spike → higher-low chain → currently relevant/protected low → pending Buy Limit`

It does not prove that this exact "latest completed higher-low" algorithm applies universally to every Spike variant, nor does it define the complete rule for deciding which low remains relevant across all structures.

### Competing interpretations

1. Immutable first/base low.
2. Latest/current relevant HL/LH.
3. Immutable original order after first placement.

### Adjudication

**Result: `SOURCE-DOES-NOT-DISCRIMINATE` at universal-algorithm level.**

The source evidence discriminates against treating the original/base low as the only entry reference in the demonstrated bullish higher-low example, and it strongly favors a dynamic/relevant-low interpretation for that demonstrated variant. However, the available evidence does not establish a universal deterministic definition of "relevant" across all Spike variants.

### Canonical consequence

Do **not** freeze `Entry = latest swing low` as a universal Strategy A rule.

The following semantic statement may remain research-confirmed:

> In the demonstrated bullish higher-low construction, the pending Buy Limit reference can move to the currently relevant completed higher-low while structural invalidation remains at a deeper/base structural level.

The universal entry-anchor algorithm remains unresolved.

## F9 — Entry versus start of Leg 2

### Source evidence

The source geometry matrix explicitly records: **Entry identical to Leg-2 start? No; keep separate — HIGH confidence.** The visual triangulation likewise treats pending entry and continuation/Leg-2 structure as distinct concepts.

### Adjudication

**Result: `SOURCE-DISCRIMINATED` at semantic level.**

Entry must not be silently equated with the start of Leg 2. Exact candle/price anchors for both remain unresolved.

## F10 — Structural invalidation versus risk-distance stop

### Source evidence

The source geometry matrix records a distinct invalidation condition from executable Entry and explicitly rejects deriving structural invalidation from a risk budget. The source visual ordering is `SL → Enter → leg 2`. Exact OHLC/wick/body semantics and any execution buffer remain unresolved.

### Adjudication

**Result: `SOURCE-DISCRIMINATED` at semantic level.**

Risk percentage cannot determine structural invalidation. Entry, invalidation anchor, and position sizing must remain separate variables. Exact stop-price construction is still unresolved.

## F11 — Pending-order refresh condition

### Source evidence

The source permits deleting a prior order and placing a new order when another candle forms and the distance to SL changes. However, the teacher's criterion is qualitative/material-distance based and does not provide a deterministic numerical replacement threshold.

### Adjudication

**Result: `SOURCE-DOES-NOT-DISCRIMINATE`.**

Source supports that refresh can occur, but does not define a universal deterministic retain/replace condition. No pip, percentage, ATR, or other threshold may be invented.

## F12 — Trigger family

### Source evidence

The source geometry matrix records that one-, two-, and three-candle constructions are confirmed. Exact acceptance taxonomy remains unresolved.

### Adjudication

**Result: `SOURCE-DISCRIMINATED` for family existence; `BLOCKED` for final classifier.**

The system must not collapse the source into a one-candle-only trigger. A deterministic acceptance classifier remains unresolved.

## F13 — 2X operational meaning

### Source evidence

The source records 2X as a confirmed concept and preserves distinct teaching examples including a second position at half target and a second position with its own reward profile. No single numeric universal formula is frozen.

### Adjudication

**Result: `SOURCE-DOES-NOT-DISCRIMINATE`.**

The available evidence does not select one operational formula without inventing semantics.

## F14 — AB=CD anchor set

### Source evidence

The source explicitly confirms AB=CD and the approximate equality of Leg 2 magnitude to Leg 1 magnitude. The available visual/transcript record does not unambiguously label a unique candle-level A/B/C/D anchor set or numerical equality tolerance.

### Adjudication

**Result: `SOURCE-DOES-NOT-DISCRIMINATE`.**

Only the magnitude relationship is source-confirmed. No arbitrary swing anchors, entry-as-C assumption, Fibonacci substitute, or tolerance may be introduced.

## F15 — Bearish mirror

### Source evidence

The current evidence set is materially stronger for the demonstrated bullish construction. Absence of a directly adjudicating bearish example cannot be treated as proof of symmetry.

### Adjudication

**Result: `BLOCKED`.**

A mirrored bearish implementation remains a research hypothesis until sufficiently strong source evidence supports it.

## Current gate state

| Gate | Status |
|---|---|
| SOURCE RESOLUTION | **IN PROGRESS** |
| SYNTHETIC FIXTURES | **ADJUDICATION IN PROGRESS** |
| FROZEN GEOMETRY | **BLOCKED** |
| DEV | **LOCKED for Strategy A geometry** |
| UNTOUCHED VALIDATION | **LOCKED** |
| ROBUSTNESS / STABILITY | **LOCKED** |
| FRESH HOLDOUT | **LOCKED** |
| PRODUCTION | **LOCKED** |

## Non-negotiable boundary

These adjudications do not authorize Strategy A geometry implementation or canonicalization. Any remaining ambiguity is preserved as unresolved. Canonical promotion still requires explicit manual approval by Ali.

## Next source-resolution target

Continue with direct source evidence for the unresolved portions of F8 and F11, then adjudicate the exact anchor semantics in F9/F10 and the remaining F12–F15 blockers. Do not use historical performance to break ties.
