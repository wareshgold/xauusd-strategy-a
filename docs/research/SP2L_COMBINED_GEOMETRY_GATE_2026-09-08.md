# SP2L Combined Geometry Gate — 2026-09-08

## Purpose

This gate combines the source-resolution results for P-Gap, Entry, structural invalidation/SL, Leg 1, and AB=CD into one decision record. It is research-only. It does not promote any unresolved geometry into production.

## Evidence rule

The source hierarchy remains: raw authoritative source → source visual evidence → source ledger/meaning map → frozen deterministic specification → implementation → historical research.

Backtest performance cannot resolve source meaning.

## Combined resolution matrix

| Component | Source semantic | Executable geometry | Gate status |
|---|---|---|---|
| P-Gap | Required for valid Spike/Breakout | Exact OHLC boundary and candle timing unresolved | BLOCKED |
| Entry | Correction reaches previous/relevant Low/High; pending-limit entry | Exact candle index and exact price anchor unresolved | BLOCKED |
| SL | Behind candle where Spike originated / structural invalidation | Wick/body convention and buffer unresolved | BLOCKED |
| Leg 1 | First directional leg associated with Spike, followed by correction | Exact OHLC anchors unresolved | BLOCKED |
| Leg 2 | Second leg approximately/equally related to Leg 1; explicit AB=CD | Exact A/B/C/D anchors and tolerance unresolved | BLOCKED |
| Base TP | 1:1 source-confirmed | Executable only after entry/SL geometry is frozen | BLOCKED |

## Cross-component contradictions rejected

1. **Generic FVG as P-Gap** — rejected as canonical. The source distinguishes P-GAP/E-GAP/Common-GAP and says location matters; the public secondary indicator is not authority for an equivalence.
2. **Entry at P-Gap boundary** — rejected. Source describes the entry during correction at the relevant prior Low/High and explicitly demonstrates Buy Limit/Sell Limit semantics.
3. **Market close-reclaim as base entry** — rejected. A close-reclaim may exist in legacy research code, but it is not the source-confirmed execution semantics.
4. **50% retracement as base entry** — rejected. Secondary/add-on management must not replace the base pending-limit entry.
5. **Classical harmonic A/B/C/Fibonacci mapping** — rejected. The source explicitly contrasts internet/classical AB=CD treatment with its candle-level approach.
6. **Invented SL buffer or wick/body convention** — rejected until source evidence resolves it.
7. **Invented AB=CD tolerance** — rejected until source evidence or a frozen specification defines it.

## What can be frozen semantically

The following semantic contract is sufficiently source-aligned for continued fixture research:

- Identity: SP2L / Spike → 2 Leg.
- A valid Spike requires source-defined P-Gap evidence.
- Spike follows a range/context and breakout/follow-through structure.
- Correction is part of the setup and references the prior/relevant Low for bullish setups or High for bearish setups.
- Base execution is a pending limit during the correction.
- Structural invalidation is tied to the Spike-origin structure.
- Leg 2 follows correction and is related to Leg 1 through the source-confirmed equal-leg / AB=CD relationship.
- Base target is 1:1.

These statements remain semantic, not executable price formulas.

## Synthetic discrimination plan

Synthetic fixtures must discriminate interpretations before any historical optimization:

### P-Gap
- adjacent-candle wick separation
- three-candle outer-wick separation
- adjacent-body separation
- three-candle outer-body separation
- exact boundary touch
- bullish/bearish mirrors
- timing variants where gap appears before/after follow-through

### Entry
- correction touching prior/relevant Low/High
- correction that never reaches the reference
- multiple candidate lows/highs
- same candle touching the reference versus later candle
- pending-limit fill versus market close-reclaim
- 50% retracement occurring without the source entry condition

### SL
- origin wick differs from origin body
- multiple plausible origin candles
- correction extreme versus origin structure
- exact-touch invalidation
- bullish/bearish mirrors

### Leg 1 / AB=CD
- origin-to-extreme versus breakout-to-extreme
- first structural extreme versus Spike extreme
- equal-leg exact match
- unequal legs around the unresolved tolerance
- bearish mirror
- classical Fibonacci anchors present but intentionally non-canonical

## Gate decision

**SOURCE RESOLUTION: semantic freeze candidate passed.**

**FROZEN GEOMETRY: BLOCKED.**

Reason: at least four executable quantities remain unresolved: P-Gap boundary/timing, exact pending-limit price anchor, exact SL price convention, and exact Leg-1/AB=CD anchors/tolerance.

Therefore:

- DEV historical optimization remains locked.
- Untouched validation remains locked.
- Robustness/stability remains locked.
- Fresh holdout remains locked.
- Production promotion remains locked.
- Research fixtures may continue.

## Required next gate

Build and test the missing entry, SL, and Leg-1/AB=CD synthetic fixture suites, then run a combined cross-component consistency test. If multiple candidate geometries survive, retain them as unresolved alternatives rather than selecting one by profitability.
