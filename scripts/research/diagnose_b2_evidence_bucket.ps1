#requires -Version 5.1
<#
.SYNOPSIS
  Read-only diagnostics for the SP2L Backblaze B2 evidence bucket.

.DESCRIPTION
  Authenticates with a locally-entered Master Application Key, inspects the
  v4 authorization capability envelope, and reads one known bucket.
  This script does NOT create/delete keys, upload files, or modify buckets.

.SECURITY
  Never send the Master Application Key secret, authorization token, or this
  script's terminal session containing secrets to anyone.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$BucketId = '0bd958e97ddd990eae1f0a1c'
$ExpectedBucketName = 'sp2l-factory-evidence'

function Get-B2ErrorSummary {
    param([Parameter(Mandatory = $true)][System.Management.Automation.ErrorRecord]$ErrorRecord)

    $exception = $ErrorRecord.Exception
    $response = $exception.Response

    if ($null -eq $response) {
        $status = $null
        if ($exception -is [System.Net.WebException]) { $status = [string]$exception.Status }
        return "No HTTP response. Transport status: $status. Error type: $($exception.GetType().FullName)."
    }

    $httpStatus = $null
    try { $httpStatus = [int]$response.StatusCode } catch {}

    $responseText = $null
    try {
        if ($response -is [System.Net.HttpWebResponse]) {
            $stream = $response.GetResponseStream()
            if ($null -ne $stream) {
                $reader = New-Object System.IO.StreamReader($stream)
                try { $responseText = $reader.ReadToEnd() }
                finally { $reader.Dispose() }
            }
        }
        elseif ($null -ne $response.Content) {
            $responseText = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
        }
    } catch {}

    if (-not [string]::IsNullOrWhiteSpace($responseText)) {
        try {
            $apiError = $responseText | ConvertFrom-Json
            $code = [string]$apiError.code
            $message = [string]$apiError.message
            if ($code -or $message) { return "HTTP $httpStatus; B2 code='$code'; message='$message'." }
        } catch {}
    }

    return "HTTP $httpStatus. Response body was unavailable or not a B2 error document."
}

function Invoke-B2JsonRequest {
    param(
        [Parameter(Mandatory = $true)][ValidateSet('GET', 'POST')][string]$Method,
        [Parameter(Mandatory = $true)][string]$Uri,
        [Parameter(Mandatory = $true)][hashtable]$Headers,
        [string]$JsonBody
    )

    $requestParams = @{
        Method          = $Method
        Uri             = $Uri
        Headers         = $Headers
        ErrorAction     = 'Stop'
        UseBasicParsing = $true
    }

    if ($Method -eq 'POST') {
        $requestParams.ContentType = 'application/json'
        $requestParams.Body = $JsonBody
    }

    try {
        $response = Invoke-WebRequest @requestParams
        if ([string]::IsNullOrWhiteSpace($response.Content)) { throw 'B2 returned an empty response body.' }
        return ($response.Content | ConvertFrom-Json)
    } catch {
        $summary = Get-B2ErrorSummary -ErrorRecord $_
        throw "B2 request failed: $summary"
    }
}

$secretPtr = [IntPtr]::Zero
$masterSecret = $null
$basicAuth = $null
$rawCredentials = $null
$authResponse = $null
$bucketResponse = $null
$secureSecret = $null

try {
    Write-Host ''
    Write-Host 'SP2L B2 READ-ONLY DIAGNOSTICS' -ForegroundColor Cyan
    Write-Host "Target bucket: $ExpectedBucketName"
    Write-Host "Target bucket ID: $BucketId"
    Write-Host 'Actions: authorize + read bucket only'
    Write-Host 'No key creation, upload, delete, or bucket mutation.'

    $masterKeyId = Read-Host 'Master Application Key ID'
    if ([string]::IsNullOrWhiteSpace($masterKeyId)) { throw 'Master Application Key ID is required.' }

    $secureSecret = Read-Host 'Master Application Key SECRET (hidden)' -AsSecureString
    if ($secureSecret.Length -eq 0) { throw 'Master Application Key secret is required.' }

    $secretPtr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureSecret)
    $masterSecret = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($secretPtr)
    $rawCredentials = '{0}:{1}' -f $masterKeyId, $masterSecret
    $basicAuth = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($rawCredentials))

    Write-Host ''
    Write-Host '[1/3] Authorizing with Backblaze...' -ForegroundColor Yellow

    $authResponse = Invoke-B2JsonRequest -Method GET -Uri 'https://api.backblazeb2.com/b2api/v4/b2_authorize_account' -Headers @{ Authorization = "Basic $basicAuth" }

    $apiUrl = [string]$authResponse.apiInfo.storageApi.apiUrl
    $authToken = [string]$authResponse.authorizationToken
    $accountId = [string]$authResponse.accountId
    $allowedCapabilities = @($authResponse.apiInfo.storageApi.allowed.capabilities)

    if ([string]::IsNullOrWhiteSpace($apiUrl) -or [string]::IsNullOrWhiteSpace($authToken) -or [string]::IsNullOrWhiteSpace($accountId)) {
        throw 'Authorization response did not contain the required v4 fields.'
    }

    Write-Host 'AUTHORIZATION=PASS' -ForegroundColor Green
    Write-Host "API_HOST=$(([uri]$apiUrl).Host)"

    Write-Host ''
    Write-Host '[2/3] Inspecting authorization capabilities...' -ForegroundColor Yellow
    foreach ($capability in @('writeKeys', 'listBuckets', 'readBucketRetentions')) {
        $present = $allowedCapabilities -contains $capability
        Write-Host ("{0}={1}" -f $capability.ToUpperInvariant(), $present)
    }
    if ($allowedCapabilities.Count -eq 0) { Write-Host 'CAPABILITY_ENVELOPE=NOT_RETURNED' -ForegroundColor Yellow }
    if ($allowedCapabilities -notcontains 'listBuckets') { throw 'The authorized key does not expose listBuckets; cannot perform the read-only bucket check.' }

    Write-Host ''
    Write-Host '[3/3] Reading the target bucket...' -ForegroundColor Yellow

    # b2_list_buckets uses bucketId (singular) as a filter.
    # b2_create_key v4 uses bucketIds (plural array); these schemas differ.
    $listBody = @{ accountId = $accountId; bucketId = $BucketId } | ConvertTo-Json -Depth 5
    $bucketResponse = Invoke-B2JsonRequest -Method POST -Uri ($apiUrl.TrimEnd('/') + '/b2api/v4/b2_list_buckets') -Headers @{ Authorization = $authToken } -JsonBody $listBody

    $matches = @($bucketResponse.buckets | Where-Object { $_.bucketId -eq $BucketId })
    if ($matches.Count -ne 1) { throw "Expected exactly one bucket with the configured ID; found $($matches.Count)." }

    $bucket = $matches[0]
    if ($bucket.bucketName -ne $ExpectedBucketName) { throw "Bucket ID resolved to an unexpected bucket name: '$($bucket.bucketName)'." }

    Write-Host 'BUCKET_ACCESS=PASS' -ForegroundColor Green
    Write-Host "BUCKET_NAME=$($bucket.bucketName)"
    Write-Host "BUCKET_TYPE=$($bucket.bucketType)"

    $lockConfig = $bucket.fileLockConfiguration
    if ($null -ne $lockConfig) {
        Write-Host "OBJECT_LOCK_ENABLED=$($lockConfig.isFileLockEnabled)"
        if ($lockConfig.isClientAuthorizedToRead -eq $false) {
            Write-Host 'RETENTION_READBACK=NOT_AUTHORIZED' -ForegroundColor Yellow
        } elseif ($null -ne $lockConfig.value.defaultRetention) {
            Write-Host "DEFAULT_RETENTION_MODE=$($lockConfig.value.defaultRetention.mode)"
            Write-Host "DEFAULT_RETENTION_PERIOD=$($lockConfig.value.defaultRetention.period)"
        } else {
            Write-Host 'DEFAULT_RETENTION=NOT_CONFIGURED_OR_NOT_RETURNED'
        }
    } else {
        Write-Host 'OBJECT_LOCK_CONFIGURATION=NOT_RETURNED' -ForegroundColor Yellow
    }

    Write-Host ''
    Write-Host 'DIAGNOSTIC_RESULT=PASS' -ForegroundColor Green
    Write-Host 'NO_KEYS_CREATED_OR_DELETED'
    Write-Host 'NO_FILES_UPLOADED_OR_DELETED'
    Write-Host 'NO_BUCKET_SETTINGS_CHANGED'
}
catch {
    Write-Host ''
    Write-Host 'DIAGNOSTIC_RESULT=FAIL' -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host 'No automatic retry was attempted.'
}
finally {
    if ($secretPtr -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($secretPtr) }
    $masterSecret = $null
    $basicAuth = $null
    $rawCredentials = $null
    $authResponse = $null
    $bucketResponse = $null
    $secureSecret = $null
    $authToken = $null
    $apiUrl = $null
    $accountId = $null
}
