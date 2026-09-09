# G50 — Multi-Window Acquisition Runner

Status: IMPLEMENTATION READY; REAL RUN REQUIRED

## Scope

G50 adds strategy-neutral orchestration over the G49 deterministic historical window/chunk planner and G48 real Twelve Data acquisition runner.

Pipeline:

`Historical Windows → deterministic chunks → Twelve Data acquisition → raw preservation → UTC normalization → quality audit → per-chunk manifest/artifact → dataset manifest`

## Safety boundaries

- API credentials are supplied only through an environment variable.
- Credentials are never written into manifests or printed.
- No missing candles are fabricated.
- No feed is mixed with another feed.
- No Strategy A geometry, BUY/SELL detection, optimization, or performance selection is performed.
- A chunk with failed quality status prevents an overall PASS.

## Real-run requirement

G50 is not PASS until the runner is executed with the real Twelve Data API and all planned chunks return PASS. The resulting dataset manifest and fingerprints must be retained as research artifacts outside source control unless intentionally versioned as metadata-only artifacts.
