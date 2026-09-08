# SP2L Spike-Origin Candle Resolution — 2026-09-08

## Scope

Research-only source-resolution pass focused on the identity of the candle from which the SP2L Spike originates, because the source ties structural SL placement to that candle. No production or validation logic is changed.

## Evidence set

Inspected the uploaded authoritative video at:

- ~28:00–30:30: four bullish spike constructions and progressive candle-level annotations.
- ~34:00–36:30: P-Gap teaching sequence with multiple accepted-looking spike variants.
- ~46:00–47:30: executable teaching diagram showing Entry, TP1, TP2 and SL.

The source transcript separately states that the SL is placed behind the candle from which the Spike originated.

## Direct visual findings

### 1. The teaching diagrams distinguish the spike sequence from later correction/continuation

The bullish examples are drawn as ordered candle sequences. The earliest candle in each construction is visually part of the directional movement, while later candles extend the same movement. The source does not provide a universal numeric candle index such as “third candle” for the Spike origin.

### 2. SL is visually referenced to the earliest structural candle

In the ~46:00–47:30 execution diagram, the `SL` line is below the earliest candle of the bullish sequence. The line is therefore consistent with the transcript's semantic statement that the stop is behind the candle from which the Spike originated.

This is stronger evidence for the **origin-candle identity** than for the exact stop price.

### 3. Entry is separate from the origin candle

The same diagram places `Entry` materially above the SL and at a later correction-related level. This supports keeping Entry geometry separate from SL/origin geometry.

### 4. Multiple Spike variants prevent a fixed global candle index

The P-Gap teaching sequence contains multiple accepted-looking variants. Gap timing varies within the sequence, so a rule such as “origin is always candle N” is not source-safe. Origin must be defined relative to the source-defined Spike sequence, not by a fixed absolute index.

## Resolution status

### Spike-origin identity

**STRONG SOURCE-ALIGNED SEMANTIC / CANDIDATE GEOMETRY:**

> The Spike-origin candle is the first/earliest candle of the source-defined directional Spike sequence, i.e. the candle from which the displayed Spike movement begins.

This formulation is intentionally relational. It does **not** claim that the origin is a fixed candle number across all variants.

### Exact SL price

**UNRESOLVED.**

The source supports “behind the Spike-origin candle,” but the available teaching diagram does not establish whether the executable price is:

- origin candle Low/High;
- origin wick extreme plus an offset;
- origin body boundary;
- another source-defined structural boundary;
- or a broker/tick-specific buffered price.

No buffer, tick distance, or wick/body substitution is invented.

## Relationship to Entry

The strongest current source-aligned structure is:

`source-defined Spike sequence`
`→ origin candle = first/earliest candle of that sequence`
`→ correction`
`→ correction reaches the relevant prior-candle extreme`
`→ pending Limit during correction`
`→ SL structurally behind the Spike-origin candle`

Entry and SL therefore remain distinct geometry variables. The source does not establish that Entry equals the Spike-origin price or P-Gap boundary.

## Relationship to P-Gap

P-Gap remains unresolved at exact boundary level. The source does not prove that the P-Gap boundaries identify the Spike-origin candle. P-Gap and origin identity must therefore remain separate until a direct source mapping is found.

## Synthetic discriminators

| Fixture | Question | Current result |
|---|---|---|
| OR-01 | First candle starts directional Spike; later candles continue | First candle is source-compatible origin candidate |
| OR-02 | Same structure with an earlier range candle preceding breakout | Earlier range candle is not automatically Spike origin |
| OR-03 | Gap appears on candle 2 while directional sequence starts on candle 1 | Fixed “gap candle = origin” rule rejected |
| OR-04 | Higher-lows-first variant before visible gap | Origin remains sequence-relative; gap timing does not redefine it automatically |
| OR-05 | Origin candle wick differs from body boundary | Origin identity supported; exact SL price unresolved |
| OR-06 | Candidate SL requires fixed buffer | Buffer remains unresolved |
| OR-07 | Bearish mirror | Origin is first/earliest candle of the source-defined bearish Spike sequence; exact High/buffer remains unresolved |

## Important non-decisions

This pass does **not** freeze:

- exact P-Gap formula;
- exact entry price;
- exact SL price;
- fixed candle index for Spike origin;
- wick-vs-body convention;
- any numeric buffer;
- classical A/B/C/D mapping.

## Gate decision

The origin-candle question is **narrowed materially** but not fully frozen as executable geometry.

- SOURCE RESOLUTION: progressing
- Spike-origin semantic: strong
- Exact origin identification across all variants: candidate / requires final variant cross-check
- Exact SL price: unresolved
- FROZEN GEOMETRY: blocked
- DEV: locked
- VAL: locked
- HOLDOUT: locked
- PRODUCTION: unchanged

## Next highest-value action

Cross-check the bearish teaching example against the bullish diagram and verify whether the same relational definition (“first/earliest candle of the source-defined Spike sequence”) survives direction reversal. If yes, freeze only the **origin identity semantics**, while keeping the executable SL price unresolved.
