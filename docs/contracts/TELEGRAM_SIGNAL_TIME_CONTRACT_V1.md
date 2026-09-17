# Telegram Signal Time Contract v1

**Status:** FROZEN PRESENTATION/COMPARISON CONTRACT  
**Scope:** XAUUSD Strategy A / SP2L research signal-source alignment  
**Canonical Telegram display timezone:** `Asia/Tehran`  
**Canonical MT5 research timestamp basis:** UTC  

## 1. Purpose

Freeze the project's handling of Telegram signal timestamps so that Telegram message times are compared and reported in Tehran time without changing the canonical MT5 dataset timestamps.

This contract concerns timestamp representation only. It does not define SP2L geometry, trigger rules, execution semantics, or BUY/SELL decisions.

## 2. Frozen rules

1. Telegram signal timestamps used for human-readable signal records shall be represented in `Asia/Tehran`.
2. The original Telegram timestamp/source representation must be preserved as raw evidence whenever available.
3. MT5 bar timestamps remain canonical UTC under `MT5_TIMESTAMP_CONTRACT_V1`.
4. Converting a Telegram timestamp to Tehran time must not modify or shift the underlying MT5 bar timestamps.
5. Tehran conversion is a comparison/presentation-layer operation, not an acquisition-layer timezone correction.
6. Any matching between a Telegram signal and MT5 bars must compare absolute instants, with Telegram rendered in `Asia/Tehran` and MT5 retained in UTC.
7. No broker/server/local offset may be applied to MT5 data merely to make Telegram times align.
8. If a Telegram timestamp lacks enough information to establish its absolute instant unambiguously, the timestamp match remains `UNRESOLVED` rather than being guessed.

## 3. Canonical representation

Conceptually:

```text
Telegram raw timestamp
        -> establish absolute instant
        -> render as Asia/Tehran

MT5 raw epoch
        -> canonical UTC timestamp

comparison
        -> absolute instant / epoch
        -> no MT5 timestamp shift
```

## 4. Separation from session calendar

Telegram timezone presentation is independent of the MT5 session-calendar contract.

The MT5 session calendar remains unresolved until supported by terminal-side historical evidence. Telegram timestamps must not be used to infer broker session hours, DST behavior, or historical market availability.

## 5. Evidence status

### User/project requirement

- Telegram signal time should be recorded/displayed in Tehran time.

### Existing canonical research rule

- MT5 bar timestamp basis is UTC with no manual timestamp shift under `MT5_TIMESTAMP_CONTRACT_V1`.

### Not defined here

- Telegram message ingestion/provider semantics;
- historical Telegram export timezone metadata;
- signal-message parsing rules;
- signal-to-bar matching tolerance;
- execution/fill semantics;
- SP2L geometry.

## 6. Frozen decision

**FROZEN:** Telegram signal timestamps are a Tehran-time presentation/comparison layer (`Asia/Tehran`), while MT5 remains canonical UTC.

**UNRESOLVED:** Any Telegram source timestamp whose absolute instant cannot be established from source evidence remains unresolved.
