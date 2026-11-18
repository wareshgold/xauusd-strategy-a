# V3 36-position Tick + Broker History Evidence Acquisition

**Status:** Research-only acquisition utility; no trading actions and no runner changes.

## Provenance and scope

The original V3 RR2/TRAIL4 forward event stream records:
- Account login: `812930`
- Server: `OtetGroup-MT5`
- Symbol: `XAUUSD.ecn`
- Runner start: 2026-10-01

The M1 intrabar audit covers 2026-10-01T01:00:00Z through 2026-10-05T15:01:00Z. This acquisition requests the wider half-open interval **[2026-10-01T00:00:00Z, 2026-10-06T00:00:00Z)** so the first and last observed windows are not clipped.

The script refuses to write any files unless MT5 reports the exact account login and server above. This is specifically intended to prevent collecting from a different terminal/account. It also refuses to overwrite existing evidence files.

## What it collects

1. `COPY_TICKS_ALL` for `XAUUSD.ecn`, retaining millisecond time, Bid, Ask, Last, Volume, Volume Real, and flags.
2. MT5 history orders for the interval and symbol.
3. MT5 history deals for the interval and symbol.
4. A manifest with hashes, coverage counts, terminal/account identity, and a current-time symbol specification snapshot.

The current stops/freeze levels are explicitly marked as a present-time snapshot, not historical broker settings. Historical order/deal history is not guaranteed to contain SLTP modification request/response acknowledgements. The original local forward event JSONL and any terminal/broker logs are still required for those acknowledgements.

## Run on the Factory PC

Use the existing project venv and the exact Otet terminal installation. Ensure that the intended MT5 terminal is already logged in to account 812930 on OtetGroup-MT5. If the account/server check fails, stop; do not change terminals or credentials inside this procedure.

```powershell
$Base = "D:\Mirzaei\Private\1\xauusd-strategy-a"
$Repo = "D:\Mirzaei\Private\1\_sp2l_v3_36_tick_broker_evidence_20261118"
$Python = "D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe"
$Terminal = "C:\Program Files\Otet Group MT5 Terminal\terminal64.exe"
$Branch = "research/v3-36-tick-broker-evidence-acquisition-20261118"

if (!(Test-Path $Base)) { throw "Base repo missing: $Base" }
if (!(Test-Path $Python)) { throw "Python venv missing: $Python" }
if (!(Test-Path $Terminal)) { throw "MT5 terminal missing: $Terminal" }

git -C $Base fetch origin $Branch
if ($LASTEXITCODE -ne 0) { throw "git fetch failed" }

if (!(Test-Path $Repo)) {
    git -C $Base worktree add $Repo "origin/$Branch"
    if ($LASTEXITCODE -ne 0) { throw "worktree add failed" }
}

$Out = Join-Path $Repo "data\raw\v3_36_intrabar_evidence"
& $Python (Join-Path $Repo "scripts\acquire_v3_36_tick_broker_evidence.py") `
  --start "2026-10-01T00:00:00Z" `
  --end "2026-10-06T00:00:00Z" `
  --symbol "XAUUSD.ecn" `
  --terminal-path $Terminal `
  --expected-login 812930 `
  --expected-server "OtetGroup-MT5" `
  --output-dir $Out

$Exit = $LASTEXITCODE
if ($Exit -ne 0) { throw "Evidence acquisition failed with exit code $Exit" }

$Manifest = Join-Path $Out "MT5_EVIDENCE_MANIFEST_20261001_20261006.json"
$Summary = Get-Content $Manifest -Raw | ConvertFrom-Json
$Summary | Select-Object status,account_login,account_server,tick_count,valid_non_crossed_bidask_count,history_orders_count_symbol,history_deals_count_symbol | Format-List | Out-String | Set-Clipboard
"ACQUISITION_OK — concise manifest summary copied to clipboard."
```

## Expected local outputs

`data/raw/v3_36_intrabar_evidence/` (Git-ignored/local evidence):
- `XAUUSD_ECN_TICKS_20261001_20261006.csv.gz`
- `MT5_HISTORY_ORDERS_20261001_20261006.json`
- `MT5_HISTORY_DEALS_20261001_20261006.json`
- `MT5_EVIDENCE_MANIFEST_20261001_20261006.json`

Do not commit raw ticks automatically. Preserve the files and manifest unchanged; share the manifest first, then the compressed ticks and history JSON files through the project upload flow.

## Interpretation boundaries

- A non-empty tick file is not proof of complete broker tick coverage. Review daily counts, first/last tick, missing/crossed Bid/Ask counts, duplicate and out-of-order millisecond timestamps, and gaps.
- Tick chronology can establish the order of recorded quote updates, but does not alone select canonical fill semantics.
- Deal records establish actual executed deals; order history establishes broker-retained order records. Neither necessarily exposes every SLTP modification attempt.
- No P/L, R, win rate, PF, parameter ranking, 2X fill, or canonical strategy rule is calculated here.
- If the expected account/server does not match, acquisition stops before creating evidence files.
