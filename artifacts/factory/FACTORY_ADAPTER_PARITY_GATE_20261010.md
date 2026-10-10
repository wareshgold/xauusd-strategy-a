# Factory adapter parity gate — 2026-10-10

## Purpose

The Candidate Lab can enumerate and assess a finite research matrix, but real 1v1 results are only meaningful after the source implementations have honest historical adapters and share a frozen data/execution contract.

## Source facts captured for the Alireza reference

Reference implementation:
- Repository: `AlirezaSadabadi/PythonTraderBot`
- Path: `code/SP2L/SP2L_Advanced_Bot_Optimized.py`
- Captured source blob: `602c6b79d86189e044b9520689d963b746d74b5c`
- Role: `EXTERNAL_REFERENCE`, not canonical Strategy A.

The captured live implementation repeatedly evaluates the current forming M1 candle, including current low/high and setup predicates, on a polling loop. It uses the live entry check's retrace condition, EMA60 and trend filters by default, a 1R TP, and a stop anchored to the candle before the spike by default. Its configuration also has a 100 broker-point P-Gap and 1000-point maximum SL distance. These are source-profile facts, not canonical SP2L rules.

## Why a naive M1 OHLC 1v1 is blocked

Completed M1 OHLC bars do not contain the sequence of prices inside each candle. They cannot reproduce when a forming candle first satisfied or stopped satisfying Alireza's setup, nor the exact order of entry/stop/target events inside that minute. Replacing this with bar-close rules would be a new approximation, not an exact replay of the source implementation.

Therefore, the new `adapter_readiness` gate blocks a direct comparison when an adapter requires tick Bid/Ask or forming-candle path semantics but the dataset is only M1 OHLC. It also blocks missing common execution fingerprints, mismatched entry/exit semantics, unverified/different cost models, and absent trade ledgers.

## Next engineering sequence

1. Obtain an immutable XAUUSD tick Bid/Ask dataset covering the selected research window, or explicitly approve a separately labelled M1-bar approximation for both strategies. Do not label an approximation as exact upstream parity.
2. Implement isolated offline adapters for:
   - Internal SP2L V3 RR2/TRAIL4 baseline using its frozen source/profile.
   - Alireza source revision using the captured blob and explicit default configuration.
3. Add synthetic fixtures around setup/entry/SL/TP, same-bar ambiguity, and forming-candle/tick ordering before comparing real data.
4. Require both adapters to emit complete per-trade ledgers and the same frozen data and cost/execution fingerprints.
5. Run the exit candidate matrix (no trailing and declared activation/distance combinations) only within a predeclared development window. Do not tune on validation/holdout.
6. Report descriptive results and a validation shortlist only; no automatic winner, canonical promotion, production signals, or alteration of the independent RR2/TRAIL4 forward runner.

## Status

- Candidate matrix / deterministic shortlist layer: implemented as research infrastructure.
- Adapter readiness preflight: implemented, fail-closed.
- Actual internal and Alireza historical adapters: not yet implemented.
- Real 1v1 result: not available until the data and execution parity blockers are resolved.
- Active RR2/TRAIL4 forward evidence: preserved and not touched.
