# Python MT5 History Position Filter — Source Resolution (2026-11-16)

**Branch:** `research/multi-account-foundation-rfc-20261116`  
**Classification:** offline source research; non-canonical; no MT5 connection, account access, broker query, or Runner interaction.

## 1. Question

What identity value is intended for the `position=` argument of:

- `MetaTrader5.history_orders_get(position=...)`
- `MetaTrader5.history_deals_get(position=...)`

The Python Integration pages repeatedly call the argument a “position ticket”, which can be confused with the current `POSITION_TICKET`. The same pages specify the actual history fields used for filtering.

## 2. Official source statements

### Python Integration: history orders

The official page states that `history_orders_get(position=POSITION)` returns orders whose `ORDER_POSITION_ID` property matches the supplied value. Its parameter description says the supplied “ticket” is stored in `ORDER_POSITION_ID`.

Source: https://www.mql5.com/en/docs/python_metatrader5/mt5historyordersget_py

### Python Integration: history deals

The official page states that `history_deals_get(position=POSITION)` returns deals whose `DEAL_POSITION_ID` property matches the supplied value. Its parameter description says the supplied “ticket” is stored in `DEAL_POSITION_ID`.

Source: https://www.mql5.com/en/docs/python_metatrader5/mt5historydealsget_py

### MQL5 field semantics

The official position properties reference defines `POSITION_IDENTIFIER` as the stable position identifier and says it is specified in each related order's `ORDER_POSITION_ID` and each related deal's `DEAL_POSITION_ID`. It separately defines `POSITION_TICKET` as the current position ticket, which can change in documented circumstances.

Source: https://www.mql5.com/en/docs/constants/tradingconstants/positionproperties

The official `HistorySelectByPosition(position_id)` reference explicitly names its argument as the position identifier (`POSITION_IDENTIFIER`) and selects history by the corresponding order/deal position-ID fields.

Source: https://www.mql5.com/en/docs/trading/historyselectbyposition

### MetaQuotes MQL5 book — Python integration chapter

The official MQL5 book describes both Python history functions as filtering by **position ID**, not by current position ticket:
- `history_orders_get(position=<POSITION_ID>)` selects by `ORDER_POSITION_ID`.
- `history_deals_get(position=<POSITION_ID>)` selects by `DEAL_POSITION_ID`.

Sources:
- https://www.mql5.com/files/book/mql5book.pdf
- Section 7.9.15, “Reading the history of orders and deals” (PDF text around printed pages 2034–2036).

## 3. Source-level conclusion

The phrase “position ticket” on the Python Integration pages is imprecise terminology. The documented filter keys are `ORDER_POSITION_ID` and `DEAL_POSITION_ID`; MQL5 defines those fields as the position identifier relationship, corresponding to `POSITION_IDENTIFIER`.

Therefore, the **documentation-derived intended key** for both Python `position=` filters is the position lifecycle identifier (`POSITION_IDENTIFIER`), not an independently observed current `POSITION_TICKET`.

This is a source interpretation of the documented fields and is strongly corroborated by the official MQL5 book's explicit “position ID” wording. It is not a claim that the Python wrapper implementation has been experimentally verified for every package release.

## 4. What is resolved and what remains open

**Resolved at documentation level:**
- `history_orders_get(position=x)` is documented to filter `ORDER_POSITION_ID == x`.
- `history_deals_get(position=x)` is documented to filter `DEAL_POSITION_ID == x`.
- Those fields represent the position identifier relationship, not a generic alias for the current `POSITION_TICKET`.
- The Python docs' use of “position ticket” should not be copied into internal contracts without qualification.

**Still unverified at implementation/version level:**
- The exact behavior of the installed MetaTrader5 Python package reported previously as version `5.0.6180` has not been independently tested.
- No source code for the compiled Python extension has been inspected.
- No recorded terminal/API result has been used to test a deliberately non-equal pair where `POSITION_TICKET != POSITION_IDENTIFIER`.
- Broker/terminal availability, history completeness, and the behavior of `None` versus an empty tuple remain separate concerns.

## 5. Safe research contract (not yet an adapter implementation)

A future read-only adapter specification may describe the `position=` argument as accepting a **position identifier** and must preserve the raw current ticket separately.

Before treating that behavior as verified for the installed package, require a controlled, read-only compatibility fixture or recorded evidence in which:
1. the observed current `POSITION_TICKET` differs from `POSITION_IDENTIFIER`;
2. the order/deal records carry the matching `ORDER_POSITION_ID` / `DEAL_POSITION_ID`;
3. the Python history filter is compared against explicit record filtering by those fields;
4. the package version, terminal build, account mode, query result, and `last_error()` are recorded;
5. no order, position, SL, TP, or account configuration is changed.

No such experiment is authorized or performed in this research step.

## 6. Next gate

Update synthetic fixtures to encode the documentation-derived mapping without pretending it is a runtime compatibility test. Then review a narrow, read-only mocked history adapter contract, including:
- query result states: valid empty, non-empty, and `None` error;
- preservation of raw `POSITION_TICKET` and `POSITION_IDENTIFIER`;
- explicit filtering by `ORDER_POSITION_ID` and `DEAL_POSITION_ID`;
- incomplete time windows and partial-history evidence;
- no implicit reconciliation, fill interpretation, or broker ownership inference.

Any installed-package compatibility test remains a separate, explicitly approved gate. No MT5 initialization, history call, broker connection, or active Runner interaction is part of this step.
