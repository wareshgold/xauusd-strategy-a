# Strategy A — Poorsamadi Time Analysis Research V1

Date: 2026-09-05
Branch: `research/strategy-a-poorsamadi-geometry`
Source: `docs/strategy/source/POORSAMADI_TIME_ANALYSIS_SOURCE.txt`

## Research status

This document is a semantic research ledger, not an executable strategy specification. No production Strategy A rule is changed by this document.

The source transcript is preserved verbatim in the source file. The purpose here is to separate source-established timing concepts from examples, implementation assumptions, and unresolved details.

## 1. Core thesis

The source presents time analysis as a complementary axis to price action and horizontal levels, not as a replacement for the setup itself.

The final conceptual triad is:

- **Time = when**
- **Level = where**
- **Price action = how**

The source explicitly says signals should be prioritized rather than simply deleted: a price-action setup outside a tested time window is lower quality than the same setup inside a tested window.

## 2. Time window has priority over time point

A major source-established hierarchy is:

1. Time window
2. Time point

The source explicitly states that a time window has higher priority because time points are weaker from a backtesting perspective. A setup should therefore not be evaluated independently of the time window in which it occurs.

This is important for Strategy A: the current implementation's session filter cannot be treated as equivalent to the source's time-window concept without further research.

## 3. Time does not replace the setup

The source repeatedly states that time analysis, price action, SP2L, PBTB, MicroMap and levels are interconnected components.

The source does **not** establish a rule of the form `time window alone => trade`.

Instead, the intended decision chain is approximately:

`identify relevant time window -> identify relevant level/context -> wait for measurable price-action trigger -> manage according to the active timing context`

The trigger must remain measurable and backtestable. The source explicitly criticizes discretionary "in the air" entries because they cannot be measured, optimized, or repeated.

## 4. Personalization is explicitly encouraged

The source distinguishes between:

- globally recognizable windows,
- symbol-specific windows,
- personally backtested windows.

The recommended process is to discover important times from historical behavior and then validate them by backtest/forward test.

A time window is therefore **not canonical merely because it is mentioned in the video**. It becomes a candidate research feature until validated on the exact symbol, data source, timezone and timeframe used by Strategy A.

## 5. How important times are discovered

The source gives four discovery methods:

1. Historical backtesting.
2. Identify when the day's high/low formed.
3. Identify where the main trend/move started.
4. Identify where the largest movement occurred.

These are discovery methods, not yet executable Strategy A rules. Each needs a precise algorithm before it can enter deterministic code.

## 6. Gold timing references

The source describes gold as a highly active, effectively 24-hour instrument and gives global timing references for gold, Dow Jones and EUR/USD.

For gold, the transcript explicitly references the following timing structures/examples:

- a very early/Oceania region beginning around `00:00` and extending to approximately `02:30`;
- a `02:30` time point/window transition;
- a `03:00` time point;
- a `04:00` time point;
- `08:00–09:00` window;
- `09:00–10:00` window;
- `10:00–13:00` window;
- `13:00–15:30` window;
- `15:30–16:30` window;
- `16:30–18:00` window;
- `18:00–21:00` window;
- an explicit `18:30` time point inside the later structure.

The transcript also gives internal examples such as `17:00` inside `16:30–18:00` and `11:00` inside `10:00–13:00`.

These timestamps are source references, not yet validated Strategy A session rules. The exact boundaries and interpretation of every early window need to be reconstructed from the complete indicator logic/backtest evidence before codification.

## 7. Broker timezone is critical

The source explicitly warns that the listed hours are based on the broker/chart clock and should not simply be interpreted as Iran time.

The source says the reference timing is aligned with standard European broker chart time and is approximately/explicitly aligned with Istanbul time, while daylight-saving transitions can shift the practical local conversion.

Therefore Strategy A must store timing rules in an explicit timezone convention. We must not silently map these windows to UTC or Iran time.

### Research requirement

Before implementation, determine the actual timezone of the historical XAUUSD dataset timestamps and define a deterministic conversion layer:

`source candle timestamp -> broker/chart timezone -> timing-window classification`

DST behavior must be explicit and testable.

## 8. Time point vs time window

The source differentiates:

- **Time window:** a period in which a class of market behavior is expected/observed.
- **Time point:** a specific moment that can mark a change in market narrative or pressure.

A time point can be nested inside a time window. Example from the source: `16:30–18:00` is a window, while `17:00` is a time point within it.

Time points are useful for management and narrative transitions, but the source explicitly places the broader window first in the hierarchy.

## 9. Window transitions can change management

The live examples repeatedly use an approaching time point/window as a reason to change trade management:

- reduce exposure,
- half-close,
- close fully,
- allow the position to continue if the new window confirms the direction,
- reassess whether a new setup is forming.

The source's example around `03:00` is especially explicit: actions are taken before the new window, followed by observation of whether the new timing regime continues in the trade's direction.

This suggests a research hypothesis for Strategy A: **time may be more useful as a state-transition / conditional-management feature than as a simple entry filter.**

This is a hypothesis only; it requires OOS testing.

## 10. Time + level + price action

The source gives a clear ordering of signal quality:

- time + level + measurable price-action trigger = highest-quality combination;
- time + price action without level = possible, but lower priority;
- level + price action without time = possible, but lower priority;
- price action alone = lower priority;
- time + level without a measurable price-action trigger is explicitly criticized as difficult/non-robust to backtest.

For Strategy A this supports a feature hierarchy rather than a binary session gate.

## 11. Time changes the meaning/weight of the same pattern

The source's core rule is that the setup does not necessarily change; its meaning/weight changes with time.

A visually identical price-action pattern at two different times can have materially different empirical outcomes because different market participants, liquidity and activity are present.

This is directly relevant to the existing Strategy A session-performance research: any timing effect should be tested as an interaction with the deterministic setup, not assumed to be a standalone edge.

## 12. Market participants change through the day

The source attributes intraday differences to changing participants, behavior and volume across Asia, Europe and America.

It also warns against treating generic volume indicators as a necessary confirmation because the trader does not observe the complete market volume and price behavior already contains important information.

For this project, this is contextual rationale only. It is not a rule to remove/add any indicator without empirical testing.

## 13. Dead-market testing principle

One of the strongest research statements in the source is methodological: a system should be tested in poor/dead timing conditions, not only in attractive London/New York windows.

The speaker uses Oceania/Asia/dead hours as a stress test and argues that a system that works only in one favorable timing window may be accidental rather than robust.

This is highly compatible with the project's existing anti-overfitting policy and suggests a timing robustness test:

- evaluate the canonical Strategy A setup across poor and strong timing regimes;
- compare effect sizes and uncertainty;
- do not optimize thresholds on the same validation set used to judge the hypothesis.

## 14. Time windows and SP2L

The source repeatedly demonstrates SP2L inside selected timing windows. The important semantic relationship is:

`time window -> context/level -> SP2L or another measurable price-action trigger`

The source does not justify a universal rule that every SP2L inside a named window is valid.

Instead, it explicitly says the setup must be backtested on the relevant window and symbol.

## 15. Time and exhaustion/pressure context

The source provides an important connection to the prior gap research:

- a move/gap late in a timing sequence can be interpreted as exhaustion;
- a move/gap in an earlier/active part of a sequence can act as pressure/continuation context;
- the same visual pattern can have different meaning depending on its time and location.

This reinforces the earlier finding that P-GAP vs E-GAP cannot be defined from geometry alone. Time/session and location are contextual variables.

No executable exhaustion rule is established here.

## 16. End-of-day discipline

For the day-trading horizon, the source explicitly describes closing trades by the end of the broker day rather than silently converting a failed day trade into a multi-day hold.

This is a behavioral/risk rule from the source, but the exact Strategy A implementation still needs a precise broker-day definition and a separate validation decision.

## 17. Journal/sample-size principle

The source repeatedly emphasizes backtesting and journaling rather than trusting a single live example. One explicit example uses a 60-sample journal to evaluate a specific entry behavior.

This does **not** establish that 60 trades are statistically sufficient for Strategy A. It establishes the source's methodological preference for repeated samples over anecdotal outcomes.

## 18. Direct implications for current Strategy A

### Existing assumption that must remain provisional

Current `Context.ts` uses:

- EMA period 60
- round step 50
- round distance 5
- London 07:00–16:00 UTC
- New York 13:00–22:00 UTC

The new source does **not** establish these exact UTC session boundaries as canonical. In particular, the source's broker-time convention and DST comments mean that direct UTC equivalence must be verified.

Therefore these current values should be treated as implementation assumptions/research baseline, not as source truth.

### Recommended research direction

Do not immediately replace the current session filter.

Instead, construct a frozen timing-classification research layer and test:

1. canonical Strategy A setup outcome by source-referenced window;
2. outcome by time point proximity;
3. interactions between timing window and direction;
4. interactions between timing window and SP2L structure quality;
5. interactions between timing window and location/level quality;
6. robustness across chronological DEV/VAL/fresh holdout;
7. poor-window stress performance.

## 19. What is NOT yet established

The transcript does not provide enough evidence to canonically specify:

- exact machine-readable XAUUSD window definitions for every hour;
- exact timezone/DST algorithm for our dataset;
- exact number of minutes around each time point;
- whether windows are inclusive/exclusive at boundaries;
- exact entry cutoff rules;
- exact management action required at each time point;
- universal TP/SL behavior by window;
- a universal direction bias for each window;
- exact interaction coefficients between time and SP2L;
- whether the named global windows remain optimal on our historical data;
- whether the examples are representative enough to become rules.

All of these remain research questions.

## 20. Research hypotheses to test next

### H1 — Time-window conditional edge

`Y` differs materially across timing windows for the same canonical Strategy A setup.

### H2 — Time × direction interaction

Some timing windows have asymmetric BUY/SELL performance.

### H3 — Time × setup-quality interaction

Timing may strengthen/weaken otherwise identical setup-quality states.

### H4 — Time × entry-edge interaction

The previously observed entry-edge weakness may vary by timing window.

### H5 — Time-point transition effect

Performance/MAE behavior changes near major source-referenced time points.

### H6 — Poor-window robustness

A system that retains reasonable expectancy in poor/dead windows is less likely to depend on a narrow timing artifact.

These are hypotheses, not conclusions.

## 21. Canonical-source rule

The following distinction must be preserved throughout future implementation:

- **Source-established:** explicitly stated by the transcript.
- **Source-example:** demonstrated in a live chart but not necessarily universal.
- **Research hypothesis:** proposed for statistical testing.
- **Implementation assumption:** current code behavior not proven by the source.
- **Validated rule:** survives the project's chronological/OOS validation protocol.

Only the final category may be promoted into production Strategy A behavior.
