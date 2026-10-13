# SP2L Entry Geometry Audit — 2026-10-13

## Purpose

This is a research-only measurement of the V3 RR2/Trail4 candidate entry geometry against the source note that describes BUY retrace to the previous candle Low and SELL retrace to the previous candle High.

It does not decide which candle or fill interpretation is canonical. It does not simulate fills, score outcomes, optimize parameters, or change the Forward Runner.

## Evidence already observed

For the shared M1 dataset from 2026-07-13 through 2026-10-13:

- Bars: 90,869
- Bars SHA-256: `28596964f2b9d6136fb24c0773fa983145b297fb40c2dc46f4a497ca803f5a38`
- Candidates: 1,521
- BUY candidates: 750; all 750 entries equal the current bar Low; none equal the previous bar Low.
- SELL candidates: 771; all 771 entries equal the current bar High; none equal the previous bar High.

Those counts establish what the current research implementation does. They do not establish a canonical source rule.

## Audit measures

For each candidate, the script records:

- current-variant entry price and current bar extreme;
- previous candle Low (BUY) or High (SELL);
- signed and absolute price difference between the variant entry and previous level;
- whether the previous level falls within the entry bar's OHLC range;
- whether the bar extends beyond that previous level, and whether the level is outside the bar's range.

The range tests are OHLC diagnostics only. They do not establish the order in which the price levels were visited or prove that a pending order would have filled. Gap-through cases are explicitly surfaced rather than assumed filled.

## Run locally

From the repository root in the intended research workspace:

```powershell
python .\scripts\sp2l_v3_entry_geometry_audit.py `
  --mt5-path "C:\Program Files\Otet Group MT5 Terminal\terminal64.exe" `
  --symbol "XAUUSD.ecn" `
  --start "2026-07-13T00:00:00+00:00" `
  --end "2026-10-13T00:00:00+00:00" `
  --config-module "sp2l_v3_rr2_trail4_config"
```

The output is a timestamped JSON report and candidate-level CSV under `artifacts/v3/`. Verify the reported bar SHA-256 matches the evidence above before comparing counts. Keep generated outputs uncommitted unless they are deliberately being added as an audit artifact.

## Interpretation constraints

- The existing current-candle extreme entry is a research variant, not canonical Strategy A.
- The source meaning outranks any performance difference.
- The exact candle identity, touch versus penetration versus close, intrabar order, and entry/fill semantics remain unresolved.
- Do not select a geometry because it improves net R, win rate, profit factor, or trailing results.
- No production logic, config, Fresh Holdout, or Forward Runner changes are authorized by this audit.
