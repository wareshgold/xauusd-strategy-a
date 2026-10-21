# XAUUSD Tick Research Eligibility Matrix

Status: research-only guardrail, 2026-10-21  
Scope: existing XAUUSD.ecn MT5 `COPY_TICKS_ALL` capture and offline analyses  
Authority: this document does not define canonical SP2L geometry or execution semantics.

## Source facts and unresolved items

- The captured CSV.GZ and manifest are immutable research inputs. Preserve their SHA-256, byte size, row count, and original row order.
- The capture contains repeated `time_msc` values with differing Bid/Ask quotes. A timestamp is millisecond precision; it does not establish a unique sub-millisecond event order.
- The reviewed MetaQuotes `MqlTick` flag reference documents bits 2, 4, 8, 16, 32, and 64, but does not define bit 128. The official Python `copy_ticks_range` example itself contains values 130 and 134. Therefore bit 128 is undocumented in reviewed sources, not by itself proof of corruption.
- Tick order within equal `time_msc` remains unresolved. Do not sort, deduplicate, infer hidden precision, or select a “correct” quote sequence without authoritative source evidence.
- OHLC intrabar ordering, touch/penetration/close fill semantics, Bid/Ask/Last execution choice, and Strategy A geometry remain separate unresolved source questions.

## Eligibility matrix

| Analysis | Status | Constraints |
|---|---|---|
| File integrity, manifest hash/size/row-count verification | ALLOWED | Read-only; report mismatches explicitly. |
| Row counts, timestamp duplicate profiles, flags distribution, spread distributions | ALLOWED | Descriptive only; retain raw flags and row order. |
| Quote-level summaries grouped by exact `time_msc` | ALLOWED WITH CAVEAT | A group is a set of same-millisecond observations, not a proven ordered micro-sequence. |
| Time-bucket aggregates (e.g. minute-level spread summaries) | ALLOWED WITH CAVEAT | State the aggregation and do not use as proof of executable path/order. |
| Reconstructing a unique within-millisecond quote path | BLOCKED | Ordering evidence is insufficient. |
| Tick-order-sensitive threshold-touch sequencing | BLOCKED / NOT CERTIFIED | Must not certify execution outcomes from ambiguous equal-millisecond ordering. |
| Fill, stop-loss, take-profit, or trailing simulation requiring an event sequence | BLOCKED unless independent semantics and ordering are source-confirmed | No guessed fill policy or price field. |
| Strategy A signal generation or production BUY/SELL decisions | OUT OF SCOPE | AI/research diagnostics cannot define canonical rules or issue production decisions. |

## Required report labels

- Integrity gate and execution eligibility are separate outputs.
- Use `NOT_CERTIFIED` when duplicate timestamps contain different quotes or UTC/time inconsistencies are present.
- Use `NOT_ESTABLISHED` when the current audit has not demonstrated an order-sensitive execution problem but also has not certified the needed semantics. This is not a pass.
- Never translate either label into “dataset corrupt” or “strategy invalid” without further evidence.

## Exit criteria for blocked tick-order-sensitive validation

1. Obtain authoritative clarification for the meaning of flag bit 128 for this acquisition API/feed, or explicitly retain it as opaque if no clarification is available.
2. Establish whether MT5 or broker source data supplies a deterministic order for distinct ticks with equal `time_msc`; if not, define no substitute order by assumption.
3. Separately resolve execution price field, touch/penetration/close semantics, spread treatment, and relevant order lifecycle rules from source-approved specifications.
4. Build synthetic fixtures for every confirmed rule and ambiguity boundary.
5. Freeze the source-approved specification before implementation and keep fresh holdout data untouched until validation design is frozen.

## Non-goals

This matrix does not repair data, discard duplicate rows, define P-Gap/AB=CD geometry, choose a fill model, change the forward runner, alter trailing settings, or authorize production use.
