# SP2L MT5 Source Baseline — Research Lock

Status: RESEARCH ONLY — NOT CANONICAL
Date: 2026-09-27

## Purpose

This document freezes one reproducible MT5 research baseline so historical results are not compared across different detectors, indexing, fill semantics, or filters.

## Single baseline contract

- Instrument: XAUUSD, broker-resolved symbol recorded by the runner (expected XAUUSD.ecn)
- Timeframe: M1
- Data source: connected MT5 terminal only
- Window for first controlled replay: 2026-09-14T00:00:00Z through 2026-09-25T23:59:59Z
- P-Gap threshold: 1.0 XAUUSD price unit (research hypothesis; not source-confirmed)
- Setup: Before-Spike → Spike → After-Spike
- Spike body: > 1.5× Before-Spike and > 1.5× After-Spike
- Trigger: first later candle with BUY current Low < previous Low, or SELL current High > previous High
- Entry: Trigger Low/High
- SL: Before-Spike Low/High
- TP: 1R
- Maximum accepted risk: 10.0 price units
- EMA/ATR/ADX/trend/session filters: OFF
- 2X: OFF

## Explicit unresolved items

No canonical decision is made here for exact P-Gap source formula, trigger touch/penetration/close semantics, intrabar fill chronology, exact SL wick/body/buffer semantics, AB=CD anchors/tolerance, or 2X lifecycle.

The mechanical outcome evaluator must be treated as a research assumption and versioned separately from source geometry. No positive result may promote this contract to canonical Strategy A.

## Reproducibility requirements

Every replay artifact must record:
1. Git commit SHA
2. detector module SHA
3. runner SHA
4. exact MT5 symbol
5. timeframe
6. UTC window
7. complete configuration
8. raw-bar acquisition method
9. signal count and signal ledger hash
10. outcome convention and ambiguity policy

## Rule

If two results disagree, do not average or choose the better result. First prove whether the code, data, configuration, signal ledger, or outcome evaluator differs.
