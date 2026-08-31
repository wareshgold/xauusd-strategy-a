# Strategy A / XAUUSD Research Snapshot — 2026-08-31

## Frozen baseline
- Repository: `wareshgold/xauusd-strategy-a`
- Research branch at snapshot: `research/spike-opportunity-window`
- Frozen source commit: `15043f754281542617c105c61de13c32946a7207`
- Snapshot branch: `snapshot/2026-08-31-opportunity-forensics`
- Snapshot purpose: preserve the current research state before the next forensic iteration.

## Current research objective
Build a deterministic XAUUSD price-action signal system with **quality over quantity**.
- Target: normally 1–5 high-quality trades/signals per day.
- No requirement to force a daily trade.
- `NO TRADE` is valid when the setup is not sufficiently strong.
- Session/opportunity windows are hypotheses, not trading rules until independently validated.

## Evidence observed so far
### Opportunity windows
The current opportunity-window analysis shows elevated spike frequency around `PRE_NY_BUILD`, `LONDON_NY_OVERLAP`, and `NY_OPEN_WINDOW`, but raw opportunity-window trades are not profitable OOS by themselves.

### Structural forensics
Inside opportunity windows, the strongest recurring positive clue has been **delayed entry / expansion-related behavior on 1m**, but samples are small and contradictory across other timeframes.

### Entry delay
1m `D9_12` was the only clearly positive delay band in the latest forensic, with OOS PF `3.9504` on only `n=6`. This is hypothesis-generating, not a validated rule.

### PRE-NY
`PRE_NY_BUILD` is the most promising research area, especially on 1m. Earlier chain forensics showed positive OOS results for `SPIKE` and `SPIKE+EXPANSION+FVG_RETEST`, but the newer spike/sweep quality forensic produced poor OOS results. This discrepancy must be reconciled before any rule is adopted.

### Daily cap
1m PRE-NY cap tests looked positive for caps 1–5/day in the prior forensic, with strongest OOS statistics around lower caps. 5m did not confirm the edge. These are not yet production constraints.

## Critical unresolved issue
There is a **definition/universe mismatch risk** between the earlier PRE-NY structural-chain forensic and the newer PRE-NY spike/sweep-quality forensic. Before optimizing thresholds, reconcile:
1. exact trade universe,
2. spike detection/indexing,
3. session/window boundaries,
4. direction convention,
5. pre-entry lookahead rules,
6. OOS split definition,
7. handling of missing/ambiguous structural events.

## Next research path
1. **PRE-NY reconciliation forensic** — explain the conflicting results above.
2. Freeze one canonical feature/event definition.
3. Test spike quality independently of sweep quality.
4. Test entry timing/confirmation after the spike, without selecting thresholds from the same OOS sample.
5. Validate promising hypotheses on a third untouched chronological holdout.
6. Test independence across direction and session.
7. Only after survival, define the deterministic Strategy A entry/exit/risk rules.
8. Then build the live signal engine and Telegram delivery.
9. Keep broker/execution adapters separate from the core strategy so the same engine can later integrate with TradingView and MetaTrader/MT5.

## Integration architecture target
`Market Data -> Strategy A Engine -> Risk/Signal Engine -> Webhook/API -> Telegram`

Future adapters:
- TradingView/Pine Script for charting/alerts or data/alert integration.
- MetaTrader 5 EA as a live-data/execution adapter.

The core BUY/SELL decision remains deterministic and independent of either platform.

## Research discipline
- Do not optimize to maximize trade count.
- Do not force one trade per day.
- Do not promote small-n OOS findings to rules.
- Prefer stable expectancy/PF and controlled drawdown over headline win rate.
- Require out-of-sample and preferably third-holdout confirmation before productionizing a discovered edge.
