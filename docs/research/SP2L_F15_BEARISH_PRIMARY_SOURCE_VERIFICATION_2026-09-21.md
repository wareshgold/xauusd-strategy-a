# SP2L F15 Bearish Primary-Source Verification — 2026-09-21

## New primary-source evidence
The instructor's official SP2L page explicitly states:
- in an uptrend, wait for the corrective candle to reach the previous candle's Low;
- in a downtrend, wait for the corrective candle to reach the previous candle's High;
- after the second-leg trigger, entry follows the spike direction;
- a valid spike includes a P-Gap.

Source: official Mohammad Ali Poursamadi SP2L page, accessed 2026-09-21.

## What this resolves
The source independently confirms the directional bearish second-leg trigger concept:
- bearish/downtrend trigger uses the previous candle's High;
- bearish entry follows the downward spike.

This is independent primary-source evidence, not synthetic bullish mirroring.

## What remains unresolved
The source page does not uniquely define:
- exact bearish P-Gap OHLC indexing/formula;
- wick/body endpoint selection;
- exact swing/pivot algorithm;
- exact F10 stop field/buffer/invalidation;
- full deterministic bearish geometry.

Therefore this evidence must not be promoted into a universal executable bearish detector.

## Gate
- F15 bearish directional trigger: SOURCE_CONFIRMED_PARTIAL
- F15 full bearish geometry: UNRESOLVED
- Synthetic mirror as primary evidence: NOT ACCEPTED
- Frozen Geometry: BLOCKED
- Production: DISABLED

## Canonicalization rule
Only the explicitly sourced bearish trigger meaning may be retained as source evidence. Any exact executable formula remains quarantined until uniquely discriminated.