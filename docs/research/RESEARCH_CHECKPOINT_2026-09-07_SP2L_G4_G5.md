# Research Checkpoint — 2026-09-07 — SP2L G4/G5

## Branch
`research/phase12-preentry-geometry-robustness`

## Current research state
- Local HEAD before this checkpoint: `74dbfaa`.
- GitHub already contains G4 source-resolution commit `4db59f0`; local checkout has not yet pulled it.
- Phase32 semantic-state foundation is completed and validated.
- G1/G2/G3 structural geometry candidates are implemented as research-only candidates and their tests passed.

## Validation completed
- SP2L Semantic State: 12/12 tests passed.
- G1 Structural Reference: 3/3 tests passed.
- G2 Pending Limit: 5/5 tests passed.
- G3 Structural Stop: 4/4 tests passed.
- TypeScript build/type-check passed.

## G1/G2/G3 candidate conclusions
- G1: bullish candidate uses previous candle low / HL level; bearish candidate uses previous candle high / LH level. This remains `CANDIDATE`, not source-confirmed as one universal structural point.
- G2: bullish pending Buy Limit candidate = HL price; bearish pending Sell Limit candidate = LH price; activation is exact retest/touch. No tolerance invented.
- G3: bullish structural SL candidate = spike-origin low; bearish structural SL candidate = spike-origin high. No historical buffer optimization or invented buffer.

## G4 — Leg 1 source resolution
Status: `TBD / SOURCE-RESOLUTION-INCOMPLETE`.

Source confirms the SP2L relationship `Leg 2 ~= Leg 1`, but the transcript text does not expose exact chart coordinates for the endpoints of Leg 1. Candidate endpoint definitions must therefore NOT be selected from the transcript by guesswork.

Candidate families kept separate for future evidence:
1. structural low/high -> spike extreme
2. breakout -> spike extreme
3. spike start -> spike end
4. relevant open -> spike extreme
5. structural -> structural

No historical optimization or calculator has been built for G4.

## G5 — Leg 2 projection origin
Status: `TBD`.

Candidate origins currently tracked:
1. correction extreme
2. actual fill
3. structural reference
4. source-defined chart point

G5 should not be promoted by backtest performance. First seek source/visual evidence; if unresolved, keep it explicit as TBD.

## Next steps
1. Continue source-first evidence extraction for G4/G5 from `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt` and corroborating source material.
2. Resolve one geometry question at a time.
3. Use deterministic synthetic fixtures before chronological historical evaluation.
4. After geometry is sufficiently resolved, address G6 equality tolerance.
5. Then address G7 execution semantics: limit touch/fill, SL/TP touch, same-candle ambiguity, spread/slippage.
6. Only after a candidate survives DEV/VAL should Fresh Holdout be unlocked.

## Hard constraints
- Fresh Holdout remains LOCKED.
- Production Strategy A remains untouched.
- No EMA50/100 promotion.
- No threshold mining.
- No VAL/Fresh optimization.
- No historical result is allowed to decide source meaning.
- AI does not generate BUY/SELL decisions.

## Continuation instruction for next chat
Start from this checkpoint. First inspect the GitHub branch and the G4/G5 source-resolution documents, then continue the SP2L V2 research from G4/G5 without asking the user to re-upload the transcript; the source is already stored in GitHub.