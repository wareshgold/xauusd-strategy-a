# SP2L Canonical Validation Readiness Ledger — 2026-09-16

## Purpose

This ledger records whether each required Frozen Geometry field has sufficient primary-source evidence to become `SOURCE_CONFIRMED` and therefore eligible for canonical validation.

This is a readiness/audit artifact, not a geometry specification. It does not select among unresolved interpretations and does not change the canonical geometry contract.

## Gate rule

Frozen Geometry may become `READY` only when **all seven required fields** are `SOURCE_CONFIRMED`:

- `entry`
- `invalidation`
- `limitRefresh`
- `trigger`
- `twoX`
- `abcd`
- `pGap`

Any `CANDIDATE` or `UNRESOLVED` field keeps the gate `BLOCKED`.

## Readiness matrix

| Field | Current provenance | Source evidence currently established | Remaining canonical ambiguity | Evidence required for `SOURCE_CONFIRMED` | Do-not-infer boundary |
|---|---|---|---|---|---|
| `entry` | **UNRESOLVED / PARTIAL** | Correction sequence and Pending/Buy Limit behavior are source-described. The source demonstrates placement within the initial three-candle structure and references the relevant correction level. | Universal exact entry-price anchor; whether the demonstrated anchor applies across all Spike variants; exact distinction between first-entry anchor and Leg-2 origin. | A primary-source worked example that exposes the exact entry price/anchor and unambiguously identifies the structural event that defines it, ideally with price-level semantics or directly readable chart levels. | Do not infer an entry equation from a visual approximation, backtest optimum, or a single demonstrated variant and generalize it to all setups. |
| `invalidation` | **UNRESOLVED / PARTIAL** | Source establishes that return to the referenced level invalidates the scenario and that stop distance is considered before activation. Structural invalidation is distinct from entry. | Exact OHLC/wick/body anchor; exact price-level convention; any buffer/spread treatment. | A primary-source worked stop/invalidation example with exact structural level semantics sufficient to determine the executable anchor and any explicit buffer rule. | Do not infer wick/body selection, buffer, spread adjustment, or numeric offset from observed charts or profitable outcomes. |
| `limitRefresh` | **UNRESOLVED / PARTIAL** | Source says a subsequent candle can cause the existing order to be deleted and a new order placed according to changed stop distance; small changes may retain/move the existing order. | Deterministic condition/threshold for mandatory refresh, including what counts as a material change. | Explicit primary-source wording or a worked example that uniquely determines the mandatory refresh condition/threshold and resulting order behavior. | Do not invent a percentage, point, ATR, candle-count, or other refresh threshold from testing. |
| `trigger` | **UNRESOLVED / PARTIAL** | Source describes one-, two-, and three-candle structures, Limit entry after the structure, and bar/key-bar confirmation variants. | Deterministic trigger taxonomy, acceptance algorithm, classifier/precedence, and exact conditions under which each variant is accepted. | A primary-source executed setup (or explicit source rule) tying trigger form to acceptance conditions and precedence sufficiently to classify every allowed case deterministically. | Do not collapse the family into a single three-candle rule or choose trigger precedence because it performs better in backtest. |
| `twoX` | **UNRESOLVED / PARTIAL** | Source identifies 2X as an optional second position and associates it with approximately half-target-distance positioning and potentially larger R from a later entry. | Exact price anchor/formula; sizing; stop; target; fill semantics; whether the half-target concept is measured from a specific anchor. | A primary-source worked 2X example exposing exact levels plus execution/sizing semantics, or explicit source formula that uniquely determines them. | Do not convert “approximately half the target” into an invented universal equation, tolerance, sizing rule, or fill model. |
| `abcd` | **UNRESOLVED / PARTIAL** | Source explicitly identifies SPIKE-2LEG and equates the two-leg concept with AB=CD; Leg 2 is expected to match Leg 1 in magnitude and target is at completion of Leg 2. | Exact A/B/C/D endpoints; OHLC convention; measurement method; tolerance; handling of non-exact equality. | A primary-source worked AB=CD example exposing all four anchors and the measurement convention, plus any explicit acceptance/tolerance rule. | Do not choose swing endpoints, candle bodies/wicks, percentage tolerance, or pivot algorithm from backtest performance. |
| `pGap` | **UNRESOLVED** | Source distinguishes P-Gap from E-Gap/Common-Gap, associates P-Gap with breakout construction, and describes multiple ordering variants as the same strategy concept. | Exact deterministic OHLC formula, candle indexing, location constraints, and classification boundaries. | Primary-source chart/transcript/frame evidence that uniquely exposes the P-Gap candle/price relationship and all required OHLC/index conditions. | Do not invent an OHLC equation, infer one from a screenshot alone when multiple formulas fit, or select a formula by backtest performance. |

## Primary-source evidence references

### Entry / invalidation / refresh / trigger

The primary transcript evidence records:

- `38:38`: correction begins in the bullish example and a manual or predefined Limit order may be used.
- `38:53–39:26`: Buy Limit can be placed within the initial three-candle structure; return to the referenced level invalidates the scenario.
- `39:48`: a subsequent candle may cause deletion/replacement of the existing order according to changed stop distance; no deterministic refresh threshold is supplied.
- `40:57–41:03`: bar and key-bar confirmation variants are described.

These statements materially constrain behavior but do not uniquely freeze all executable anchors. See `SP2L_PRIMARY_SOURCE_TRANSCRIPT_2X_TRIGGER_ABCD_2026-09-16.md`.

### 2X

- `38:05`: first pullback entry followed by a second entry called `2X`.
- `41:26–41:53`: 2X is optional and can create a larger R multiple from the later entry.
- Earlier source material associates the second position with approximately half the target distance.
- `57:14`: later 2X example still does not establish a universal numerical formula.

### AB=CD

- `36:15`: SPIKE-2LEG is explicitly identified and the two-leg concept is linked to AB=CD.
- `36:59–37:08`: second leg is expected to become equal to the first leg; target is at completion of the second leg.
- `37:57`: same-size next-leg expectation is repeated.

### P-Gap

- `31:43`: breakout candle associated with P-Gap and distinguished from E-Gap.
- `34:25–35:37`: multiple source-described ordering variants are treated as the same strategy concept.
- `50:09`: P-Gap and E-Gap are again distinguished, without a complete OHLC equation.

## Promotion criteria

A field may be promoted from `PARTIAL`/`UNRESOLVED` to `SOURCE_CONFIRMED` only when primary-source evidence uniquely determines the executable meaning required by the frozen geometry contract.

The following are not valid promotion mechanisms:

1. Backtest performance or optimization.
2. Majority vote among competing interpretations.
3. Visual guesswork that is not uniquely discriminating.
4. Convenience of implementation.
5. Matching a known trade outcome by tuning an otherwise unresolved rule.

## Current gate decision

**Frozen Geometry: `BLOCKED`**

All seven required fields remain below `SOURCE_CONFIRMED` at this checkpoint. The research harness is ready to reject unresolved/candidate geometry, but it must not be used to promote unresolved source meaning.

## Downstream lock state

| Stage | State | Reason |
|---|---|---|
| Source Resolution | 🟡 PARTIAL | Required executable details remain unresolved. |
| Synthetic Fixtures | 🟢 ADVANCED | Deterministic discrimination fixtures and gate tests exist. |
| Frozen Geometry | 🔴 BLOCKED | 7/7 required fields are not yet source-confirmed. |
| Untouched Validation | 🔒 LOCKED | Canonical geometry is not frozen. |
| Robustness / Stability | 🔒 LOCKED | Validation is not yet authorized. |
| Fresh Holdout | 🔒 LOCKED | Upstream canonical validation is not complete. |
| Production | 🔴 OFF | No canonical production geometry or BUY/SELL generation. |

## Integrity boundaries

- No geometry field is changed by this ledger.
- No BUY/SELL decision is generated.
- No validation metric denominator is opened.
- The 125R observation remains untouched, unmodified, unclipped, and unreclassified.
- This ledger must be updated only when new primary-source evidence materially changes a field's evidence state.

## Conclusion

The project is now **validation-harness ready but source-geometry not freeze-ready**. The next legitimate promotion event is not a better backtest; it is acquisition and audit of primary evidence that uniquely resolves one or more of the seven blockers.
