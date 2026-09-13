# G372 — Primary Geometry Acquisition Audit

Date: 2026-09-13
Status: SOURCE RESOLUTION / audit complete
Canonical: false

## Objective
Audit the currently available primary-source corpus against the six executable geometry blockers carried forward from G370/G371. No historical performance is used to infer source meaning.

## Evidence set
1. `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt` — source transcript.
2. `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4` — primary SP2L video artifact previously hashed and frame-audited.
3. `gap پورصمدی دوره جامع.mp4` — primary gap lesson artifact previously hashed and frame-audited.
4. Official SP2L page: https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/

## Audit result

| Blocker | Primary evidence found | Executable geometry closed? | Decision |
|---|---|---:|---|
| P-Gap endpoints / overlap / size | P-Gap = Pressure Gap; context/location matters; multiple timing examples | No | BLOCKED |
| A/B/C/D anchors / scale | SP2L/2Leg + AB=CD; parent/nested examples | No | BLOCKED |
| Pending-limit / trigger / fill | Correction trigger language; pending-limit demonstrated | No | BLOCKED |
| SL boundary | SL behind Spike-origin candle; structural invalidation | No | BLOCKED |
| TP1/TP2/R1/R2 vs 1:1 | AB=CD, TP1/TP2/R1/R2 lesson language; official default 1:1 | No reconciliation | BLOCKED |
| 50% secondary entry scope | Official page explicitly permits 50% secondary entry | Scope not established | OPTIONAL / NON-CANONICAL |

## Source-confirmed semantic facts
- SP2L is Spike → 2 Leg / AB=CD.
- A valid Spike is associated with P-Gap; the gap lesson identifies P-Gap with Pressure Gap.
- Pressure Gap is contextual and is not interchangeable with the generic gap example.
- Correction follows the first directional movement; official wording describes reaching the prior low/high depending on direction.
- The source demonstrates pending-limit entry during correction and structural invalidation.
- SL is semantically tied to the candle from which the Spike originated.
- The source contains AB=CD, TP1/TP2 and R1/R2 terminology and examples of 2X/3X outcomes.
- The official page states default TP = 1:1.

## Explicitly not resolved
- P-Gap endpoint candles/price fields, wick/body basis, overlap convention, minimum size and tolerance.
- A/B/C/D exact anchors and whether they are wick/body/close/candle-boundary/structural-event based.
- Parent versus nested leg selection as a canonical scale rule.
- Exact pending-limit price and fill semantics.
- Exact SL boundary and any offset.
- Mapping between AB=CD projection and TP1/TP2/R1/R2, including reconciliation with official 1:1 default.
- Whether 50% secondary entry belongs to the primary canonical signal or is optional add-on execution.

## Promotion guard
No pixel-derived measurement, third-party implementation, generic three-candle gap formula, guessed anchor, `fill_price = C`, guessed SL offset, fixed 2X/3X target, seven-lower-high threshold, or MA/session/timeframe hard gate is promoted.

## Gate decision
**FROZEN GEOMETRY remains BLOCKED.**

This audit does not authorize canonical DEV backtesting. The next legitimate source step is acquisition of a higher-resolution or explicitly annotated primary artifact that labels the missing geometry. If such an artifact cannot be acquired, the project should preserve the semantic freeze and continue only with clearly marked non-canonical hypothesis research.
