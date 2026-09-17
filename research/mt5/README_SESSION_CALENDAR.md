# SP2L MT5 Session Calendar Acquisition

Purpose: acquire broker/terminal-reported XAUUSD.ecn trade and quote session definitions without interpreting them.

## Run

1. Pull branch `research/sp2l-mt5-session-calendar-2026-09-17`.
2. Copy `research/mt5/Sp2lSessionCalendarDump.mq5` into the MT5 terminal's `MQL5/Scripts` directory (or open it directly in MetaEditor).
3. Compile it in MetaEditor.
4. Run the script from Navigator on the target MT5 terminal/account.
5. Keep the generated CSV unchanged. The script writes it to the terminal's **Common Files** directory because it uses `FILE_COMMON`.
6. Return the raw CSV to the project; do not manually convert its timestamps.

## What is captured

- Symbol: `XAUUSD.ecn` by default.
- Day of week.
- Session index.
- Trade sessions from `SymbolInfoSessionTrade`.
- Quote sessions from `SymbolInfoSessionQuote`.
- Raw terminal-reported session timestamps as epoch values and server-formatted text.
- A contemporaneous `TimeTradeServer()` and `TimeGMT()` observation in the MT5 Experts log.

## Deliberate non-inferences

This acquisition does **not**:

- convert session timestamps to UTC;
- infer a fixed server UTC offset;
- normalize DST;
- merge/split sessions;
- infer market-open/close semantics beyond the MT5 API's trade/quote session labels;
- modify historical M1 data;
- define SP2L geometry or execution rules.

Those interpretations remain unresolved until source evidence and cross-audit support them.
