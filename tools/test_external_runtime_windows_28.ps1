# Offline test for the EXPERIMENTAL v2.8 EXE that does NOT bundle Microsoft DLLs.
# This script does not install software, elevate permissions, download files or publish.
# It runs only when the operator explicitly supplies -LaunchSmoke.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ExePath,
    [Parameter(Mandatory = $true)][string]$ManifestPath,
    [string]$ExpectedSha256,
    [string]$ReportPath,
    [switch]$LaunchSmoke
)

$ErrorActionPreference = 'Stop'
if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { throw 'Windows 10/11 x64 is required.' }
$exe = (Resolve-Path -LiteralPath $ExePath -ErrorAction Stop).Path
if ([Environment]::Is64BitOperatingSystem -ne $true) { throw 'Windows x64 is required.' }
$build = [Environment]::OSVersion.Version.Build
if ($build -lt 10240) { throw 'Windows 10/11 or newer is required.' }

$sha = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
$proofFile = (Resolve-Path -LiteralPath $ManifestPath -ErrorAction Stop).Path
$proof = Get-Content -LiteralPath $proofFile -Raw | ConvertFrom-Json
if (-not ($proof.schema_version -eq 1 -and
           $proof.status -eq 'EXPERIMENT_ONLY' -and
           $proof.native_file_count -eq 62 -and
           $proof.bundled_microsoft_runtime_count -eq 0 -and
           $proof.requires_official_vc_redist_x64 -eq $true -and
           $proof.release_authorized -eq $false -and
           $proof.source_git_commit -match '^[0-9a-fA-F]{40}$' -and
           $proof.exe_sha256 -eq $sha)) {
    throw 'The test EXE does not match its 62-native experiment manifest.'
}
if ($ExpectedSha256) {
    if ($ExpectedSha256 -notmatch '^[0-9a-fA-F]{64}$' -or
        $sha -ne $ExpectedSha256.ToLowerInvariant()) {
        throw 'The experimental EXE does not match the supplied SHA-256.'
    }
}
$version = (Get-Item -LiteralPath $exe).VersionInfo
if ($version.FileVersion -ne '2.8.0.0' -or
    $version.ProductName -ne 'PDF Compressor by Valik2005') {
    throw 'This file is not the reviewed PDF Compressor 2.8 EXE.'
}
$signature = (Get-AuthenticodeSignature -FilePath $exe).Status.ToString()
if ($signature -ne 'NotSigned') { throw "Expected unsigned test EXE; got $signature." }

$wanted = @('vcruntime140.dll', 'vcruntime140_1.dll', 'msvcp140.dll', 'ucrtbase.dll')
$systemDlls = @{}
$missing = @()
foreach ($name in $wanted) {
    $file = Join-Path $env:SystemRoot "System32\$name"
    if (Test-Path -LiteralPath $file -PathType Leaf) {
        $systemDlls[$name] = (Get-Item -LiteralPath $file).VersionInfo.FileVersion
    } else {
        $missing += $name
    }
}
$installed = $null
$runtimeVersion = $null
$reg = Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64' -ErrorAction SilentlyContinue
if ($null -ne $reg) {
    $installed = ($reg.Installed -eq 1)
    $runtimeVersion = [string]$reg.Version
}
$report = [ordered]@{
    experiment_only = $true
    release_approved = $false
    application_version = '2.8'
    exe_sha256 = $sha
    unsigned_authenticode = 'NotSigned'
    os_build = $build
    system_runtime_dll_versions = $systemDlls
    missing_system_dlls = @($missing)
    registered_x64_vc_runtime = $installed
    registered_x64_vc_runtime_version = $runtimeVersion
    gui_smoke_passed = $false
    note = 'This only checks prerequisites and GUI launch, not full Windows 10/11 PDF regressions or legal compliance.'
}
if ($missing.Count -eq 0 -and $LaunchSmoke) {
    $oldPath = $env:PATH
    $oldQpa = $env:QT_QPA_PLATFORM
    $oldPythonPath = $env:PYTHONPATH
    $temporary = Join-Path $env:TEMP ([Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $temporary -Force | Out-Null
    $copy = Join-Path $temporary 'PDF_Compressor_2_8.exe'
    Copy-Item -LiteralPath $exe -Destination $copy
    try {
        # Prevent false success from PATH contamination by Python, Qt or MySQL.
        $env:PATH = "$env:SystemRoot\System32;$env:SystemRoot;$env:SystemRoot\System32\Wbem"
        $env:QT_QPA_PLATFORM = 'offscreen'
        $env:PYTHONPATH = ''
        $process = Start-Process -FilePath $copy -WorkingDirectory $temporary -PassThru
        try {
            Start-Sleep -Seconds 12
            $process.Refresh()
            if ($process.HasExited) { throw "EXE exited during GUI smoke check: $($process.ExitCode)" }
            $report.gui_smoke_passed = $true
        } finally {
            $process.Refresh()
            if (-not $process.HasExited) { Stop-Process -Id $process.Id -Force }
        }
    } finally {
        $env:PATH = $oldPath
        if ($null -eq $oldQpa) { Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue }
        else { $env:QT_QPA_PLATFORM = $oldQpa }
        if ($null -eq $oldPythonPath) { Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue }
        else { $env:PYTHONPATH = $oldPythonPath }
        Remove-Item -LiteralPath $temporary -Recurse -Force -ErrorAction SilentlyContinue
    }
}
if ($ReportPath) {
    # Store no hostname, account name, installation paths or PDF contents.
    $report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ReportPath -Encoding utf8
}
Write-Host "Experimental PDF Compressor v2.8, SHA-256: $sha"
Write-Host "OS build: $build; Microsoft runtime missing: $($missing -join ', ')"
Write-Host "Registered official VC++ x64 runtime: $installed ($runtimeVersion)"
Write-Host "GUI smoke passed: $($report.gui_smoke_passed)"
if ($missing.Count -gt 0) {
    throw 'System runtime files are missing. Use the OFFICIAL Microsoft VC++ Redistributable x64 installer, then retest; this script never installs it.'
}
