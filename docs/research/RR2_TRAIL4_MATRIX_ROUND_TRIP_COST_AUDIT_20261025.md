# RR2/TRAIL4 Mixed Trailing Matrix — Round-Trip Cost Adjustment

Date: 2026-10-25
Status: research-only post-processing; does not alter the live runner or gross source artifacts.

## Cost assumption

The user-confirmed minimum cost is USD 0.05 total for one complete entry-to-exit trade at 0.01 lots. It is charged exactly once per completed decisive trade. This is a fixed round-trip cost assumption, not a per-side charge.

With XAUUSD contract size 100 and volume 0.01 lots:

- Initial dollar risk = risk_price × 100 × 0.01
- Cost in R = 0.05 / initial_dollar_risk
- Net R = gross realized R − cost in R

This adjustment does not infer spread and commission separately. It applies the confirmed minimum combined cost of USD 0.05 once to each completed decisive trade. Ambiguous trades and trades without a realized outcome remain excluded from decisive net metrics and are not assigned a guessed outcome. Their source rows remain present.

## Run against the existing matrix

From the isolated research worktree, use the exact generated source paths. Do not rerun MT5 or overwrite the original gross outputs:

    $ErrorActionPreference = "Stop"
    $Python = "D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe"
    $Base = ".\artifacts\v3\SP2L_V3_TRAILING_MATRIX_20261025T072931Z"

    & $Python -m py_compile .\scripts\analyze_sp2l_v3_trailing_matrix_costs.py
    if ($LASTEXITCODE -ne 0) { throw "Cost-audit compile failed" }

    & $Python -m pytest .\tests\test_sp2l_v3_trailing_matrix_costs.py -q
    if ($LASTEXITCODE -ne 0) { throw "Cost-audit tests failed" }

    & $Python .\scripts\analyze_sp2l_v3_trailing_matrix_costs.py --matrix-csv "\${Base}_matrix.csv" --trades-csv "\${Base}_trades.csv" --cost-usd 0.05 --volume 0.01 --contract-size 100
    if ($LASTEXITCODE -ne 0) { throw "Cost-adjusted audit failed" }

The analyzer writes separate _COST_ADJUSTED matrix/trades/JSON/snapshot files and does not modify the source CSV/JSON/snapshot. Compare all 26 scenarios using net R, net PF, net win rate, net drawdown, net consecutive losses, break-even count, and total modeled costs.

## Limitations

- Gross source results are retained for auditability.
- Fixed USD 0.05 per completed trade is only a minimum-cost sensitivity analysis; actual spread can vary with time and execution.
- Slippage, swap, and variable commissions are not modeled separately.
- The same candidate trades are independently simulated in each scenario; overlapping trades are not constrained by capital or execution capacity. Trade-level drawdown is not account-level drawdown.
- This post-processing does not establish canonical Strategy A geometry or authorize production execution.
