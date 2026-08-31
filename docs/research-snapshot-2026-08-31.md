# Strategy A / SP2L — Research Snapshot

**Date:** 2026-08-31  
**Branch:** `research/spike-opportunity-window`  
**Repository:** `wareshgold/xauusd-strategy-a`

## Objective

The research direction is now explicitly **quality over frequency**. The target is not to manufacture signals every day. The intended live operating envelope is approximately:

- minimum target: about 1 high-quality trade on a suitable day
- maximum: 5 trades/day
- zero-trade days are valid when the market does not produce a qualified setup
- signals must be deterministic, explainable, and sufficiently robust for live decision support

This is a research target, not yet a validated production rule.

## Opportunity-window research

Current opportunity windows are treated as volatility/context regimes rather than automatic entry windows:

- `LONDON_OPEN_WINDOW`
- `PRE_NY_BUILD`
- `NY_OPEN_WINDOW`
- `LONDON_NY_OVERLAP`
- `OTHER`

The research found that high spike incidence does **not** imply that existing baseline entries perform well inside the window. Therefore, the system must separate:

1. identifying when the market is capable of producing a meaningful expansion/spike;
2. identifying whether a valid Strategy A structural sequence actually follows;
3. selecting only a small number of qualified entries.

## Key findings so far

### 1-minute

- Opportunity-window structural forensics were materially weaker than `OTHER` in the existing baseline.
- Entry-delay forensics showed a potentially interesting `D9_12` region, but its OOS sample was only 6 trades. This is hypothesis-generating, not sufficient for a rule.
- PRE-NY structural-chain forensics showed an interesting `SPIKE+EXPANSION+FVG_RETEST` result, but the OOS sample was only 4 trades. It cannot be promoted on sample size alone.
- Daily caps on the PRE-NY research subset remained positive in the existing two-way split, but this may reflect the same small sample and ranking assumptions.
- The later spike/sweep-quality diagnostic did **not** validate the full SPIKE→SWEEP chain; several apparently intuitive additions made the OOS result worse.

### 5-minute

- Opportunity-window results were generally weak.
- PRE-NY was less negative than several other windows, but the more complex structural chains did not have adequate OOS support.
- The 5-minute data currently does not justify selecting a complex PRE-NY entry chain.

## Important interpretation

The latest evidence does **not** justify adding more conditions blindly. In several tests, adding `SWEEP`, `BOS`, `DISPLACEMENT`, or `FVG` reduced performance. This is evidence that the current structural labels and/or their timing semantics may not match the intended SP2L pattern.

The next research step is therefore a **third chronological holdout stability test**, using fixed predicates already observed in research. No new threshold is fitted in that test.

Script:

`scripts/analyze-pre-ny-third-holdout-stability.mjs`

Output:

`data/reports/strategy-a-pre-ny-third-holdout-stability/{1min,5min}.json`

The split is:

- first third: development
- middle third: validation
- final third: untouched holdout

A candidate is only marked as surviving when the final holdout has a meaningful sample (`n >= 10`), PF >= 1, and positive average R. This is a diagnostic gate, not a production authorization.

## Current research decision

**NO production entry rule is promoted yet.**

The project remains in research/validation mode. In particular:

- do not hard-code PRE-NY as an entry filter yet;
- do not hard-code a 9–12 bar delay yet;
- do not hard-code `SPIKE+EXPANSION+FVG_RETEST` yet;
- do not optimize thresholds against the current holdout;
- keep zero-trade days allowed.

## Planned validation path

```text
Third chronological holdout
        ↓
Freeze any surviving candidate
        ↓
Independent dataset/source validation
        ↓
BUY vs SELL robustness
        ↓
Session/window robustness
        ↓
Day-level selection stability
        ↓
Forward/paper validation
        ↓
Live signal publishing
```

## TradingView / MetaTrader integration path

The strategy core must remain platform-independent. The intended boundary is:

```text
XAUUSD Market Data
        ↓
Strategy A Core
        ↓
Deterministic Signal Object
        ↓
API / Webhook Adapter
       ↙          ↘
TradingView      MetaTrader
(Pine/alert)      (EA/API bridge)
```

### TradingView

A future TradingView adapter can reproduce the validated deterministic rules in Pine Script and/or consume the same signal API through TradingView alerts/webhooks, depending on the final execution architecture.

TradingView must not become the source of truth for the strategy definition. The canonical rules remain in the Strategy A specification and validation code.

### MetaTrader 4/5

A future MT4/MT5 adapter can consume the same deterministic signal payload through an Expert Advisor, HTTP bridge, or broker-side integration. Execution-specific details such as symbol suffixes, spread, tick size, stop-distance rules, slippage, and broker session time must be handled by the adapter, not by the strategy core.

The architecture therefore preserves the option to:

- publish signals only;
- publish to Telegram;
- display/alert through TradingView;
- connect to MT4/MT5 for semi-automatic execution;
- later support automatic execution after separate execution validation.

## Non-negotiable architecture rule

The Strategy A core must not depend on Telegram, TradingView, MetaTrader, a specific broker, or Waresh Gold Assistant.

Those systems are adapters around the deterministic signal engine.

## Reproducibility

Historical data remains immutable research input. M5 should be derivable from M1 where practical so candle boundaries remain deterministic. No API credentials may be committed.
