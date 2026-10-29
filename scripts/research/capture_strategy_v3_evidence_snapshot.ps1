# Read-only Strategy V3 evidence snapshot. Does not stop processes, edit runtime, or overwrite files.
$ErrorActionPreference = "Stop"
$repoRoot = (Get-Location).Path
$expectedRunner = "scripts\\run_sp2l_v3_xauusd_forward_test.py"
$events = Join-Path $repoRoot "artifacts\\forward-test\\SP2L_V3_XAUUSD_RR2_TRAIL4_FORWARD_EVENTS.jsonl"
$state = Join-Path $repoRoot "runtime\\sp2l_v3_xauusd_rr2_trail4_forward_state.json"
$lock = Join-Path $repoRoot "runtime\\sp2l_multi_symbol_forward_runner.lock"
$dashboardPort = 8790
$v3DashboardPort = 8792
$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssZ")
$outDir = Join-Path $repoRoot "artifacts\\v3\\winner-snapshots"
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$outPath = Join-Path $outDir "STRATEGY_V3_EVIDENCE_$stamp.json"
if (Test-Path $outPath) { throw "Refusing to overwrite existing snapshot: $outPath" }

function Get-FileEvidence([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    return [ordered]@{ exists = $false; path = $Path }
  }
  $item = Get-Item -LiteralPath $Path
  $hash = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
  return [ordered]@{
    exists = $true
    path = $Path
    bytes = $item.Length
    last_write_time_utc = $item.LastWriteTimeUtc.ToString("o")
    sha256 = $hash
  }
}
$gitHead = (& git -C $repoRoot rev-parse HEAD 2>$null | Select-Object -First 1)
$gitBranch = (& git -C $repoRoot branch --show-current 2>$null | Select-Object -First 1)
$runnerMatches = @(Get-CimInstance Win32_Process | Where-Object {
  $_.CommandLine -and $_.CommandLine.Contains("run_sp2l_v3_xauusd_forward_test.py")
} | ForEach-Object {
  [ordered]@{
    process_id = $_.ProcessId
    parent_process_id = $_.ParentProcessId
    executable_name = [IO.Path]::GetFileName([string]$_.ExecutablePath)
  }
})
$dashboardListeners = @()
foreach ($port in @($dashboardPort, $v3DashboardPort)) {
  try {
    $dashboardListeners += @(Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction Stop | ForEach-Object {
      [ordered]@{ port = $port; owning_process_id = $_.OwningProcess }
    })
  } catch {}
}
$lockPid = $null
if (Test-Path -LiteralPath $lock -PathType Leaf) {
  try { $lockPid = [int](Get-Content -LiteralPath $lock -Raw).Trim() } catch {}
}
$snapshot = [ordered]@{
  schema = "sp2l.strategy_v3.evidence_snapshot.v1"
  captured_at_utc = [DateTime]::UtcNow.ToString("o")
  label = "Strategy Version 3 — RR2/TRAIL4 Pending Limit"
  status = "OPERATIONAL_SELECTION_RESEARCH_ONLY"
  canonical = $false
  statistically_proven_winner = $false
  production_approved = $false
  source = [ordered]@{ git_head = $gitHead; git_branch = $gitBranch; runner_path = $expectedRunner }
  runtime = [ordered]@{
    runner_lock_pid = $lockPid
    runner_process_matches = $runnerMatches
    process_count_is_not_duplicate_proof = $true
    dashboards_listeners = $dashboardListeners
    generic_events = Get-FileEvidence (Join-Path $repoRoot "artifacts\\forward-test\\SP2L_MULTI_SYMBOL_FORWARD_EVENTS.jsonl")
    v3_events = Get-FileEvidence $events
    v3_state = Get-FileEvidence $state
  }
  privacy = [ordered]@{
    account_login_omitted = $true
    command_lines_omitted = $true
    environment_values_and_secrets_omitted = $true
  }
  note = "Read-only snapshot. Hashes identify files at capture time; process presence does not prove health. Dashboard listeners are observations only."
}
$json = $snapshot | ConvertTo-Json -Depth 8
[IO.File]::WriteAllText($outPath, $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
$sha = (Get-FileHash -LiteralPath $outPath -Algorithm SHA256).Hash
Write-Output "SNAPSHOT_PATH=$outPath"
Write-Output "SNAPSHOT_SHA256=$sha"
Write-Output $json
