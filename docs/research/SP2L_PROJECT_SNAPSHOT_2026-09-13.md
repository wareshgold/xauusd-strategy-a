# SP2L Project Snapshot — 2026-09-13

## Project state
Research-first / source-first deterministic XAUUSD Strategy A (SP2L = Spike → 2 Leg).
No unresolved geometry has been promoted to canonical rules.

## Current branch / commit
- Branch: `research/sp2l-g388-dataset-runner-2026-09-13`
- HEAD: `eb8bee2057cae2f5f7b1a902b83d7bc4202c287d`
- Commit: `fix: correct G397 AB=CD fixture expectation`
- PR: #124 — `research: validate G393 hypothesis batch on current branch`
- Base branch: `research/sp2l-g386-dev-harness-2026-09-13`
- Base SHA: `523bed70d0c935664a8d80e59c3f8c10c516bf12`

## Latest source/evidence status
- G337: PASS — wick/body anchor source audit; exact OHLC mapping unresolved.
- G338: PASS — structural anchor/event source audit; semantic A/B/C/D roles supported, exact candle-field mapping unresolved.
- P-Gap executable geometry remains unresolved.
- AB=CD relationship is source-confirmed; exact A/B/C/D anchors and tolerance remain unresolved.
- Pending-limit entry is source-confirmed; fill price is not automatically geometric C.
- Next research gate remains controlled synthetic fixture discrimination before historical optimization.

## G393 / G397
- G393 test corrected to call `runHypothesisBatch([candle], config, noCanonicalStrategyAdapter(), () => null)`.
- G393 remains research-only and non-canonical.
- G397 is synthetic-only: separates competing P-Gap and AB=CD interpretations without promoting any hypothesis.
- Current commit contains the G397 fixture expectation correction.

## CI state at snapshot
Successful on the same SHA `eb8bee2`:
- G376 Hypothesis Fixture Runner — SUCCESS, run `34749107213`.

Problematic runs:
- G386 DEV Harness — QUEUED, run `34749107291`, jobs=[]
- G397 Synthetic Geometry Discrimination — QUEUED, run `34749107171`, jobs=[]
- G388 Dataset Runner — QUEUED, run `34749107243`, jobs=[]
- G396 Provenance Guard — QUEUED, run `34749107240`, jobs=[]
- Semantic V2 — STARTUP_FAILURE, run `34749107175`, jobs=[]
- G394 Outcome Simulator — STARTUP_FAILURE, run `34749107176`, jobs=[]
- G4/G5 Fixture Suite — STARTUP_FAILURE, run `34749107330`, jobs=[]

## Key diagnostic finding
On the same commit, six other GitHub Actions check runs were created and completed successfully around 09:12:50Z. G376 also created a real job and completed successfully. Therefore this is not currently explained by a general Actions outage or inability to run any workflow on the commit.

The affected workflows create workflow-run/check-suite records but do not create a Job. Therefore the failure/queue point is before checkout, Node, pnpm, TypeScript, or Vitest execution.

No blind rerun was performed.
No Strategy A geometry/rule was changed.
No production logic was changed.

## Next step for 2026-09-14
Compare workflow registration/trigger resolution for the affected workflows against a successful workflow on the same SHA. Focus on why GitHub creates the run/check suite but produces no job for G386/G388/G396/G397 and why Semantic V2/G394/G4-G5 reach startup_failure with no job.

Do not alter strategy geometry to resolve CI behavior.
Do not optimize historical performance until source geometry is frozen.
