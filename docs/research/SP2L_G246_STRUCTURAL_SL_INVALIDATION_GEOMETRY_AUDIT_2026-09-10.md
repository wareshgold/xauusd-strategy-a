# SP2L G246 — Structural SL / Invalidation Geometry Audit

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Decision class:** `B3_STRUCTURAL_SL_INVALIDATION`  
**Status:** `PARTIAL_FREEZE__EXECUTABLE_BOUNDARY_BLOCKED`

## 1. Purpose

This pass isolates the Strategy-A stop-loss / structural-invalidation concept from the unresolved entry and target geometry.

The objective is to freeze only what the authoritative source actually states about where the structural stop belongs. No wick/body rule, buffer, tick convention, or candle-index formula is invented from visual appearance.

No historical performance or optimization result is used to select source meaning.

## 2. Authoritative source evidence

The official creator explanation states that after the second-leg setup is triggered:

- Entry is taken in the direction of the spike;
- **Stop-Loss is placed behind the candle from which the spike originated**;
- Take-Profit is separately defined.

This is the clearest source-level semantic definition currently available for B3.

The raw walkthrough independently shows explicit `SL` fields in the order panel and repeated stop-side measurement references. G217/G219 establish strong source-correlated alignment between the visible `0.0` level and terminal S/L values in multiple observed states, but the source material does not expose the measurement-object construction gesture sufficiently to prove the exact candle-price anchor behind `0.0`.

## 3. Source-confirmed semantic rule

### B3-C1 — Structural invalidation anchor

**FROZEN AT SEMANTIC LEVEL:**

`Structural SL = behind the candle from which the spike originated.`

This is a source-defined structural concept, not merely a generic fixed-distance stop.

The phrase identifies the **origin candle of the spike** as the structural reference. It does not yet define the exact OHLC coordinate used behind that candle.

## 4. What the source does NOT uniquely resolve

The following remain `UNKNOWN`:

| Field | Status | Reason |
|---|---|---|
| Origin-candle index | `PARTIAL / SEMANTIC` | Source says the candle from which the spike originated, but does not provide a deterministic indexing rule for cases with multiple candidate candles. |
| Exact price anchor | `UNKNOWN` | “Behind” does not uniquely specify Low, High, open, close, wick extreme, or another point. |
| Wick vs body | `UNKNOWN` | No source text explicitly chooses full wick extreme versus body boundary. |
| Buffer | `UNKNOWN` | No numeric/pip/point buffer is source-confirmed. |
| Equality / touch semantics | `UNKNOWN` | No source rule states whether exact contact with the structural boundary is invalidation. |
| Intrabar vs close confirmation | `UNKNOWN` | Source does not freeze whether invalidation occurs on touch, breach, or candle close. |
| Spread/bid-ask handling | `UNKNOWN` | No source execution specification reviewed. |
| SL modification after placement | `UNKNOWN` | No canonical adjustment rule established. |

## 5. Directional interpretation boundary

The broader SP2L source explicitly supports both bullish and bearish setups. Therefore the semantic concept of placing the stop on the opposite side of the spike-origin candle is compatible with both directions.

However, the exact directional OHLC formula must not be manufactured solely from symmetry.

Research-only candidates may therefore be represented as hypotheses such as:

- bullish spike: stop below an origin-candle boundary;
- bearish spike: stop above an origin-candle boundary.

But the project must not silently choose `Low[origin]`, `High[origin]`, body boundary, or a buffered variant as the canonical rule until source evidence resolves it.

## 6. Relationship to `0.0` measurement level

Earlier source audits provide strong source-correlated evidence that, in observed terminal states:

`0.0 ↔ terminal S/L`

and that the same measurement vocabulary repeats across multiple trade/order states.

G217 records the direct alignment in the first order state and explicitly preserves the construction-origin uncertainty. G219 later confirms the same numerical mapping across an independent order state.

This is useful corroboration that `0.0` is a stop-side measurement reference.

It is **not** sufficient to freeze:

`0.0 = exact origin-candle wick/body boundary`

because the source transition occurs after the measurement object is already instantiated and the raw drawing gesture is not captured.

## 7. Entry independence

G245 deliberately left the pending-limit entry anchor unresolved. B3 must remain independently specified from B2.

The source-supported relationship is:

`correction → source entry mechanism → structural SL associated with spike-origin candle`

but no executable formula is inferred for Entry or for the exact distance between Entry and SL.

Therefore this audit does not use the unresolved Entry/C geometry to derive the stop.

## 8. Synthetic fixture implications

Before historical development, the research fixture layer should distinguish at minimum:

1. bullish spike with an identifiable single origin candle;
2. bearish spike with an identifiable single origin candle;
3. origin candle with long wick beyond body;
4. origin candle where wick and body boundary differ materially;
5. multiple plausible origin candles;
6. exact-touch versus breach beyond candidate stop boundary;
7. zero-buffer versus positive-buffer candidates;
8. intrabar breach versus close-only breach;
9. order placed before/after subsequent candles alter the local structure.

Fixtures must label these as competing hypotheses until source evidence freezes the relevant geometry.

## 9. Gate decision

### SOURCE RESOLUTION
`PASS_PARTIAL`

### B3 — Structural SL semantic meaning
`PARTIALLY FROZEN`

Frozen:

`SL is placed behind the candle from which the spike originated.`

### B3 — Executable OHLC geometry
`BLOCKED`

Unresolved:

- exact origin-candle selection;
- exact price boundary;
- wick/body semantics;
- buffer;
- invalidation timing;
- execution/spread semantics.

### FROZEN GEOMETRY
`BLOCKED_FOR_FULL_STRATEGY`

### DEV
`BLOCKED`

### UNTOUCHED VALIDATION
`PROTECTED`

### ROBUSTNESS / STABILITY
`BLOCKED`

### FRESH HOLDOUT
`PROTECTED`

### PRODUCTION
`BLOCKED`

## 10. Required next work

1. Preserve the semantic B3 freeze above.
2. Continue source inspection around the first four detailed trades and the explicit SL annotations.
3. Look specifically for a frame sequence in which the spike-origin candle and the final SL line are simultaneously visible at sufficient resolution.
4. Independently resolve B5 — AB=CD anchors/tolerance.
5. Independently resolve B6 — Leg-2 / TP semantics.
6. Do not derive the SL formula by fitting historical outcomes.

## 11. Final decision

**G246 partially freezes B3 at the source-semantic level but does not authorize an executable stop formula.**

The strongest canonical statement currently justified is:

> **Place the structural stop behind the candle from which the spike originated.**

Everything required to turn that sentence into deterministic OHLC code remains explicitly `UNKNOWN` until stronger source evidence resolves it.
