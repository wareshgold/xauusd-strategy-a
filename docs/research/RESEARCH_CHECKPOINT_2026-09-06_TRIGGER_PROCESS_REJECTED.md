# Research Checkpoint — 2026-09-06 — Trigger Process Axis Rejected

## Scope
Canonical NY SELL 5m universe. DEV + VAL only. Fresh Holdout remains locked.

## Trigger-process audit
The detector semantics were audited before feature implementation:
- `CorrectionDetector` defines `correctionExtremeIndex` for a bearish spike as the first candle whose high exceeds `spike.startPrice`.
- `EntryTrigger` begins at `correctionExtremeIndex + 1` and fires on the first subsequent candle whose close is below `correction.extremePrice`.
- The trigger candle is the entry candle; intermediate trigger-path candles are strictly between the correction extreme and trigger candle.

## Phase 2 feature set
The final minimal feature set was:
1. `triggerDelay = trigger.index - correction.correctionExtremeIndex`
2. `triggerPathRetraceDepth` — maximum intermediate adverse high excursion above trigger level, normalized by correction size.
3. `triggerPathFailedReclaims` — fraction of intermediate candles that intrabar pierced below trigger level but closed back at/above it.

Excluded features included exact transforms/redundancies (`triggerPathCandles`), existing trigger anatomy (`triggerBodyToRange`, `triggerCloseLocation`), and low-information/overlapping path candidates.

## Phase 3 result
Canonical N=29, DEV=15, VAL=14, Fresh=LOCKED.

- Overall AvgR = 0.692492, PF = 2.338817
- No-exceptional AvgR = -0.370744, PF = 0.357377
- DEV AvgR = 0.996411, PF = 3.491027
- VAL AvgR = 0.366864, PF = 1.570678
- Path features non-zero in only 4/29 cases after deterministic replay.
- `triggerDelay`: 25/29 cases equal 1; remaining delays 2, 2, 8, 47, 987.
- `triggerDelay` median delta = 0; Spearman all = -0.01681; no-exceptional = 0.073243.
- `triggerPathRetraceDepth` median delta = 0; Spearman all = -0.032736; no-exceptional = 0.051452.
- `triggerPathFailedReclaims` median delta = 0; Spearman all = -0.008847; no-exceptional = 0.084139.

The four non-zero path cases were mixed: one DEV loss, one small VAL win, one VAL exceptional win, and one VAL loss. Therefore the path-feature sample is descriptive only.

## Decision
**REJECTED** as a stable source of information for the canonical NY SELL entry process.

Reason: the entry process is structurally homogeneous (immediate reclaim in 25/29 cases), and the delayed/path cases are too few and outcome-mixed to support a stable edge. No threshold, rule, optimization, or Fresh Holdout decision was made.

## Integrity notes
- No production detector semantics were changed.
- Fresh Holdout was not opened.
- No trading rule was created.
- Research status remains descriptive-only.
- A replay discrepancy with an older expanded-anatomy report was investigated; deterministic replay aligned with baseline semantics and showed the older 987-delay attribution came from a different historical detector pairing.

## Next research candidates
1. Session/time-of-day regime interactions using already validated/descriptive pre-entry features.
2. Broader universes such as other NY/SELL/BUY segments, only after explicit methodology definition.
3. Carefully bounded post-entry/exit-path research only where the question is genuinely about management rather than entry prediction.
