\# SP2L Live Demo Gateway Verification — 2026-09-20



Branch:

research/sp2l-live-mt5-telegram-2026-09-19



\## Verified



\### MT5 Connection

\- Terminal: Otet Group MT5 Terminal

\- Server: OtetGroup-MT5

\- Symbol: XAUUSD.ecn

\- connected: PASS

\- trade\_allowed: PASS



\### Gateway

\- Script:

&#x20; scripts/live\_mt5\_gateway.py



Verified:

\- approved\_signal.json loading

\- signal schema validation

\- MT5 request construction

\- dry-run execution path



\### Execution Safety

LIVE\_TRADING\_ENABLE=false



Result:

\- No broker order sent

\- Execution request archived as DRY\_RUN



\### Journal



Verified files:

\- runtime/journal/signals.jsonl

\- runtime/journal/trades.jsonl

\- runtime/journal/market\_snapshots.jsonl



Result:

PASS



\## Not Yet Verified



\### Telegram Delivery

Status:

IMPLEMENTED BUT CREDENTIAL TEST PENDING



Reason:

TELEGRAM\_BOT\_TOKEN and TELEGRAM\_CHAT\_ID are not configured in repository environment.



\### Strategy Integration



Current boundary:



Approved Signal

&#x20;       |

&#x20;       v

Live Gateway

&#x20;       |

&#x20;       v

MT5 / Telegram / Journal



SP2L geometry detection is intentionally not connected.



\## Current Safety State



\- Live order execution: OFF

\- Strategy auto-generation: OFF

\- Dry-run execution: PASS



Next gate:

Credentialed Telegram delivery test and controlled demo observation.

