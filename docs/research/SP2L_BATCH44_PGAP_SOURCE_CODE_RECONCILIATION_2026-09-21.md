# SP2L Batch 44 — P-Gap Source-to-Author-Code Reconciliation — 2026-09-21

## Objective

Close the highest-value remaining P-Gap evidence questions without tuning,
backtesting, or promoting implementation behavior to canonical strategy rules.

Scope:
- OHLC endpoint evidence
- candle indexing
- bullish/bearish mirror
- trend-bar semantics
- compression boundary
- formula/type binding

Governing rule: primary source meaning outranks implementation. Author-code
evidence may narrow the unresolved search space but cannot by itself freeze a
canonical rule.

## Evidence reviewed

Primary/source records:
- `SP2L_PGAP_SOURCE_RESOLUTION_UPDATE_2026-09-20.md`
- `SP2L_RAW_VIDEO_FRAME_AUDIT_2026-09-20.md`
- `SP2L_F10_F11_F12_F14_EVIDENCE_GAP_MATRIX_2026-09-20.md`

Author implementation crosswalk:
- `SP2L_BATCH38_AUTHOR_IMPLEMENTATION_CROSSWALK_2026-09-17.md`

Batch43 forensic result:
- `SP2L_BATCH43_SOURCE_ALIGNMENT_FORENSIC_RESULT_2026-09-21.md`
- Candidate/imbalance partition: candidate 1,755; generic imbalance 7,402;
  overlap 290; candidate-only 1,465; imbalance-only 7,112.
These counts are descriptive only and do not select a rule.

## Reconciliation matrix

| Question | Primary source evidence | Author implementation evidence | Status |
|---|---|---|---|
| P-Gap identity | P-Gap = pressure gap; 10–30 pressure candles → pause → trend-bar → continuation context | Indexed P-Gap construction exists in author code | SOURCE-CONFIRMED concept; geometry not frozen |
| OHLC endpoints | No P-Gap-specific endpoint formula; generic gap slide gives high[-2] vs low[0] only, type-unspecified | Bullish uses low[-2] vs high[-4]; bearish uses high[-2] vs low[-4] | IMPLEMENTATION-RESOLVED CANDIDATE; SOURCE-UNRESOLVED |
| Candle indexing | Source 10–30 count is developmental, not detector indices | -4 = before spike, -3 = spike, -2 = after spike, -1 = latest | AUTHOR-IMPLEMENTATION CONFIRMED; PRIMARY-SOURCE NOT EXPLICIT |
| Bullish mirror | Source text is bullish-worded; no explicit mirror statement | Bearish mirror is explicitly encoded | AUTHOR-IMPLEMENTATION CONFIRMED; SOURCE MIRROR NOT EXPLICIT |
| Trend-bar semantics | Source explicitly requires a trend-bar after the pause | Author code uses spike/body-size comparisons around fixed window | SOURCE-CONFIRMED qualitative concept; exact executable body rule UNRESOLVED |
| Compression boundary | Source shows pressure pauses/compression; blue boxes mark multi-candle zones | Code/backtest uses configurable implementation conditions | SOURCE-CONFIRMED qualitative concept; deterministic boundary UNRESOLVED |
| Formula/type binding | No source statement binds the generic gap formula to P-Gap | Author code binds a four-bar construction to P-Gap | AUTHOR-IMPLEMENTATION EVIDENCE only; canonical binding UNRESOLVED |
| Threshold | Source confirms 10–30 pressure candles, but no P-Gap price threshold | `P_GAP_PRICE`/`pGapSize` are configurable | Threshold meaning/canonical value UNRESOLVED |

## Deterministic conclusions

1. The author implementation materially narrows the executable P-Gap search
   space to a fixed four-candle family:
   - `-4`: before-spike/origin-side candle
   - `-3`: spike candle
   - `-2`: post-spike candle
   - `-1`: latest/trigger-side candle
2. The author implementation explicitly supplies both directional P-Gap
   inequalities:
   - bullish: `low[-2] > high[-4] + P_GAP_PRICE`
   - bearish: `high[-2] < low[-4] - P_GAP_PRICE`
3. These implementation facts are stronger than the generic gap convention
   found in the gap lesson, but they are still not primary-source confirmation
   of the canonical P-Gap formula.
4. The source does confirm the developmental structure: pressure → pause/
   compression → trend-bar. It does not supply deterministic pause length,
   compression ratio, trend-body multiplier, or price-gap threshold.
5. Therefore the Batch43 Candidate V1 parameters (`pause_len=2`,
   compression_factor=0.75, trend_body_factor=1.5) remain research-only and
   must not be promoted.
6. The generic `high[-2]` vs `low[0]` convention must not be silently
   substituted for the author-code P-Gap construction. They are separate
   evidence items with different status.

## Canonical gate decision

**FROZEN GEOMETRY: BLOCKED**

No production detector is created or modified.

No threshold is tuned.

No backtest result is used to resolve source ambiguity.

The strongest currently defensible statement is:

> P-Gap is source-confirmed as a pressure-gap developmental pattern, while
> the exact executable OHLC formula is author-implementation-supported but not
> primary-source-confirmed.

## Next evidence-closure target

The remaining high-value source question is not another statistical test.
It is whether the archived primary material contains a frame/audio statement
that directly binds the P-Gap label to the author implementation's
`-4/-2` endpoints and directional mirror.

If that binding cannot be established from primary evidence, retain the
implementation as a clearly labeled non-canonical candidate and proceed only
with source-confirmed portions to synthetic fixtures.

