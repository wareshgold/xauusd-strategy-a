# SP2L Research Snapshot — 2026-09-26 — Pre-Coding-Test Checkpoint

## Snapshot identity

- Repository: `wareshgold/xauusd-strategy-a`
- Branch: `research/sp2l-pgap-source-aligned-2026-09-26`
- Base commit: `3df432a8f880ef555777dbcbafa7a7f57b60574c`
- Base commit message: `research: add continuous MT5 polling forensic capture`
- Purpose: preserve a clean research checkpoint before any Cline/Gemini coding experiment.

## Source-resolution status

The project remains source-first. Only source-confirmed rules may become canonical.

Source-confirmed from the official author material:

- F12 bullish trigger reference: BUY correction reaches the Low of the previous candle.
- F15 bearish trigger reference: SELL correction reaches the High of the previous candle.
- F13 2X: secondary entry is at 50% of Entry-to-SL distance.
- F10 stop concept: SL is behind the candle from which the Spike starts.
- F14 AB=CD concept.

Still unresolved:

- universal P-Gap formula and candle-role mapping;
- trigger acceptance semantics;
- trigger candle indexing;
- entry-price anchor;
- fill semantics;
- exact SL boundary;
- F13 order lifecycle;
- AB/CD anchors and equality tolerance;
- bearish complete execution mirror;
- cancellation/expiry semantics.

No unresolved geometry is promoted to canonical status.

## P-Gap status

The current research branch records the source-aligned strict separation condition:

- BUY research condition: `correction.low > a.high`
- SELL research condition: `correction.high < a.low`

Existing research window roles remain `a, spike, correction, trigger = [-5],[-4],[-3],[-2]`.

Important boundary:

- `p_gap_price=0.0` is the source-aligned strict-separation research condition.
- Positive thresholds are counterfactual sensitivity tests only.
- The candle-role mapping is not source-frozen.
- Legacy guessed formulae such as `Low[1] > High[3] + 1` are not canonical.

One-month MT5 replay/sensitivity work may quantify implementation differences, but performance cannot select the canonical source meaning.

## Forensic continuity status

Three historical intervals remain explicitly:

**UNRESOLVED — continuous polling not proven from preserved evidence.**

Intervals:

1. 2026-09-24 10:00–10:15 UTC
2. 2026-09-24 11:45–12:05 UTC
3. 2026-09-24 12:35–12:55 UTC

The preserved event log has no matching events for those windows. The absence of events is not treated as proof of an outage.

The frozen runner log and prior telemetry do not cover the historical intervals.

## MT5 API parity status

A same-terminal forensic comparison of `copy_rates_range()` and `copy_rates_from()` was completed for the observed Sep 24 windows. The returned timestamp sequences and OHLC data were exactly equal in all three comparisons.

This proves API parity for those observed windows only. It does not prove continuous forward-loop polling.

## Continuous polling forensic runner

Commit `3df432a` added:

`scripts/run_sp2l_continuous_poll_forensics.py`

Its intended boundary is research-only and detector-independent:

- records every polling iteration;
- records raw MT5 acquisition metadata;
- records raw candle timestamp/OHLC data;
- records errors and lifecycle events;
- does not run the Strategy A detector;
- does not place orders;
- does not send Telegram messages;
- does not change Strategy A geometry or canonical status.

This separation is intentional: polling continuity is a separate evidence layer from detector continuity.

## Cline/Gemini coding experiment status

Cline/Gemini read-only repository inspection tests were completed successfully and produced source-aligned status assessments.

A subsequent coding test was attempted but did not execute because the Cline Credits balance was insufficient (`$0.01`). Therefore:

- no Cline coding change is accepted from that attempt;
- no Cline commit is accepted;
- no PR is created;
- no repository rollback is required.

The planned coding test remains available for a future run: add deterministic tests around the continuous polling forensic runner without changing production semantics, Strategy A geometry, execution, Telegram, or canonical rules.

## Safety boundary at this snapshot

- Canonical Strategy A BUY/SELL generation: not promoted by this snapshot.
- Live trading: not enabled by this snapshot.
- Source meaning remains authoritative over backtest performance.
- Research diagnostics remain research-only.
- Historical continuity claims remain unresolved where preserved evidence is incomplete.

## Next controlled step

Before any coding change is accepted:

1. obtain sufficient Cline/Gemini credits or use another controlled development path;
2. run the small deterministic forensic-runner test task;
3. inspect the exact diff;
4. run tests;
5. verify no geometry/execution/canonical changes;
6. only then decide whether to commit the coding result.

This snapshot is a checkpoint, not a canonical-rule promotion.
