#requires -Version 5.1
<#
Safely starts the SP2L V3.1 XAUUSD research forward runner with an
operator-pinned broker server UTC offset.

This launcher refuses to start a second copy. It does not stop or modify
an already-running runner. The offset must be supplied explicitly.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateRange(-12, 14)]
    [int]$ServerOffsetHours,

    [string]$PythonExe = 'D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe'
)

$ErrorActionPreference = 'Stop'
$scriptsRoot = $PSScriptRoot
$runnerRoot = Split-Path -Parent $scriptsRoot
$runnerScript = Join-Path $scriptsRoot 'run_sp2l_v3_1_xauusd_forward_test.py'

if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
    throw "Python executable not found: $PythonExe"
}
if (-not (Test-Path -LiteralPath $runnerScript -PathType Leaf)) {
    throw "Runner script not found: $runnerScript"
}

# Refuse duplicate starts; this intentionally does not stop an existing process.
$existing = @(Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -and
    $_.CommandLine.IndexOf($runnerScript, [StringComparison]::OrdinalIgnoreCase) -ge 0
})
if ($existing.Count -gt 0) {
    $ids = ($existing | ForEach-Object { [string]$_.ProcessId }) -join ','
    throw "Runner already appears active (PID(s): $ids). No process was changed."
}

$logDir = Join-Path $runnerRoot 'artifacts\forward-test\restart-logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$stdout = Join-Path $logDir "runner_$stamp.log"
$stderr = Join-Path $logDir "runner_$stamp.err"

$envName = 'SP2L_PENDING_SERVER_OFFSET_HOURS'
$previousValue = [Environment]::GetEnvironmentVariable($envName, 'Process')

try {
    # Start-Process inherits this process environment; spawned Python workers
    # inherit it as well. The value is explicit and validated, never guessed.
    [Environment]::SetEnvironmentVariable($envName, [string]$ServerOffsetHours, 'Process')
    $process = Start-Process -FilePath $PythonExe -ArgumentList @('-u', ('"{0}"' -f $runnerScript)) -WorkingDirectory $scriptsRoot -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
}
finally {
    [Environment]::SetEnvironmentVariable($envName, $previousValue, 'Process')
}

$result = @(
    "START_REQUESTED=True"
    "PID=$($process.Id)"
    "SERVER_OFFSET_HOURS=$ServerOffsetHours"
    "STDOUT=$stdout"
    "STDERR=$stderr"
)
$result -join [Environment]::NewLine | Set-Clipboard
Write-Host 'Runner launch details copied to clipboard.'
$result
