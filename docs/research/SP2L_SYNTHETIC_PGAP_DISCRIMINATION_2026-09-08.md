# SP2L Synthetic P-Gap Discrimination

**Date:** 2026-09-08  
**Branch:** `research/source-resolution-entry-level-v2`  
**Gate:** SOURCE RESOLUTION → SYNTHETIC FIXTURES  
**Production impact:** none

## Objective

Convert the remaining P-Gap ambiguities into deterministic synthetic fixtures without allowing historical profitability to decide source meaning.

The source establishes that P-Gap is a distinct gap type associated with valid breakout/spike context, and that the source treats multiple temporal spike constructions as one current strategy family. It does **not** yet provide enough precision to freeze wick/body boundaries, a minimum gap size, or a universal candle index.

## Fixture matrix

| ID | Synthetic condition | Wick candidate | Body candidate | Generic 3-candle candidate | Source-safe result |
|---|---|---:|---:|---:|---|
| PG-SYN-01 | Bullish adjacent candles: prior High < next Low; bodies also separated | yes | yes | maybe | candidate discriminator, not canonical |
| PG-SYN-02 | Bullish wick separation while bodies overlap | yes | no | maybe | must remain unresolved |
| PG-SYN-03 | Bullish bodies separated while wicks overlap | no | yes | maybe | must remain unresolved |
| PG-SYN-04 | Exact touch: prior High = next Low | depends on equality rule | depends | depends | equality unresolved |
| PG-SYN-05 | Breakout-first gap followed by higher lows | candidate | candidate | candidate | preserve as source-supported temporal variant |
| PG-SYN-06 | Higher lows first, gap on later candle | candidate | candidate | candidate | preserve as source-supported temporal variant |
| PG-SYN-07 | Gap only after several continuation pushes | candidate | candidate | candidate | not automatically P-Gap; E-Gap distinction blocks promotion |
| PG-SYN-08 | Generic three-candle imbalance without source breakout context | possible | possible | yes | reject as canonical P-Gap |
| PG-SYN-09 | Breakout + follow-through but overlapping ranges | no | no | no | not sufficient for P-Gap |
| PG-SYN-10 | Sharp directional/channel-like movement with overlap | no | no | possible | source says channel-like movement is not the spike-axis setup |

## Fixture interpretation rule

These fixtures are not optimization candidates. They exist to expose whether a proposed implementation makes an assumption that the source has not resolved.

A fixture can receive a canonical expected value only when primary-source evidence identifies the relevant boundary/timing rule. Otherwise its expected value is explicitly `UNRESOLVED`.

## Current evidence outcome

### 1. Generic three-candle imbalance

**Rejected as canonical.** The source explicitly distinguishes P-Gap from other gap types and discusses more than one temporal construction. A generic three-candle detector therefore cannot be substituted for P-Gap merely because it is easy to implement.

### 2. Wick-range non-overlap

**Strong candidate, not frozen.** The source language and drawings support non-overlap around breakout. The available frames do not establish that the exact boundaries are always wick High/Low.

### 3. Body-range non-overlap

**Unresolved.** It remains possible from the available visual resolution but lacks sufficient direct textual confirmation.

### 4. Timing

**Multiple constructions are source-supported.** The source describes breakout-first and higher-lows-first constructions as conceptually equivalent for the current strategy. Therefore a universal fixed candle index is unsafe.

### 5. Location / early trend

**Source-confirmed concept, executable threshold unresolved.** The source distinguishes P-Gap from later E-Gap conditions and ties the distinction to location/context. No numeric "early" threshold is authorized.

## Entry cross-check

The same fixture family must keep the pending-limit entry separate from P-Gap geometry. Source evidence strongly supports a Buy Limit during the first correction and the mirrored Sell Limit for bearish setups, with the correction described around the prior candle Low/High. However, the exact price of the pending order remains a source-resolution item rather than an assumed equality with a P-Gap boundary or classical C point.

## SL cross-check

Stop/invalidation is structural and can change the pending-order lifecycle when the subsequent candle materially changes the stop distance. The exact structural OHLC anchor is still unresolved. Synthetic fixtures must therefore test candidate anchors without promoting one to canonical.

## Gate decision

**SYNTHETIC FIXTURES:** defined and ready for deterministic implementation.  
**P-Gap formula:** still unresolved.  
**Generic 3-candle imbalance:** rejected as canonical.  
**Entry:** pending-limit semantics confirmed; exact limit price unresolved.  
**SL:** structural invalidation confirmed; exact anchor unresolved.  
**Production:** unchanged.

## Next action

Implement the fixture harness as research-only assertions that enforce these provenance states, then perform the final source-resolution pass on entry/SL/Leg-1 alignment. No historical optimization or production integration should occur before the geometry freeze.
