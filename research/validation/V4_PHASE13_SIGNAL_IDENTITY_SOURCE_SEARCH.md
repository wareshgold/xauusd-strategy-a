# V4 Phase 13 — Signal Identity Source Evidence Search

**TEST_ID:** `SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z`  
**Branch/HEAD:** `research/strategy-v4-xauusd-20261028` / `fb14ca20`  
**Status:** `SIGNAL_IDENTITY_NOT_ESTABLISHED / BLOCKED / NOT_PROVEN`  
**Decision:** **SOURCE EVIDENCE UNAVAILABLE**

## Scope of search (verifiable)
Searched in the local repository:
- Docs: `docs/strategy-a.md`, `docs/LIVE_MT5_TELEGRAM_GATEWAY.md`, `docs/research/*.md` (including batch resolutions 35/36/37/38/40, live infra/telegram docs, test failure fixes)
- Research: `research/source_audit/*`, `research/design/V4_DESIGN_FREEZE.md`, `research/source_audit/V4_SOURCE_RULE_REGISTER.csv`, `research/validation/V4_*SIGNAL_IDENTITY*`, `research/manifests/original_history_snapshot_20261028_085035/*`
- Code/config: `research/source_audit/observed_disk/scripts/*`, `research/backtests/SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z_trades.csv`, `research/backtests/V4_BACKTEST_MATRIX.csv`
- Git history: full log across all refs (`git log --oneline --all`)

## Findings
- **Operational identity exists**: Live runner constructs `signal_id` as `"<SYMBOL>:<trigger_time>:<DIRECTION>"` (epoch seconds). Duplicate protection uses it as an index key. Docs explicitly state: *"`signal_id` remains only an index key."* and note past behavior allowed matching by `signal_id` even if `candidate.trigger_time` disagreed (fixed). (`docs/research/SP2L_TEST_FAILURE_FIXES_20260926.md:19,25`)
- **No source definition found**: No document in repo defines a canonical signal identity/numbering scheme assigned by the original author/source. Strategy docs describe structure/concepts (spike/legs/P-Gap/TP1) but not a canonical signal ID. Design freeze does not define source-authenticated identity. Source rule register has no rule for signal identity.
- **No source-assigned IDs in data**: Trade CSV has `signal_time` and `direction` but no source-provided immutable signal ID field. Prior audits (Phase 4/6) concluded no source-authenticated immutable identity key exists; match counts are key-dependent.

## Evidence decision
**C. SOURCE EVIDENCE UNAVAILABLE** — No verifiable primary-source definition or mapping of source-assigned canonical signal IDs exists in the repository.

## Exact missing evidence (minimum acquisition request)
To resolve this blocker, obtain from the original author/source:
1. **Canonical signal list** for the analyzed periods (July/August/September 2026) with a stable, immutable source-assigned `signal_id` for each signal occurrence (independent of implementation).
2. **Identity definition** stating how signals are numbered/identified by the source (uniqueness, duplicate/repeated triggers, timestamp precision/timezone, what constitutes the same signal).
3. **Mapping** linking source-assigned IDs to concrete bar/time/direction/context sufficient to map to the datasets used (or provide the original signal list in a machine-readable form).
4. **Provenance** (original file/location/commit or signed source document) and content hash of the primary source.

## Recommendation
- Keep verdict `SIGNAL_IDENTITY_NOT_ESTABLISHED / BLOCKED / NOT_PROVEN`.
- Do **not** infer canonical identity from `symbol:trigger_time:direction` or from matching rates/outcomes.
- Treat paired comparisons as key-dependent heuristics only. All match/unmatch counts must remain labeled by key definition and object type.
- If authoritative source IDs cannot be obtained, this remains a permanent limitation for identity-based claims.
