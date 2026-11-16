# History-to-Recovery Gate — Offline Research Contract (2026-11-16)

**Branch:** `research/multi-account-foundation-rfc-20261116`  
**Classification:** offline research; non-canonical; synthetic observations only.  
**Status:** implementation and tests authored; operator-local validation pending.

## Purpose

Connect the paired Order/Deal observation to the existing fail-closed recovery fixture without allowing a query error or an empty tuple to become implicit permission to restore or bootstrap state.

## Gate order

1. Require a typed `HistoryPairObservation`.
2. Require pair status `BOTH_RESPONSES_VALID`; otherwise return `HALT`.
3. Require an explicit `history_completeness_verified=True` assertion from an independent evidence source; otherwise return `HALT`.
4. Only then delegate to the existing recovery contract, which independently checks account identity, inventory availability, event-journal completeness, linkage ambiguity, state integrity/schema, and the missing-state/empty-inventory bootstrap condition.

## Critical boundary

The gate does **not** calculate or establish `history_completeness_verified`. A pair of empty tuples is not a completeness proof. The boolean is an externally supplied assertion that must eventually be backed by a separately specified and source-aligned completeness protocol. Until that protocol exists, production callers must not set it based solely on the pair result.

This is a research fixture, not a production recovery implementation. It does not query MT5, inspect files, access accounts, reconcile records, or control a Runner. No order/deal linkage or broker fill semantics are defined here.

## Synthetic tests

`tests.test_sp2l_history_recovery_gate_research` covers failed pair, empty-pair insufficiency, explicit completeness gate, missing-state inventory ambiguity, corrupt state, identity/inventory/journal/linkage failures, valid restore, and invalid pair type.
