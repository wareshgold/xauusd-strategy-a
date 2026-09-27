# XAUUSD Cross-Symbol Raw-Bar Control

Research-only forensic step.

The control compares the same 58 XAUUSD unresolved non-weekend gap intervals
against M1 boundary observations for seven liquid FX control symbols:

- USDJPY
- EURJPY
- GBPUSD
- GBPJPY
- EURUSD
- USDCHF
- USDCAD

It queries the same UTC interval around each XAUUSD gap and records the nearest
M1 bar before the gap start and the nearest M1 bar at/after the gap end.

This is deliberately descriptive. A control-symbol match or mismatch does not
by itself establish broker session closure, maintenance, feed behavior, or a
canonical XAUUSD data rule.

Current evidence boundary remains:

`SESSION_CAUSE=UNRESOLVED`
`SESSION_APPROVAL=NOT_ESTABLISHED`
