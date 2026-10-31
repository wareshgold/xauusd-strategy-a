#requires -Version 5.1
<#
.SYNOPSIS
  Read-only diagnostics for a bucket-scoped Backblaze B2 Application Key.

.DESCRIPTION
  Authenticates with a locally-entered restricted Application Key, reads the
  v4 authorization envelope from apiInfo.storageApi.allowed, verifies the
  configured bucket and factory/test/ prefix, then calls b2_list_file_names.
  This script does NOT list buckets, upload/download files, create/delete keys,
  delete files, or modify bucket settings.

.SECURITY
  Never share the Application Key secret, authorization token, or terminal
  session containing secrets. The secret is entered as a SecureString.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ExpectedBucketId = '0bd958e97ddd990eae1f0a1c'
$ExpectedBucketName = 'sp2l-factory-evidence'
$ExpectedPrefixWithoutLeadingSlash = 'factory/test/'

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
    }
    catch {
        $summary = Get-B2ErrorSummary -ErrorRecord $_
        throw "B2 request failed: $summary"
    }
}

$secretPtr = [IntPtr]::Zero
$secretText = $null
$rawCredentials = $null
$basicAuth = $null
$authResponse = $null
$listResponse = $null
$secureSecret = $null
$authToken = $null

try {
    Write-Host ''
    Write-Host 'SP2L B2 SCOPED-KEY READ-ONLY DIAGNOSTICS' -ForegroundColor Cyan
    Write-Host "Expected bucket: $ExpectedBucketName"
    Write-Host "Expected prefix: $ExpectedPrefixWithoutLeadingSlash (leading slash is tolerated)"
    Write-Host 'Actions: authorize + inspect key scope + list file names only'
    Write-Host 'No bucket listing, upload, download, delete, key mutation, or bucket mutation.'

    $keyId = Read-Host 'Restricted Application Key ID'
    if ([string]::IsNullOrWhiteSpace($keyId)) { throw 'Application Key ID is required.' }

    $secureSecret = Read-Host 'Restricted Application Key SECRET (hidden)' -AsSecureString
    if ($secureSecret.Length -eq 0) { throw 'Application Key secret is required.' }

    $secretPtr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureSecret)
    $secretText = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($secretPtr)
    $rawCredentials = '{0}:{1}' -f $keyId, $secretText
    $basicAuth = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($rawCredentials))

    Write-Host ''
    Write-Host '[1/3] Authorizing...' -ForegroundColor Yellow
    $authResponse = Invoke-B2JsonRequest -Method GET -Uri 'https://api.backblazeb2.com/b2api/v4/b2_authorize_account' -Headers @{ Authorization = "Basic $basicAuth" }

    $storageApi = $authResponse.apiInfo.storageApi
    $apiUrl = [string]$storageApi.apiUrl
    $authToken = [string]$authResponse.authorizationToken
    $allowed = $storageApi.allowed

    if ([string]::IsNullOrWhiteSpace($apiUrl) -or [string]::IsNullOrWhiteSpace($authToken)) {
        throw 'Authorization response is missing apiInfo.storageApi.apiUrl or authorizationToken.'
    }
    if ($null -eq $allowed) {
        throw 'Authorization response is missing apiInfo.storageApi.allowed; refusing to continue.'
    }

    Write-Host 'AUTHORIZATION=PASS' -ForegroundColor Green
    Write-Host "API_HOST=$(([uri]$apiUrl).Host)"

    Write-Host ''
    Write-Host '[2/3] Verifying the authorized scope...' -ForegroundColor Yellow

    # B2 Native API v4 represents bucket restrictions as allowed.buckets[].
    # The pre-v4 allowed.bucketId / allowed.bucketName fields are not present.
    # Normalize the v4 allowed-buckets value defensively. PowerShell may
    # deserialize a single object, an array, or a null value differently.
    $rawBuckets = $allowed.buckets
    $allowedBuckets = @()
    if ($null -ne $rawBuckets) {
        if ($rawBuckets -is [System.Array]) {
            $allowedBuckets = @($rawBuckets)
        }
        else {
            $allowedBuckets = @($rawBuckets)
        }
    }

    $bucketDiagnostics = @(
        foreach ($bucket in $allowedBuckets) {
            if ($null -eq $bucket) {
                [pscustomobject]@{ type = '<null>'; properties = ''; id = ''; name = '' }
            }
            else {
                $props = @($bucket.PSObject.Properties | ForEach-Object { $_.Name })
                $idValue = ''
                $nameValue = ''
                if ($bucket -is [System.Collections.IDictionary]) {
                    if ($bucket.Contains('id')) { $idValue = [string]$bucket['id'] }
                    if ($bucket.Contains('name')) { $nameValue = [string]$bucket['name'] }
                }
                else {
                    $idProperty = $bucket.PSObject.Properties['id']
                    $nameProperty = $bucket.PSObject.Properties['name']
                    if ($null -ne $idProperty) { $idValue = [string]$idProperty.Value }
                    if ($null -ne $nameProperty) { $nameValue = [string]$nameProperty.Value }
                }
                [pscustomobject]@{
                    type = $bucket.GetType().FullName
                    properties = ($props -join ',')
                    id = $idValue
                    name = $nameValue
                }
            }
        }
    )

    $allowedBucketIds = @($bucketDiagnostics | ForEach-Object { $_.id })
    $matchingBuckets = @($allowedBuckets | Where-Object {
        $candidateId = ''
        if ($null -ne $_) {
            if ($_ -is [System.Collections.IDictionary]) {
                if ($_.Contains('id')) { $candidateId = [string]$_['id'] }
            }
            else {
                $candidateProperty = $_.PSObject.Properties['id']
                if ($null -ne $candidateProperty) { $candidateId = [string]$candidateProperty.Value }
            }
        }
        $candidateId -eq $ExpectedBucketId
    })
    $allowedPrefix = ''
    if ($null -ne $allowed.PSObject.Properties['namePrefix']) {
        $allowedPrefix = [string]$allowed.namePrefix
    }
    $capabilities = @()
    if ($null -ne $allowed.PSObject.Properties['capabilities']) {
        $capabilities = @($allowed.capabilities)
    }
    if ($matchingBuckets.Count -ne 1) {
        $safeShape = ConvertTo-Json -InputObject $bucketDiagnostics -Depth 6 -Compress
        Write-Host "ALLOWED_BUCKETS_DIAGNOSTIC=$safeShape"
        Write-Host "ALLOWED_PREFIX=$allowedPrefix"
        Write-Host "ALLOWED_CAPABILITIES=$($capabilities -join ',')"
        throw "Bucket scope mismatch. Expected bucket ID was not present in allowed.buckets[]. Returned bucket count=$($allowedBuckets.Count); IDs='$($allowedBucketIds -join ',')'."
    }
    $matchedBucket = $matchingBuckets[0]
    $allowedBucketId = ''
    $allowedBucketName = ''
    if ($matchedBucket -is [System.Collections.IDictionary]) {
        if ($matchedBucket.Contains('id')) { $allowedBucketId = [string]$matchedBucket['id'] }
        if ($matchedBucket.Contains('name')) { $allowedBucketName = [string]$matchedBucket['name'] }
    }
    else {
        if ($null -ne $matchedBucket.PSObject.Properties['id']) { $allowedBucketId = [string]$matchedBucket.id }
        if ($null -ne $matchedBucket.PSObject.Properties['name']) { $allowedBucketName = [string]$matchedBucket.name }
    }
    if ($allowedBucketName -and $allowedBucketName -ne $ExpectedBucketName) {
        throw "Bucket name mismatch: '$allowedBucketName'."
    }
    if ([string]::IsNullOrWhiteSpace($allowedPrefix)) {
        throw 'The key did not return a namePrefix; refusing to list outside a confirmed prefix.'
    }

    $normalizedPrefix = $allowedPrefix.TrimStart('/')
    if (-not $normalizedPrefix.StartsWith($ExpectedPrefixWithoutLeadingSlash, [StringComparison]::Ordinal)) {
        throw "Prefix scope mismatch. Returned prefix '$allowedPrefix' is not the expected factory/test/ prefix."
    }
    if ($capabilities -notcontains 'listFiles') {
        throw 'The key lacks listFiles; cannot perform the read-only file listing.'
    }

    Write-Host 'BUCKET_SCOPE=PASS' -ForegroundColor Green
    Write-Host 'PREFIX_SCOPE=PASS' -ForegroundColor Green
    Write-Host "ALLOWED_PREFIX=$allowedPrefix"
    Write-Host "LIST_FILES=$($capabilities -contains 'listFiles')"
    Write-Host "READ_FILES=$($capabilities -contains 'readFiles')"
    Write-Host "WRITE_FILES=$($capabilities -contains 'writeFiles')"

    Write-Host ''
    Write-Host '[3/3] Listing file names inside the authorized prefix...' -ForegroundColor Yellow

    $listBody = @{
        bucketId = $allowedBucketId
        prefix = $allowedPrefix
        maxFileCount = 10
    } | ConvertTo-Json -Depth 5

    $listResponse = Invoke-B2JsonRequest -Method POST -Uri ($apiUrl.TrimEnd('/') + '/b2api/v4/b2_list_file_names') -Headers @{ Authorization = $authToken } -JsonBody $listBody

    $filesReturned = @($listResponse.files).Count
    Write-Host 'LIST_FILES_REQUEST=PASS' -ForegroundColor Green
    Write-Host "FILES_RETURNED=$filesReturned"
    Write-Host ''
    Write-Host 'DIAGNOSTIC_RESULT=PASS' -ForegroundColor Green
    Write-Host 'NO_FILES_UPLOADED_OR_DOWNLOADED'
    Write-Host 'NO_FILES_OR_KEYS_DELETED'
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
    $secretText = $null
    $rawCredentials = $null
    $basicAuth = $null
    $authResponse = $null
    $listResponse = $null
    $secureSecret = $null
    $authToken = $null
}
