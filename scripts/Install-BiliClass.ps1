param(
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA 'Programs\BiliClass'),
    [switch]$NoShortcuts,
    [switch]$Uninstall
)
$ErrorActionPreference = 'Stop'
$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$installPath = [IO.Path]::GetFullPath($InstallRoot).TrimEnd('\')
$markerPath = Join-Path $installPath '.biliclass-install.json'
if ($installPath -eq [IO.Path]::GetPathRoot($installPath).TrimEnd('\')) { throw 'Cannot use a drive root.' }
if (Test-Path -LiteralPath (Join-Path $installPath 'library.db')) { throw 'Select an application folder separate from the lesson library.' }
if (-not $Uninstall -and (Test-Path -LiteralPath $installPath) -and -not (Test-Path -LiteralPath $markerPath) -and (Get-ChildItem -LiteralPath $installPath -Force | Select-Object -First 1)) { throw 'Use an empty folder or an existing verified BiliClass installation.' }
$shortcutPath = Join-Path ([Environment]::GetFolderPath('Programs')) 'BiliClass.lnk'
if ($Uninstall) {
    if (-not (Test-Path -LiteralPath $markerPath)) { throw 'Not a verified BiliClass installation.' }
    $marker = Get-Content -LiteralPath $markerPath -Raw | ConvertFrom-Json
    if ($marker.product -ne 'BiliClass' -or $marker.root -ne $installPath) { throw 'Installation marker mismatch.' }
    $running = Get-Process BiliClass -ErrorAction SilentlyContinue | Where-Object { $_.Path -and $_.Path.StartsWith($installPath + '\', [StringComparison]::OrdinalIgnoreCase) }
    if ($running) { throw 'Close this BiliClass installation before uninstalling.' }
    # The absolute named install directory and marker were verified above. User lesson data is elsewhere.
    Remove-Item -LiteralPath $installPath -Recurse -Force
    if (-not $NoShortcuts -and (Test-Path -LiteralPath $shortcutPath)) {
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($shortcutPath)
        if ($shortcut.TargetPath.StartsWith($installPath + '\', [StringComparison]::OrdinalIgnoreCase)) { Remove-Item -LiteralPath $shortcutPath }
    }
    Write-Output 'BiliClass removed. Lesson libraries and backups were preserved.'
    exit 0
}
$manifest = Get-Content -LiteralPath (Join-Path $packageRoot 'app-manifest.json') -Raw | ConvertFrom-Json
if ($manifest.product -ne 'BiliClass' -or $manifest.version -notmatch '^\d+\.\d+\.\d+(?:rc\d+)?$') { throw 'Invalid package manifest.' }
$sourceRoot = [IO.Path]::GetFullPath((Join-Path $packageRoot 'BiliClass'))
foreach ($entry in $manifest.files.PSObject.Properties) {
    $sourceFile = [IO.Path]::GetFullPath((Join-Path $sourceRoot $entry.Name))
    if (-not $sourceFile.StartsWith($sourceRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe package path.' }
    if ((Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.Value) { throw ('Checksum mismatch: ' + $entry.Name) }
}
$versionPath = Join-Path $installPath $manifest.version
if (Test-Path -LiteralPath $versionPath) { throw 'This version is already installed. Uninstall or select a different install directory.' }
$staging = Join-Path $installPath ('.staging-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $staging -Force | Out-Null
foreach ($entry in $manifest.files.PSObject.Properties) {
    $target = [IO.Path]::GetFullPath((Join-Path $staging $entry.Name))
    if (-not $target.StartsWith($staging + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe install path.' }
    New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $sourceRoot $entry.Name) -Destination $target
}
Move-Item -LiteralPath $staging -Destination $versionPath
@{product='BiliClass';root=$installPath;version=$manifest.version} | ConvertTo-Json | Set-Content -LiteralPath $markerPath -Encoding UTF8
Copy-Item -LiteralPath $MyInvocation.MyCommand.Path -Destination (Join-Path $installPath 'Install-BiliClass.ps1') -Force
if (-not $NoShortcuts) {
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = Join-Path $versionPath 'BiliClass.exe'
    $shortcut.WorkingDirectory = $versionPath
    $shortcut.Description = 'BiliClass - English Vietnamese teaching workspace'
    $shortcut.Save()
}
Write-Output ('Installed BiliClass ' + $manifest.version + ' at ' + $versionPath)
Write-Output 'Lesson data is preserved across installs. Start BiliClass from the Start menu.'
