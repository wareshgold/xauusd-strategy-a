# SP2L G227 — P-Gap Synthetic Fixture Matrix

**Date:** 2026-09-10  
**Gate:** SYNTHETIC FIXTURES  
**Status:** `FIXTURE_SPEC_READY_SOURCE_DECISION_PENDING`

## Purpose

Create deterministic OHLC fixtures that separate competing P-Gap interpretations before any historical optimization. These fixtures test implementation behavior; they do not decide which interpretation is canonical.

## Hypotheses under test

- **H1 Generic Gap:** bullish `High[t-2] < Low[t]`; bearish mirror remains a candidate pending direct source confirmation.
- **H2 Breakout Gap context:** H1 plus the source-described beginning-of-move / close-location context.
- **H3 SP2L-specific P-Gap:** an additional condition not yet uniquely resolved from source.
- **Body-only candidate:** gap judged from candle bodies rather than full wick extrema.

## Fixture matrix

| ID | Purpose | Key OHLC relation | H1 | H2 | Body-only | Source status |
|---|---|---|---|---|---|---|
| PG-01 | Clean bullish wick gap | `High[t-2] < Low[t]`, bodies and wicks separated | PASS | context-dependent | PASS | compatible |
| PG-02 | Wick overlap / body separation | `High[t-2] >= Low[t]`, but body ranges separated | FAIL | FAIL | PASS | unresolved discriminator |
| PG-03 | Gap + breakout close context | H1 true + source-described breakout context | PASS | PASS | context-dependent | strong discriminator |
| PG-04 | Gap without breakout context | H1 true, context intentionally absent | PASS | FAIL | context-dependent | strong discriminator |
| PG-05 | Adjacent-only separation | adjacent candle separation but `High[t-2] >= Low[t]` | FAIL | FAIL | possible PASS | indexing discriminator |
| PG-06 | Exact-touch boundary | `High[t-2] == Low[t]` | FAIL under strict `<` | FAIL under strict `<` | candidate-dependent | strictness unresolved |
| PG-07 | Bearish mirror | `Low[t-2] > High[t]` candidate | candidate | candidate | candidate | direct source confirmation required |
| PG-08 | No gap / overlap | `High[t-2] > Low[t]` | FAIL | FAIL | FAIL | negative control |

## Proposed explicit OHLC values

Use simple deterministic prices so every fixture is independently auditable.

### PG-01 — clean bullish wick gap

- t-2: `O=100, H=105, L=99, C=104`
- t-1: `O=106, H=108, L=105.5, C=107`
- t:   `O=109, H=111, L=106, C=110`
- H1 predicate: `105 < 106` → PASS.

### PG-02 — body-only separation with wick overlap

- t-2: `O=100, H=106, L=99, C=105`
- t-1: `O=105.5, H=108, L=104.5, C=107`
- t:   `O=107, H=110, L=105.5, C=109`
- H1 predicate: `106 < 105.5` → FAIL.
- Body ranges may appear separated under a body-only interpretation.

### PG-03 — gap plus breakout context

- t-3: `O=100, H=104, L=99, C=103`
- t-2: `O=103, H=105, L=102, C=104`
- t-1: `O=106, H=108, L=105.5, C=108`
- t:   `O=109, H=112, L=106.5, C=111`
- H1 predicate: `105 < 106.5` → PASS.
- The fixture is reserved for the separate source-described breakout/close condition; that condition must be encoded only after its exact source mapping is frozen.

### PG-04 — generic gap without breakout context

Use the same H1 relation as PG-01 but place the sequence inside an established move rather than at its beginning. This fixture must not be hand-labelled as P-Gap until H2 is source-confirmed.

### PG-05 — adjacent-only gap

Construct OHLC so the immediately adjacent pair is separated while the t-2 high reaches or exceeds current low. This isolates indexing.

### PG-06 — exact touch

Set `High[t-2] == Low[t]` exactly. This tests strict `<` versus non-strict `<=` and must remain neutral until source evidence resolves the boundary.

### PG-07 — bearish mirror

Mirror PG-01 around a chosen price axis, but keep expected canonical classification unresolved until the raw SP2L source confirms the bearish OHLC rule.

## Acceptance rules for fixtures

1. Every fixture is deterministic and contains explicit OHLC values.
2. Expected outputs are recorded per hypothesis, not as a single canonical truth.
3. No fixture may be labelled as a production P-Gap solely because it is profitable historically.
4. Strict-boundary cases are mandatory to prevent accidental `<=` substitution.
5. Wick/body differences are mandatory to prevent silent geometry drift.
6. Candle indexing cases are mandatory.
7. Bearish symmetry is tested independently.
8. Any unresolved source mapping remains represented as `UNKNOWN`, not guessed.

## Promotion boundary

These fixtures may support future research implementation and unit tests, but **must not be connected to production Strategy A P-Gap detection** until B1 source geometry is frozen.

## Gate impact

- Source Resolution: **still BLOCKED**
- Synthetic Fixtures: **specification prepared**
- Frozen Geometry: **BLOCKED**
- DEV/VAL/Production: **UNCHANGED / NOT AUTHORIZED**
