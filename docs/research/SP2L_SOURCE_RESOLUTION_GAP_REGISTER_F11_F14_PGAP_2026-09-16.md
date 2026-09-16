# SP2L Source Resolution Gap Register — F11–F14 + P-Gap — 2026-09-16

## Purpose

Convert the current forensic state into a strict evidence-acquisition checklist. This register does not infer missing geometry.

## F11 — Limit refresh

**Current:** behavior source-confirmed; mandatory deterministic threshold unresolved.

**Need one of:**
- explicit numeric threshold;
- explicit structural state transition that deterministically selects keep/move versus delete/re-place/new sizing;
- repeated worked examples establishing the same executable rule without contradiction.

**Do not accept:** discretionary wording alone as a hidden numeric rule.

## F12 — Trigger family

**Current:** one-, two-, and three-candle constructions plus Bar/Key-Bar variants are source-described; classifier and precedence unresolved.

**Need:** a worked setup or explicit teaching statement that uniquely maps observable structure to the accepted trigger and resolves precedence when multiple variants are simultaneously present.

**Do not accept:** frequency of appearance in examples as proof of precedence.

## F13 — 2X

**Current:** optional later position; half-target example and R comparison source-confirmed; universal formula unresolved.

**Need:** source visual/value mapping that uniquely identifies:
1. target reference used to define half target;
2. second-position entry anchor;
3. stop/risk reference;
4. sizing relationship, if any;
5. fill semantics.

**Do not accept:** deriving the formula from the worked R example alone.

## F14 — AB=CD

**Current:** Leg2≈Leg1 magnitude relationship source-confirmed; A/B/C/D endpoints and tolerance unresolved.

**Need:** explicit labels or unambiguous source visual endpoints plus measurement convention and acceptable equality tolerance, if tolerance is actually specified.

**Do not accept:** conventional harmonic-trading A/B/C/D definitions as a substitute.

## P-Gap

**Current:** concept/location distinction exists; exact OHLC construction unresolved.

**Need:** primary-source evidence identifying the candles and OHLC relationship that makes a P-Gap, plus enough evidence to distinguish it from E-Gap.

**Do not accept:** generic three-candle fair-value-gap/imbalance formulas unless the source explicitly equates them.

## Stop condition for source resolution

A field is promoted to `SOURCE_CONFIRMED` only when the evidence uniquely determines the executable meaning. Otherwise it remains `PARTIAL` or `UNRESOLVED`.

## Current gate

F11 🟡 | F12 🟡 | F13 🟡 | F14 🟡 | P-Gap 🔴

Frozen Geometry remains blocked. Historical validation remains locked. Production remains off.
