# V4 Phase 14 — Direct Primary-Source Verification

**TEST_ID:** `SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z`  
**Branch/HEAD:** `research/strategy-v4-xauusd-20261028` / `f85d344e`  
**Status:** `SIGNAL_IDENTITY_NOT_ESTABLISHED / BLOCKED / NOT_PROVEN`  
**Decision:** **SOURCE EVIDENCE UNAVAILABLE (C)**

## Primary source inspected
- Repository: `AlirezaSadabadi/PythonTraderBot` (local copy: `D:/Mirzaei/Private/1/pythontrader/PythonTraderBot`)
- Git HEAD (local copy): `cbe6650` (branch/history as present)
- Key files inspected:
  - `code/SP2L/SP2L_Bot.py` (v2.0)
  - `code/SP2L/SP2L_Advanced_Bot.py` (v4.0)
  - `code/SP2L/SP2L2_Advanced_Backtest.ipynb` (advanced backtest)
  - `code/SP2L/SP2L2_Advanced_Optimized_BackTest_VWAP_ATR_ADX_NewEngine.ipynb` (optimized)
  - `code/SP2L/Meta.py`, `code/SP2L/TelegramBot.py`
  - `README.md`
  - CSV outputs in repo (`code/matrix_results.csv`, etc.)

Related docs in this repo: `docs/research/SP2L_EXTERNAL_IMPLEMENTATION_AUDIT_20260927.md`, `docs/research/SP2L_BATCH38_AUTHOR_IMPLEMENTATION_CROSSWALK_2026-09-17.md`

## What was searched for
- Explicit author/source definition of signal identity
- Source-assigned signal ID, sequence number, or canonical tuple
- Rules for uniqueness/duplicates/timestamp precision/timezone
- Mapping between original source signals and trade rows

## Findings
- **No source-assigned signal IDs found.** In the Advanced Backtest, signals are detected from DataFrame conditions and trades are appended with `setup_id` set to the loop index `i` (e.g. `active_setup["setup_id"] = i`, `leg["setup_id"] = i`). This is a generated index, not a source-assigned identity.
- **Operational identity is index-based.** The author implementation uses fixed candle indexing (`-4/-3/-2/-1`), generates setup/trade entries via counters/indices, and has no canonical "signal_id" field assigned by the original source material.
- **Our own operational codebase** also constructs `signal_id` as `symbol:trigger_time:direction` (epoch seconds) as an index/key for duplicate protection and explicitly documents it as "only an index key" (see Phase 12). This is implementation-derived.
- **No mapping found.** No CSV/JSON in the original repo contains source-assigned signal IDs linking to trade rows with a canonical identity scheme.

## Evidence decision
**C. SOURCE EVIDENCE UNAVAILABLE** — No verifiable primary-source definition or mapping of source-assigned canonical signal IDs exists in the inspected author repository or related docs.

## Conclusion
The original author implementation does not provide source-authenticated signal identity. Identity used in practice (row/index, or `symbol:trigger_time:direction`) are deterministic implementation-derived keys. As established in prior phases, paired matching is key-dependent and cannot be treated as proof of source-identical signals.

## Minimum evidence needed to resolve (unchanged)
1. Canonical signal list with immutable source-assigned `signal_id` for analyzed periods (independent of implementation)
2. Explicit identity definition (uniqueness, duplicates/repeats, timestamp precision/timezone)
3. Mapping from source-assigned IDs to signals/trades in the datasets used
4. Provenance (original file/location/commit or signed document) with content hash

## Recommendation
- Keep `SIGNAL_IDENTITY_NOT_ESTABLISHED / BLOCKED / NOT_PROVEN`
- Do not infer canonical identity from `setup_id`/index or `symbol:trigger_time:direction` or matching rates/outcomes
- Treat paired comparisons as key-dependent heuristics only; label by key definition and object type
- No changes to SP2L geometry/P-Gap/AB=CD/entry/fill/exit rules or datasets
