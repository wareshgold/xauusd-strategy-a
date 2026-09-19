# SP2L Synthetic Discrimination Pass — 2026-09-19

## Result

F10/F12/F14 adversarial research fixtures were added without promoting any candidate geometry.

## Covered distinctions

- F10: wick vs body vs structural-origin stop candidates.
- F12: touch vs penetration vs close trigger semantics.
- F12: one/two/three-candle and Bar/Key-Bar variants are represented as alternatives without precedence.
- F14: competing anchor families remain explicit; Entry=C is not canonical.

## Important limitation

The first fixture pass is intentionally a harness-level discrimination layer. It proves that the research environment can represent competing interpretations; it does not prove which interpretation the source intends.

F14 candidate arithmetic is therefore only a fixture mechanism and must not be reused as the Strategy A AB=CD formula.

## Gate

Source Resolution: PARTIAL
F10: PARTIAL / UNRESOLVED
F12: PARTIAL / UNRESOLVED
F14: PARTIAL / UNRESOLVED
P-Gap: UNRESOLVED / QUARANTINED
Frozen Geometry: BLOCKED
Canonical Promotion: BLOCKED
Production: BLOCKED
Live Trading: DISABLED

## Commits

- Discrimination matrix: 06eb04f98b4ccd2e9b6ee4e0e0423ef93ea152f5
- Adversarial fixture harness: 6ccfb89dfc6f74057de435634467c37eb2f8bce2

## Next step

Run the repository's existing TypeScript/Vitest suite and, if clean, harden these fixtures against accidental canonical imports. Do not tune trading parameters and do not reopen generic P-Gap theory.