# Strategy A — Poorsamadi Source Ledger

> **Status:** Source extraction v0.1 — research foundation
> **Branch:** `research/entry-edge-t1-exit-validation`
> **Primary source:** `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt`
> **Source type:** supplied transcript of the Poorsamadi SP2L Strategy video
>
> **Non-negotiable rule:** this ledger records what the source says. It does not turn our interpretation into a source fact. When the transcript does not provide a deterministic numeric definition, the rule remains `UNKNOWN/TBD`.

---

## 1. Source hierarchy

1. **Raw source** — the transcript above is preserved unchanged.
2. **Source ledger** — this document records source-grounded statements and their timestamps.
3. **Codification** — a deterministic implementation may only be written when the source provides enough information, or when a separate explicit research assumption is declared.
4. **Current code** — implementation is evidence of what the machine currently does, not evidence that the source intended it.
5. **Research** — validates/rejects hypotheses about a codified implementation; it does not rewrite the teacher's meaning.

If source and code conflict, the result is `CONFLICT`, not an automatic code change and not a silent reinterpretation.

---

# 2. Strategy definition / philosophy

| ID | Time | Source-grounded statement | Deterministic implication | Status |
|---|---:|---|---|---|
| SRC-001 | 3:44–4:09 | Strategy means knowing why we enter, when to enter, what time of day to trade, what timeframe to trade, where to exit, and why to exit. | A complete strategy includes entry, timing, timeframe and exit logic. | SOURCE-ESTABLISHED |
| SRC-002 | 4:09–4:25 | Strategy also includes what to do when the market goes against the expected direction. | Adverse-move reaction must be part of the plan. | SOURCE-ESTABLISHED |
| SRC-003 | 4:33–4:50 | Entry, stop and target are components of the strategy, but are not the whole strategy. | Do not define Strategy A as entry-only logic. | SOURCE-ESTABLISHED |
| SRC-004 | 4:50–5:28 | The plan should be known before the game/market starts; decisions should not be improvised emotionally during the move. | Rules must be predefined before the outcome is known. | SOURCE-ESTABLISHED |
| SRC-005 | 5:37–6:18 | Strategy and trading system are distinguished. A strategy is an operational plan that is repeatable and evaluable/backtestable. | A rule that cannot be consistently classified/backtested is not yet a complete codified strategy. | SOURCE-ESTABLISHED |
| SRC-006 | 6:18–8:39 | Similar situations should receive the same reaction; materially different actions must not be mixed as one strategy population. | Setup classification and action mapping must be reproducible. | SOURCE-ESTABLISHED |
| SRC-007 | 8:39–9:58 | Strategy is fixed behavior in response to variable market outcomes. | Same setup/action can legitimately produce different outcomes. | SOURCE-ESTABLISHED |
| SRC-008 | 10:22–11:42 | Strategy quality is about the distribution of risk versus gain, not simply consecutive winning trades; changing numerical exits emotionally damages the formula. | Risk/return parameters must be treated as predefined rules in testing. | SOURCE-ESTABLISHED |
| SRC-009 | 11:50–15:58 | Losing/winning sequences cannot be predicted; trader should accept uncertainty and follow the tested strategy. | No rule may depend on predicting the next trade's outcome. | SOURCE-ESTABLISHED |
| SRC-010 | 15:03–15:58 | SET & FORGET is presented as the intended behavioral model after setting a trade/order according to the plan. | Post-entry discretionary interference is not part of the base behavior unless explicitly defined. | SOURCE-ESTABLISHED |

---

# 3. Candle-by-candle price reading

| ID | Time | Source-grounded statement | Deterministic implication | Status |
|---|---:|---|---|---|
| CND-001 | 18:27–18:58 | Price action is described as a chart language; candles are its words and should be read individually. | Candle-level OHLC relationships are primary evidence. | SOURCE-ESTABLISHED |
| CND-002 | 18:58–19:21 | M1, M5 and M15 are explicitly discussed; higher timeframes are described as having a different trading subject. | Timeframe is part of strategy context; M1/M5/M15 are explicitly mentioned in the source. | SOURCE-ESTABLISHED |
| CND-003 | 19:21–20:30 | Consecutive candles can reveal weakness/range or strength; each candle's high, low, open and close and its relation to prior candles matter. | Structural comparisons must use explicit OHLC relationships rather than visual wave descriptions. | SOURCE-ESTABLISHED |
| CND-004 | 20:37–21:04 | A trader should ask whether a close broke a previous level, whether a gap/pressure movement exists, and whether candles are extending. | Breakout, gap and extension are source concepts requiring explicit definitions. | SOURCE-ESTABLISHED / CODIFICATION TBD |
| CND-005 | 27:09–27:42 | A higher high/lower low and candle engulf/close relationships are examples of the chart language. | Structural event definitions should be based on candle relationships. | SOURCE-ESTABLISHED |
| CND-006 | 1:04:32–1:04:59 | The market must still be read candle by candle even after a leg/target concept is identified; the scenario can change from one candle to another. | Future candles cannot be used to retroactively define an earlier state. | SOURCE-ESTABLISHED |
| CND-007 | 1:07:49–1:08:16 | Final emphasis: do not view the market only wave-by-wave; work candle-by-candle and identify cycles and candle counts within them. | Sequence/cycle context must be preserved in any future codification. | SOURCE-ESTABLISHED |

---

# 4. Trend / breakout / spike

| ID | Time | Source-grounded statement | Deterministic implication | Status |
|---|---:|---|---|---|
| SPK-001 | 26:14–26:37 | A spike is described as a sharp movement after a range. | Spike requires a preceding range/context and a sharp directional movement. Exact numeric thresholds are not supplied here. | SOURCE-ESTABLISHED / NUMERIC TBD |
| SPK-002 | 26:37–27:20 | The range can be small at candle level; it does not have to be a long-duration range. | Do not require a large/long range by assumption. | SOURCE-ESTABLISHED |
| SPK-003 | 27:51–28:29 | One way a strong movement can appear is through successive higher lows; in a downtrend attention shifts to lower highs. | Directional structure is part of spike recognition. Exact count requirement is not stated as a universal numeric rule. | SOURCE-ESTABLISHED / NUMERIC TBD |
| SPK-004 | 28:47–29:16 | Strong movements can have overlapping bodies/shadows; overlap affects their strength/type and can distinguish strategy branches. | Candle overlap must not be ignored when classifying movement. | SOURCE-ESTABLISHED / EXACT RULE TBD |
| SPK-005 | 30:48–31:29 | A movement with internal overlap/canal-like behavior may be treated as channel-oriented rather than spike-oriented. A valid breakout is central to the spike-oriented branch. | Spike classification depends on breakout/structure quality, not merely directional movement. | SOURCE-ESTABLISHED |
| SPK-006 | 31:02–31:18 | Breakout is described as a candle closing beyond a level, followed by a next candle/follow-through (FT or key bar) that cannot return into/overlap the prior area. | Breakout has a close-beyond-level event plus a follow-through condition. Exact level/overlap tolerance is TBD. | SOURCE-ESTABLISHED / NUMERIC TBD |
| SPK-007 | 31:43–32:12 | P-GAP is presented as a pressure gap and is distinguished from E-GAP, Common-GAP and morning gap. | Gap subtype matters; all visible gaps must not be treated as identical. | SOURCE-ESTABLISHED / EXACT P-GAP RULE TBD |
| SPK-008 | 32:21–32:44 | A candle closing above the previous high is still a breakout/trend; different breakout/trend types can require different reactions. | Breakout direction and context must be preserved. | SOURCE-ESTABLISHED |
| SPK-009 | 33:37–35:37 | Different candle sequences can represent the same underlying strong-trend concept. The source gives cases where breakout+FT occurs before higher lows, or higher lows precede the gap; these can currently be treated as one strategy branch, though the teacher says they could later be separated. | Do not invent a branch split unless explicitly adopted. Current source teaching groups the described variants for this strategy. | SOURCE-ESTABLISHED |
| SPK-010 | 35:37–36:05 | Three variants of the strong movement are considered, including breakout/FT/P-GAP sequencing and higher-low/gap sequencing. | The canonical spike detector must eventually encode which variants are accepted. Exact formal grammar is TBD. | SOURCE-ESTABLISHED / CODIFICATION TBD |

---

# 5. SP2L / Leg 1 / Leg 2 / Leg 3

| ID | Time | Source-grounded statement | Deterministic implication | Status |
|---|---:|---|---|---|
| 2L-001 | 24:42–25:55 | SP2L is the teacher's naming for “Spike - 2 Leg”; the name is primarily a unique label and should not be treated as proof of novelty. | Name itself carries no trading rule. | SOURCE-ESTABLISHED |
| 2L-002 | 36:15–36:46 | 2Leg is associated with AB=CD, but the teaching is brought down to candle-level rather than a classical chart-only/fibonacci treatment. | Leg relationship must be evaluated from candle-level price action. | SOURCE-ESTABLISHED |
| 2L-003 | 36:59–37:08 | After a spike, expectation is a correction followed by completion of Leg 2, with Leg 2 equal to Leg 1. | Core relationship: expected Leg2 magnitude ≈ Leg1 magnitude. Exact measurement endpoints/tolerance are TBD. | SOURCE-ESTABLISHED / NUMERIC TBD |
| 2L-004 | 37:08–37:46 | After Leg 2, another continuation/Leg 3 may occur; the source explicitly points to another video for the detailed Leg 3 relationship. | Leg 3 exists as a source concept but its detailed canonical rule is NOT contained in this video. | SOURCE-ESTABLISHED / DETAIL TBD |
| 2L-005 | 37:57–38:18 | The sequence is summarized as: directional increase/decrease, correction, then expected next leg equal to the first leg. | This is the semantic nucleus of SP2L. | SOURCE-ESTABLISHED |
| 2L-006 | 38:18–38:53 | A trend with successive higher lows can be treated as the spike stage; when the next candle begins correcting below the first low, an order can be placed. | Correction begins with a source-described breach of the first relevant low/high depending on direction. Exact universal trigger still requires careful source mapping. | SOURCE-ESTABLISHED / CODIFICATION TBD |
| 2L-007 | 39:11–40:22 | An order may be placed before the next candle completes when the spike/breakout/FT/P-GAP context already establishes the opportunity; a limit order can define the entry and known SL distance. | Source permits pre-placed limit entry in at least the demonstrated case. | SOURCE-ESTABLISHED |
| 2L-008 | 40:57–41:10 | Additional confirmation can include a signal bar and key bar; these are examples of extra confirmation, not a universal mandatory numeric rule in this transcript. | Do not promote optional confirmation examples into mandatory rules without source evidence. | SOURCE-ESTABLISHED / MANDATORY STATUS TBD |
| 2L-009 | 45:15–45:39 | After price gets direction, trader attempts to enter in that direction to capture Leg 2; the entry is described as highly optimized. | Directional alignment is core; exact entry optimization rule remains to be extracted from broader source material. | SOURCE-ESTABLISHED |
| 2L-010 | 46:15–46:45 | Three-candle situations followed by a return to the low/high and first pullback are cited as common examples for reaching Leg 2. | First-pullback behavior is an important source pattern, but “three candles” is illustrative here, not yet a universal hard requirement. | SOURCE-ESTABLISHED / NUMERIC TBD |

---

# 6. Entry / limit / 2X

| ID | Time | Source-grounded statement | Deterministic implication | Status |
|---|---:|---|---|---|
| ENT-001 | 38:38–39:26 | When the next candle starts correcting, an order can be placed below the first low (or corresponding opposite-direction level). A limit order can be set in advance. | Entry may be a limit order at a structural correction level in the demonstrated setup. | SOURCE-ESTABLISHED |
| ENT-002 | 39:26–40:07 | The distance from limit entry to SL is known before activation; if a subsequent candle changes the setup and the distance becomes too large, the order can be deleted and a new one placed. In the demonstrated case the teacher keeps the original order because the distance is not sufficiently large. | Source includes adaptive order management based on risk distance, but exact “too large” threshold is not given. | SOURCE-ESTABLISHED / NUMERIC TBD |
| ENT-003 | 40:16–40:22 | First priority is good money management and trading with the trend. | Trend direction and risk management are core constraints. | SOURCE-ESTABLISHED |
| ENT-004 | 41:26–42:17 | A second position (“2X”) can be entered after the first position has moved a defined amount toward target; the second position can have a different effective reward because its entry is better. | 2X is a distinct position/entry action, not merely a label on the original trade. Exact trigger is source-described as a fraction of target in the example, but universal formula must be documented separately. | SOURCE-ESTABLISHED |
| ENT-005 | 41:37–42:17 | In the demonstrated example, when the first trade obtains one unit of reward from its entry, the 2X entry can produce roughly three units of reward from its own entry; with equal dollar risk this creates an asymmetric combined outcome. | 2X is explicitly connected to money management and improved entry location. | SOURCE-ESTABLISHED |
| ENT-006 | 42:17–42:26 | The teacher refers to a separate “2nd position” teaching for detailed money management. | Detailed 2X rules are not fully contained in this video. | SOURCE-ESTABLISHED / DETAIL TBD |
| ENT-007 | 47:42–48:30 | SP2L can be added as a trigger to an existing trading concept (e.g. moving averages, cycles, channels); the teacher demonstrates using the spike trigger at a meaningful location rather than blindly everywhere. | SP2L may function as an entry trigger layered onto context. Context is not optional merely because a spike exists. | SOURCE-ESTABLISHED |

---

# 7. Stop loss / invalidation

| ID | Time | Source-grounded statement | Deterministic implication | Status |
|---|---:|---|---|---|
| SL-001 | 17:30–17:52 | In a demonstrated short, SL is placed above a defined level; if price reaches that level, the trader has a different reaction/scenario. | SL is structural and tied to scenario invalidation. | SOURCE-ESTABLISHED |
| SL-002 | 39:26–39:48 | For the demonstrated buy-limit setup, if price returns to the invalidating level, the scenario is considered cancelled/invalid. | Invalidation is part of setup definition. Exact general formula is direction-dependent and must be explicitly mapped. | SOURCE-ESTABLISHED |
| SL-003 | 1:07:15–1:07:43 | The teacher warns against moving SL farther away merely because the trade is going against the trader; this can transform a planned small risk into a much larger loss. | No discretionary widening of SL in the base strategy. | SOURCE-ESTABLISHED |
| SL-004 | 1:07:43–1:07:49 | Final instruction: remain committed to planned take-profit and stop-loss. | SL/TP adherence is a core behavioral rule. | SOURCE-ESTABLISHED |

---

# 8. TP1 / TP2 / exits / profit management

| ID | Time | Source-grounded statement | Deterministic implication | Status |
|---|---:|---|---|---|
| EXT-001 | 41:37–42:10 | The first and second positions can have different R outcomes because the second position has a better entry. | Each position must be evaluated separately before any combined-account metric. | SOURCE-ESTABLISHED |
| EXT-002 | 42:26–42:47 | TP can be TP1 or TP2. The teacher says he generally uses TP1 for this strategy because the second trade enlarges the total profit; TP2 is described as somewhat large for the strategy because the SL is relatively large. | TP1 is the demonstrated preferred base exit; TP2 is possible but not necessarily the default. | SOURCE-ESTABLISHED |
| EXT-003 | 42:37–42:47 | TP1 is preferred partly because the strategy has a relatively larger SL and therefore TP2 has a lower practical occurrence probability. | Target selection is linked to probability and risk distance. | SOURCE-ESTABLISHED |
| EXT-004 | 59:08–59:42 | In the demonstrated sequence, some positions are closed at the lower target while the last position is left without a fixed TP and reaches approximately R3.5–R4 before management decisions. | The teacher demonstrates discretionary/advanced position management beyond the simplest TP1 rule. This must not be silently merged with the base backtest. | SOURCE-ESTABLISHED / ADVANCED MANAGEMENT |
| EXT-005 | 1:01:30–1:02:16 | For a profitable remaining position, one option is to close half; another is to close all positions. The teacher personally generally closes them because he considers the market to contain further opportunities. | Multiple money-management exit styles exist; the exact default depends on the strategy variant/account objective. | SOURCE-ESTABLISHED / VARIANT TBD |
| EXT-006 | 1:02:31–1:03:32 | The teacher explains exit in relation to whether the larger bearish/bullish scenario is reaching its end and whether another leg can be traded separately. | Exit can be contextual when trading successive legs, but this video does not provide a complete deterministic exit grammar. | SOURCE-ESTABLISHED / DETAIL TBD |
| EXT-007 | 1:04:32–1:05:25 | The market is still read candle by candle; a fast scalp can be exited after a relatively small move and treated as separate from the main SP2L discussion. | Fast scalp is a separate strategy/variant and must not be mixed with base SP2L statistics. | SOURCE-ESTABLISHED |

---

# 9. Risk / money management / probability

| ID | Time | Source-grounded statement | Deterministic implication | Status |
|---|---:|---|---|---|
| RM-001 | 10:22–11:42 | A good strategy is not necessarily one that wins frequently; correct distribution of risk versus gain is central. | Optimize/evaluate expectancy, PF, drawdown and R distribution, not win rate alone. | SOURCE-ESTABLISHED |
| RM-002 | 11:50–12:41 | Consecutive losses can occur and cannot be predicted; abandoning the strategy during a losing sequence can miss later profitable trades. | Backtest must preserve chronological trade sequence and consecutive-loss statistics. | SOURCE-ESTABLISHED |
| RM-003 | 24:29–24:42 | When distance to SL is smaller, the teacher increases position size in the demonstrated example. | Position sizing is risk-distance dependent; exact sizing formula is not fully stated here. | SOURCE-ESTABLISHED / FORMULA TBD |
| RM-004 | 40:16–40:22 | Money management is a first priority. | No setup promotion without a compatible risk model. | SOURCE-ESTABLISHED |
| RM-005 | 53:54–54:29 | When probability of the setup is lower, instead of rejecting it automatically, the teacher demonstrates reducing risk (e.g. 2%→1% or 1%→0.5%) while still taking the directional trigger. | Source permits probability-adjusted risk sizing in at least this advanced context. Exact probability classification and sizing map are TBD. | SOURCE-ESTABLISHED / CODIFICATION TBD |
| RM-006 | 57:14 | A demonstrated setup is described as approximately 4% profit against 2% risk. | Source uses percentage risk/profit examples; this is an example, not a universal fixed target. | SOURCE-ESTABLISHED |
| RM-007 | 1:02:16 | A demonstrated account result is described as roughly 2–3% profit against roughly 0.5–1% risk, with 1% risk described as reasonable. | Illustrative money-management example only; not a canonical fixed risk percentage. | SOURCE-ESTABLISHED / NOT A UNIVERSAL RULE |

---

# 10. Time / sessions / locations / levels

| ID | Time | Source-grounded statement | Deterministic implication | Status |
|---|---:|---|---|---|
| TIME-001 | 18:58–19:12 | M1, M5 and M15 are explicitly used/discussed; higher timeframes are treated differently. | Timeframe is a strategy dimension. | SOURCE-ESTABLISHED |
| TIME-002 | 48:49–49:47 | The teacher excludes the early 5am example for the demonstrated trading routine and says work starts around 7am broker time, with local-time conversion depending on DST. | Trading window is session/time dependent. Exact canonical timezone/session mapping requires source reconciliation. | SOURCE-ESTABLISHED / EXACT WINDOW TBD |
| TIME-003 | 51:47–52:38 | European markets, Frankfurt and London are discussed around their opening; a setup near 9:00–9:01 is used to demonstrate time strategy. London/New York timing is explicitly important. | Session filters are core strategy context. Exact canonical session boundaries require broader source extraction. | SOURCE-ESTABLISHED / EXACT WINDOW TBD |
| TIME-004 | 55:22–55:31 | New York hours are described as another favorable period with many opportunities. | New York session is a preferred trading context in the demonstration. | SOURCE-ESTABLISHED |
| TIME-005 | 43:27–44:19 | Round levels are described as useful levels for trading gold; examples include 3200/3250/3255 and finer 3257.5. The teacher says round levels can be separated every 250 points, or 500, or 1000 depending on trading style. | Round-number levels are a contextual filter. The exact mapping from “points” to XAUUSD price units must be defined from instrument convention before coding. | SOURCE-ESTABLISHED / INSTRUMENT MAPPING TBD |
| TIME-006 | 44:19–44:29 | 250-point separation is described for fast scalpers, 500 for scalpers, and 1000 for swing-oriented trading. | Level spacing can vary by trading style. Do not assume the current project value is canonical without source mapping. | SOURCE-ESTABLISHED |
| TIME-007 | 45:39–46:45 | Important levels are said to create especially good opportunities; the teacher references another video/highlights for the detailed list of important levels. | “Important level” is source-critical but its complete definition is outside this transcript. | SOURCE-ESTABLISHED / DETAIL TBD |
| TIME-008 | 53:16–53:54 | Market cycles and larger-timeframe pullbacks remain relevant even when the entry is executed on a low timeframe. | Low-timeframe execution does not eliminate higher-level context. | SOURCE-ESTABLISHED |

---

# 11. Market quality / context

| ID | Time | Source-grounded statement | Deterministic implication | Status |
|---|---:|---|---|---|
| CTX-001 | 48:09–48:35 | On a channel boundary, do not immediately enter merely on a signal bar/key bar; look for a trend/Leg1/Leg2 behavior and spike/breakout/FT/gap context. | A spike trigger can be a confirmation layer for another context. | SOURCE-ESTABLISHED |
| CTX-002 | 49:13–49:37 | Very wide spikes are discouraged; the teacher says to preferably avoid entering when the spike's width is too large, even if the example later reaches target. | Spike width is a quality filter. Exact threshold is not given. | SOURCE-ESTABLISHED / NUMERIC TBD |
| CTX-003 | 50:09–50:26 | Taking a good early trend opportunity can favor P-GAP rather than E-GAP and may reach targets quickly. | Early trend location and gap type affect quality. | SOURCE-ESTABLISHED |
| CTX-004 | 50:56–51:15 | After several sequential pushes toward a level, the teacher says the setup becomes risky and should be skipped, waiting for a better opportunity. | Repeated extension/late-stage location can invalidate entry quality. Exact count threshold is illustrative, not fully codified. | SOURCE-ESTABLISHED / NUMERIC TBD |
| CTX-005 | 51:25–51:31 | Moving average is described as “equilibrium price” and a place where price can return before a decision. | EMA/MA can be used as contextual equilibrium. Exact canonical period must be sourced rather than inferred. | SOURCE-ESTABLISHED |
| CTX-006 | 54:36–55:02 | Ranging/dirty markets are discouraged for ordinary users; clean markets with clearer directional structure are preferred. | Market-quality filter is part of source philosophy. Exact “clean/dirty” classifier is TBD. | SOURCE-ESTABLISHED / CODIFICATION TBD |
| CTX-007 | 55:50–56:20 | The teacher repeatedly says dirty/choppy candles visibly signal poor conditions; advanced traders may still find some orders there, but ordinary users should trade cleaner conditions. | Base strategy should not silently include discretionary “dirty-market” trades. | SOURCE-ESTABLISHED |
| CTX-008 | 56:20–56:36 | A clean lower-high sequence after a structural break is presented as a clear sell opportunity with a clean R1. | Clear directional structure + appropriate level/context is preferred. | SOURCE-ESTABLISHED |

---

# 12. FVG / P-GAP / E-GAP

| ID | Time | Source-grounded statement | Deterministic implication | Status |
|---|---:|---|---|---|
| GAP-001 | 31:43–32:12 | P-GAP, E-GAP, Common-GAP and morning gap are distinct concepts; location of formation matters. | A generic “gap exists” flag is insufficient. | SOURCE-ESTABLISHED |
| GAP-002 | 34:14–35:37 | P-GAP is used as a simple visual marker for breakout/pressure behavior; different sequence variants can contain it. | P-GAP can be used as a breakout quality marker. | SOURCE-ESTABLISHED |
| GAP-003 | 49:47–50:20 | The teacher contrasts P-GAP and E-GAP and says early-trend opportunities are associated with P-GAP. | Gap type is a timing/location quality dimension. | SOURCE-ESTABLISHED |
| GAP-004 | 58:04–58:22 | A breakout with a gap is used as a bearish trigger with an SL at a structural level; TP1 and 2X are then discussed. | Gap + breakout can form an entry trigger. Exact FVG/P-GAP geometry must be sourced separately. | SOURCE-ESTABLISHED / GEOMETRY TBD |

---

# 13. Advanced / secondary strategy concepts explicitly mentioned

These are **not** to be silently promoted into the base Strategy A implementation from this video alone:

- Trendline-based entries: 21:15–21:50.
- MTR: 7:27–8:04.
- Channels: 30:41–30:53 and 48:01–48:35.
- Cycles: 46:58–47:13 and 53:32–53:54.
- Fast scalp: 1:04:59–1:05:25.
- Leg 3: 37:08–37:46.
- Second-position / 2X detailed management: 42:17–42:26.
- Important levels: 45:39–46:45.
- Time strategy / time analysis: 51:47–52:50.

These references prove the concepts exist in the teacher's broader framework, but they do not provide enough information in this single transcript to claim a complete deterministic implementation.

---

# 14. Explicit anti-bias / anti-overfitting instructions from the source

| ID | Time | Source-grounded statement | Project rule |
|---|---:|---|---|
| BIAS-001 | 42:48–43:11 | Do not trust the teacher or any educator merely because they said something; backtest it. At least 50 trades, preferably 100, are suggested. | No source claim becomes an economic rule without empirical testing. |
| BIAS-002 | 52:50–53:07 | Do not jump onto charts merely because of the teacher's words; inspect and test what happens. | Research-first policy is directly aligned with the source. |
| BIAS-003 | 58:22–58:32 | Do not develop confirmation bias; look for failures as well as confirming examples. | Holdout/falsification work is mandatory. |
| BIAS-004 | 58:32–58:40 | The teacher explicitly acknowledges that the system has losses. | A valid strategy is not expected to win every trade. |
| BIAS-005 | 1:07:15–1:07:43 | Do not move stops farther to avoid taking the planned loss. | No hindsight loss expansion. |

---

# 15. What this source DOES establish for Strategy A

1. **Strategy is a complete operational plan**, not just an entry pattern.
2. **Repeatability is mandatory.** Equivalent situations should produce equivalent actions.
3. **Outcomes are uncertain.** Fixed behavior must be evaluated across variable results.
4. **Risk/reward and money management are core parts of the strategy.**
5. **Candle-by-candle reading is fundamental.**
6. **M1/M5/M15 are explicitly relevant**, with the teacher demonstrating M1 heavily.
7. **A spike follows a range/context and is a sharp directional movement.**
8. **Breakout + follow-through is central to identifying the strong movement.**
9. **P-GAP and E-GAP are distinct and location matters.**
10. **SP2L means Spike → 2 Leg; the core expectation is a correction followed by Leg 2 approximately matching Leg 1.**
11. **Entry can be a pre-placed limit order** in the demonstrated setup.
12. **Trading with the trend is explicitly preferred.**
13. **2X is a distinct secondary position concept** tied to money management and improved entry location.
14. **TP1 is the teacher's stated usual target for this strategy**, while TP2 exists but is described as less suitable in the demonstrated context.
15. **Important levels, sessions, market cleanliness, and context matter.**
16. **The teacher explicitly requires backtesting and warns against confirmation bias.**
17. **Stop/target discipline is mandatory.**

---

# 16. What this source does NOT establish numerically

The following must remain `UNKNOWN/TBD` until the relevant source material provides the missing definition or a clearly labeled project assumption is approved:

- exact minimum/maximum spike size;
- exact spike candle count;
- exact preceding-range definition;
- exact overlap tolerance for breakout/FT;
- exact P-GAP geometry;
- exact E-GAP geometry;
- exact Leg 1 start/end prices;
- exact correction start/end and depth;
- exact Leg 2 equality tolerance;
- exact trigger formula;
- exact limit-entry price formula for every variant;
- exact SL placement formula for every direction/variant;
- exact TP1 formula;
- exact TP2 formula;
- exact 2X trigger formula across all cases;
- exact position-size formula;
- exact “spike too wide” threshold;
- exact “dirty market” classifier;
- exact session boundaries/timezone conversion;
- exact important-level taxonomy;
- exact round-level point conversion for the project's XAUUSD feed;
- exact rules for Leg 3;
- exact rules for advanced fast-scalp branch;
- exact rules for channel/cycle/context branches.

**These are missing definitions, not invitations to guess.**

---

# 17. Required next source excavation

This video explicitly references other material for missing definitions. Before declaring Strategy A semantically complete, retrieve and extract the relevant source for:

1. **Weekly Report #19** — explicitly referenced for Leg 3 and important levels.
2. **Gap-specific teaching** — for P-GAP/E-GAP/Common-GAP/morning-gap exact definitions.
3. **2nd Position / 2X highlight** — for complete second-position money management.
4. **Time Strategy / Time Analysis** — for London/New York timing rules.
5. **Fast Scalp teaching** — if fast-scalp behavior is intended as a Strategy A branch.
6. **Cycle / candle-count teaching** — for the source's cycle and counting methodology.
7. Any original teaching that defines exact spike dimensions, correction depth, entry trigger, SL and TP formulas.

Only after these are extracted should the source-grounded semantic ledger be considered complete.

---

# 18. Implementation audit rule

For every current Strategy A rule, the audit must answer:

> **Where exactly did this rule come from?**

Allowed answers:

- `SOURCE` — explicitly stated by the teacher;
- `SOURCE-DERIVED` — directly and mechanically implied by an explicit source statement, with the derivation documented;
- `RESEARCH-ASSUMPTION` — an experiment-only operationalization, clearly labeled and never presented as the teacher's rule;
- `CURRENT-IMPLEMENTATION` — what code currently does, without claiming semantic authority;
- `UNKNOWN/TBD` — insufficient source information.

Forbidden answer:

- “It seemed logical.”
- “We thought this was better.”
- “The backtest liked it.”
- “The code already did it.”

---

# 19. Bottom line

The source gives us a **semantic skeleton**, and it is substantially richer than the current narrow deterministic DELAY1 reconstruction.

The correct next action is **not** to immediately rewrite Strategy A from this one video. The correct action is to preserve this ledger, identify every source/code conflict, obtain the referenced source material for the unresolved branches, and only then convert source-established rules into deterministic code and validate them chronologically.
