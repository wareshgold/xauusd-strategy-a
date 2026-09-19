# SP2L Live Signal Template

SP2L Strategy A
Signal ID: <unique-id>
Direction: <BUY/SELL>
Entry: <price>
SL: <price>
TP: <price>
Volume: <lots>
Status: SIGNAL
MT5: XAUUSD.ecn
Time: <UTC>

Required fields:
- unique signal_id
- direction BUY or SELL
- entry, SL, TP
- volume
- UTC timestamp

Execution states:
SIGNAL / DRY_RUN / EXECUTED / REJECTED / DUPLICATE_REJECTED

This is an interface contract only. It does not define SP2L geometry, fill semantics,
or canonical trading rules.
