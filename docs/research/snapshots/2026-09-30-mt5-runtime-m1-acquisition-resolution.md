# SP2L Research Snapshot — MT5 Runtime M1 Acquisition Resolution

**Date:** 2026-09-30  
**Project:** XAUUSD Strategy A / SP2L  
**Status:** RESEARCH-ONLY / NON-CANONICAL  
**Branch:** `research/sp2l-legacy-mirror-backtest-20260929`

## Executive finding

The 2026-09-30 bounded runtime acquisition diagnostic resolved the apparent MT5 history contradiction.

The MT5 Strategy Tester has synchronized **2026 real-tick history**, but the EA's preloaded **M1 history cache initially ends at 2025-12-31 23:59 UTC**. During simulation, M1 bars can become available progressively up to the current simulated time.

Therefore:

- `OnInit()` cannot be used as evidence that the complete 2026 M1 series is unavailable.
- `CopyRates()` for future/current 2026 windows from `OnInit()` returns `4401` because those M1 bars are not yet present in the runtime series.
- The tester subsequently generates M1 bars from real ticks as simulation advances.
- The previous full-history M1 assumptions must therefore be separated from the tester's runtime tick-to-M1 generation semantics.

## Direct evidence

### Initial M1 cache

Tester journal:

```
XAUUSD.ecn,M1: history cache allocated for 632638 bars and contains 353895 bars
from 2025.01.02 01:00 to 2025.12.31 23:59
```

### Tick history

```
XAUUSD.ecn: history ticks synchronized from 2026.01.02 to 2026.09.28
```

### Bounded OnInit probes

- Boundary Dec/Jan: copied 5 bars, ending 2025-12-31 23:59.
- Jan 2026: copied=-1, error=4401.
- Jun 2026: copied=-1, error=4401.
- Sep 2026: copied=-1, error=4401.

### Runtime probe

During simulation:

```
RUNTIME_PROBE label=NEW_M1_BAR
sim_time=2026.01.16 07:48:00
copied=108855
first_utc=2025.09.25 01:00:00
last_utc=2026.01.16 07:48:00
copy_error=0
```

This demonstrates that M1 availability expands with simulated time.

## Consequence for the 68% question

The previously observed ~68% result is reproducible for its explicitly defined historical population, but this diagnostic does **not** establish a continuous one-year M1 population from 2025-09-25 through 2026-09-25.

No new performance claim is promoted.

The unresolved issue is now **data acquisition/reconstruction**, not another strategy-geometry probe.

## Frozen research boundary

- Source meaning remains authoritative.
- Frozen Geometry remains unchanged.
- No P-Gap formula, fill semantics, SL geometry, AB=CD geometry, or execution rule is inferred from this diagnostic.
- No backtest result promotes a rule to canonical.
- Production BUY/SELL generation remains disabled.

## Next gate

Build an auditable continuous M1 dataset from the available MT5 **real ticks**, using deterministic tick-to-M1 aggregation.

Required chain:

```
MT5 real ticks
  -> deterministic UTC M1 aggregation
  -> coverage/session audit
  -> frozen dataset + manifest/checksum
  -> independent SP2L replay
  -> same-population 68% verification
```

The resulting dataset must preserve actual availability and must not fabricate, shift, or fill missing data.

Only after the continuous dataset is frozen should the SP2L replay be rerun.
