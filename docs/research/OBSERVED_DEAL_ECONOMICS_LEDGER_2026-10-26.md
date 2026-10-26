# Observed Deal Economics Ledger — 2026-10-26

## Purpose

This synthetic research fixture summarizes explicitly supplied deal rows without treating missing values as zero and without asserting the supplied history is complete.

## Field treatment

Each row retains its deal ticket and carries optional observed volume, profit, commission, swap and fee. Aggregates are emitted only for a field when every supplied row has a finite value for that field. A missing required component blocks the net result; it is not silently substituted with zero. Empty input is not reported as zero volume or zero P/L.

The arithmetic net result is the sum of the explicitly supplied profit, commission, swap and fee values. This is a transparent fixture calculation, not a claim that every broker/account configuration uses identical reporting or accounting semantics.

## Fail-closed cases

- Empty deal ledger: EMPTY_LEDGER
- Missing economic field: INCOMPLETE_FIELDS
- Invalid/non-positive deal ticket, duplicate deal ticket, or non-finite supplied value: INVALID_RECORD
- Complete supplied values: OBSERVED_ONLY

Even OBSERVED_ONLY means only that the supplied rows had the fields needed for this arithmetic. It does not mean all deals were retrieved, that an order was fully filled, that the position is closed, or that the ledger reconciles to account history.

## Still unresolved

This fixture does not fetch MT5 history or reconcile request/order/deal history windows. It does not define broker-specific commission/fee conventions, partial-fill completion, netting versus hedging treatment, delayed history arrival, currency conversion, realized versus floating P/L, or lifecycle boundaries. Those need source and broker evidence before a performance replay.

## Test coverage

Synthetic tests cover signed costs, multiple deal rows, missing cost/volume, empty input, duplicate/invalid IDs and non-finite values. No live account, runner or local journal was accessed.
