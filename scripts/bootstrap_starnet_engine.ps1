param(
    [string]$Target = "vendor/starnet-engine",
    [string]$Commit = "e0a36dcd31787248b877aea01a6e53741012bc46"
)

$ErrorActionPreference = "Stop"

if (Test-Path (Join-Path $Target ".git")) {
    Write-Host "StarNet engine already present: $Target"
    Push-Location $Target
    try { git fetch --depth 1 origin $Commit; git checkout --detach $Commit }
    finally { Pop-Location }
    exit 0
}

New-Item -ItemType Directory -Force -Path (Split-Path $Target -Parent) | Out-Null
git clone --filter=blob:none --no-checkout https://github.com/androoAGI/starnet.git $Target
Push-Location $Target
try {
    git fetch --depth 1 origin $Commit
    git checkout --detach $Commit
} finally {
    Pop-Location
}

Write-Host "StarNet engine pinned to $Commit"
Write-Host "SP2L owns the adapter/world contract; upstream artwork/branding is not reused as canonical identity."
