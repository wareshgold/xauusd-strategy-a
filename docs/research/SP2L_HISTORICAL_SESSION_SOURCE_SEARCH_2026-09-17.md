# SP2L Historical Session Source Search — 2026-09-17

## Scope

Primary-source search for historical trading-session evidence applicable to `OtetGroup-MT5 / XAUUSD.ecn`, with emphasis on July 2026.

## Findings

### 1. Otet current financial-holiday calendar

The official Otet financial-holidays page states that the displayed schedule times are **MT5 server time** and that the market calendar is updated monthly. The current page is the September 2026 schedule and therefore is not a historical July schedule. It lists XAUUSD holiday exceptions for September, confirming that symbol-specific holiday schedules exist. Source: https://otetmarkets.com/financial-holidays/

### 2. July 2026 historical page

The historical-looking URL `https://otetmarkets.com/july-2026/` currently redirects to the current financial-holidays page. Therefore the July page is not presently available through the live official site as a preserved historical schedule.

### 3. Official broker time-zone evidence

Otet's terms state that the trading platform time zone is EET, equal to GMT+2 in winter and GMT+3 in summer, and that terminal graphics and trading-server log events are reflected according to EET. The same document states that schedules can be adjusted because of liquidity-provider changes. This is useful for time-zone interpretation but does not by itself reconstruct the exact historical XAUUSD.ecn session schedule for July 2026.

### 4. Official historical holiday evidence already located

Otet's 2026 holiday material includes historical XAUUSD exceptions. The April 2026 page records XAUUSD as closed on 3 April 2026. The May 2026 page records a 19 June 2026 XAUUSD close at 20:00. These establish that historical month-specific exceptions exist, but they do not provide the complete July regular session calendar.

## Resolution status

`HISTORICAL_SESSION_CALENDAR = UNRESOLVED`

The search did **not** locate a preserved official July 2026 Otet schedule that is sufficient to establish the complete regular session boundaries and all exceptions for `OtetGroup-MT5 / XAUUSD.ecn`.

## Consequence

Do not infer the historical calendar from the July candle pattern. Do not modify or repair the dataset to force agreement with the current calendar. Do not mark July `AUDITED_PASS`.

## Next evidence source

The highest-value remaining evidence is a broker-provided archived July 2026 trading-hours schedule or an account/terminal record that explicitly identifies historical sessions for `OtetGroup-MT5 / XAUUSD.ecn`. If unavailable, July remains unresolved and the project should move to months for which source evidence can be established, while preserving July as unresolved rather than silently excluding it.

## Research gates

- Current terminal/session metadata: resolved.
- Current symbol specification: resolved.
- Historical July session applicability: unresolved.
- July audited dataset: blocked.
- SP2L geometry canonicalization: blocked.
- Production BUY/SELL: not authorized.
