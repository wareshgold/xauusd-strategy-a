SP2L V3 MT5 Actual Trailing Matrix — 2026-10-03

Research-only counterfactual matrix. It does not place or modify MT5 orders.

Pull:
cd "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a"
git checkout research/sp2l-strategy-a-v3-trailing10-20261001
git pull --ff-only

Run:
& ".\\.venv\\Scripts\\python.exe" ".\\scripts\\run_sp2l_v3_mt5_actual_trailing_matrix.py" --mt5-path "C:\\Program Files\\Otet Group MT5 Terminal\\terminal64.exe" --symbol "XAUUSD.ecn" --magic 26092201 --start "2026-10-01T10:37:00+00:00"

The script expects exactly 36 completed positions and stops before producing a matrix if the count differs. Do not use --allow-count-diff until the population has been inspected.

Outputs: artifacts/v3_matrix/SP2L_TRAILING_2X_MATRIX_<timestamp>.csv, _TRADES.csv, .json and _SNAPSHOT.md.

120 variants = 6 activation values × 10 trailing distances × 2X ON/OFF.

Data source: MT5 deal history for magic 26092201 plus M1 directly from the connected MT5 terminal.

Critical V3 note: the frozen V3 config currently declares XAU_PIP_SIZE_PRICE = 0.1. The matrix therefore uses that exact V3 definition; Trail 4 means 0.4 price units. A 0.01 convention must be source/config resolved separately and is not silently substituted.

Interpretation: research only. No row becomes canonical because it performs best on these 36 trades; candidates require fresh forward validation.