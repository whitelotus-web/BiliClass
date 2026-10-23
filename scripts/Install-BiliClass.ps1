param(
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA 'Programs\BiliClass'),
    [switch]$NoShortcuts,
    [switch]$Uninstall,
    [int]$WaitForProcessId = 0,
    [switch]$LaunchAfterInstall,
    [string]$PackageZip = '',
    [string]$ExpectedVersion = ''
)
$ErrorActionPreference = 'Stop'
function Get-FileSha256([string]$Path) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $stream = [IO.File]::OpenRead($Path)
        try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
        finally { $stream.Dispose() }
    } finally { $sha.Dispose() }
}
if ($WaitForProcessId -gt 0) {
    # The old version must finish before switching the shortcut to the new version.
    Wait-Process -Id $WaitForProcessId -Timeout 120 -ErrorAction SilentlyContinue
    if (Get-Process -Id $WaitForProcessId -ErrorAction SilentlyContinue) { throw 'Close BiliClass before installing the update.' }
}
$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$installPath = [IO.Path]::GetFullPath($InstallRoot).TrimEnd('\')
$markerPath = Join-Path $installPath '.biliclass-install.json'
if ($installPath -eq [IO.Path]::GetPathRoot($installPath).TrimEnd('\')) { throw 'Cannot use a drive root.' }
if (Test-Path -LiteralPath (Join-Path $installPath 'library.db')) { throw 'Select an application folder separate from the lesson library.' }
if (-not $Uninstall -and (Test-Path -LiteralPath $installPath) -and -not (Test-Path -LiteralPath $markerPath) -and (Get-ChildItem -LiteralPath $installPath -Force | Select-Object -First 1)) { throw 'Use an empty folder or an existing verified BiliClass installation.' }
if (-not $Uninstall -and (Test-Path -LiteralPath $markerPath)) {
    $previousMarker = Get-Content -LiteralPath $markerPath -Raw | ConvertFrom-Json
    if ($previousMarker.product -ne 'BiliClass' -or $previousMarker.root -ne $installPath) { throw 'Installation marker mismatch.' }
}
$shortcutPath = Join-Path ([Environment]::GetFolderPath('Programs')) 'BiliClass.lnk'
$desktopShortcutPath = Join-Path ([Environment]::GetFolderPath('Desktop')) 'BiliClass.lnk'
$uninstallKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\BiliClass'
if ($Uninstall) {
    if (-not (Test-Path -LiteralPath $markerPath)) { throw 'Not a verified BiliClass installation.' }
    $marker = Get-Content -LiteralPath $markerPath -Raw | ConvertFrom-Json
    if ($marker.product -ne 'BiliClass' -or $marker.root -ne $installPath) { throw 'Installation marker mismatch.' }
    $running = Get-Process BiliClass -ErrorAction SilentlyContinue | Where-Object { $_.Path -and $_.Path.StartsWith($installPath + '\', [StringComparison]::OrdinalIgnoreCase) }
    if ($running) { throw 'Close this BiliClass installation before uninstalling.' }
    if (-not $NoShortcuts -and (Test-Path -LiteralPath $uninstallKey)) {
        $registered = Get-ItemProperty -LiteralPath $uninstallKey
        if ($registered.InstallLocation -eq $installPath) { Remove-Item -LiteralPath $uninstallKey -Force }
    }
    # The absolute named install directory and marker were verified above. User lesson data is elsewhere.
    Remove-Item -LiteralPath $installPath -Recurse -Force
    foreach ($ownedShortcutPath in @($shortcutPath, $desktopShortcutPath)) {
      if (-not $NoShortcuts -and (Test-Path -LiteralPath $ownedShortcutPath)) {
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($ownedShortcutPath)
        if ($shortcut.TargetPath.StartsWith($installPath + '\', [StringComparison]::OrdinalIgnoreCase)) { Remove-Item -LiteralPath $ownedShortcutPath }
      }
    }
    Write-Output 'BiliClass removed. Lesson libraries and backups were preserved.'
    exit 0
}
$archive = $null
if ($PackageZip) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [IO.Compression.ZipFile]::OpenRead([IO.Path]::GetFullPath($PackageZip))
    $zipNames = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($zipEntry in $archive.Entries) {
        if (-not $zipNames.Add($zipEntry.FullName) -or $zipEntry.FullName -match '(^/|\\|:|(^|/)\.\.?(/|$))') {
            $archive.Dispose()
            throw 'Unsafe or repeated archive path.'
        }
    }
    $manifestEntry = $archive.GetEntry('app-manifest.json')
    if (-not $manifestEntry -or $manifestEntry.Length -gt 8MB) { $archive.Dispose(); throw 'Missing or oversized package manifest.' }
    $reader = New-Object IO.StreamReader($manifestEntry.Open(), [Text.Encoding]::UTF8)
    try { $manifest = $reader.ReadToEnd() | ConvertFrom-Json } finally { $reader.Dispose() }
} else {
    $manifest = Get-Content -LiteralPath (Join-Path $packageRoot 'app-manifest.json') -Raw | ConvertFrom-Json
}
try {
if ($manifest.product -ne 'BiliClass' -or $manifest.version -notmatch '^\d+\.\d+\.\d+(?:rc\d+)?$') { throw 'Invalid package manifest.' }
if ($ExpectedVersion -and $manifest.version -ne $ExpectedVersion) { throw 'Package version differs from this installer.' }
$fileEntries = @($manifest.files.PSObject.Properties)
if ($fileEntries.Count -lt 1 -or $fileEntries.Count -gt 20000 -or -not $manifest.files.'BiliClass.exe') { throw 'Incomplete package manifest.' }
$sourceRoot = [IO.Path]::GetFullPath((Join-Path $packageRoot 'BiliClass'))
$names = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
$requiredBytes = [long]64MB
foreach ($entry in $fileEntries) {
    if ($entry.Name -match '(^/|\\|:|(^|/)\.\.?(/|$))' -or -not $names.Add($entry.Name) -or $entry.Value -notmatch '^[a-fA-F0-9]{64}$') { throw 'Unsafe or repeated package path.' }
    $sourceFile = [IO.Path]::GetFullPath((Join-Path $sourceRoot $entry.Name))
    if (-not $sourceFile.StartsWith($sourceRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe package path.' }
    if ($archive) {
        $zipEntry = $archive.GetEntry('BiliClass/' + $entry.Name)
        if (-not $zipEntry) { throw ('Missing package file: ' + $entry.Name) }
        $requiredBytes += $zipEntry.Length
    } else {
        if ((Get-FileSha256 $sourceFile) -ne $entry.Value) { throw ('Checksum mismatch: ' + $entry.Name) }
        $requiredBytes += (Get-Item -LiteralPath $sourceFile).Length
    }
}
$drive = New-Object IO.DriveInfo([IO.Path]::GetPathRoot($installPath))
if ($drive.AvailableFreeSpace -lt $requiredBytes) { throw 'Not enough free space on the selected installation drive.' }
$versionPath = Join-Path $installPath $manifest.version
if (Test-Path -LiteralPath $versionPath) { throw 'This version is already installed. Uninstall or select a different install directory.' }
$staging = Join-Path $installPath ('.staging-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $staging -Force | Out-Null
try {
$completed = 0
foreach ($entry in $fileEntries) {
    $target = [IO.Path]::GetFullPath((Join-Path $staging $entry.Name))
    if (-not $target.StartsWith($staging + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe install path.' }
    New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
    if ($archive) {
        $inputStream = $archive.GetEntry('BiliClass/' + $entry.Name).Open()
        try {
            $outputStream = [IO.File]::Create($target)
            try { $inputStream.CopyTo($outputStream) } finally { $outputStream.Dispose() }
        } finally { $inputStream.Dispose() }
        if ((Get-FileSha256 $target) -ne $entry.Value) { throw ('Checksum mismatch: ' + $entry.Name) }
    } else {
        Copy-Item -LiteralPath (Join-Path $sourceRoot $entry.Name) -Destination $target
    }
    $completed++
    if ($completed % 50 -eq 0 -or $completed -eq $fileEntries.Count) {
        Write-Output ('PROGRESS|' + [int](100 * $completed / $fileEntries.Count) + '|Dang cai dat ' + $completed + '/' + $fileEntries.Count + ' tep')
    }
}
[IO.Directory]::Move($staging, $versionPath)
} finally {
    # This unique staging directory is owned by this attempt, under the checked
    # application root. Roll back incomplete extraction, never a user library.
    $stagingPath = [IO.Path]::GetFullPath($staging)
    if ($stagingPath.StartsWith($installPath + '\.staging-', [StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $stagingPath)) {
        Remove-Item -LiteralPath $stagingPath -Recurse -Force
    }
}
@{product='BiliClass';root=$installPath;version=$manifest.version} | ConvertTo-Json | Set-Content -LiteralPath $markerPath -Encoding UTF8
Copy-Item -LiteralPath $MyInvocation.MyCommand.Path -Destination (Join-Path $installPath 'Install-BiliClass.ps1') -Force
@'
@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-BiliClass.ps1" -InstallRoot "%~dp0." -Uninstall
pause
'@ | Set-Content -LiteralPath (Join-Path $installPath 'Uninstall-BiliClass.cmd') -Encoding ASCII
if (-not $NoShortcuts) {
    $shell = New-Object -ComObject WScript.Shell
    foreach ($ownedShortcutPath in @($shortcutPath, $desktopShortcutPath)) {
        $shortcut = $shell.CreateShortcut($ownedShortcutPath)
        $shortcut.TargetPath = Join-Path $versionPath 'BiliClass.exe'
        $shortcut.Arguments = ''
        $shortcut.WorkingDirectory = $versionPath
        $shortcut.Description = 'BiliClass - English Vietnamese teaching workspace'
        $shortcut.IconLocation = (Join-Path $versionPath 'BiliClass.exe') + ',0'
        $shortcut.Save()
        # Match the process/window identity so Explorer resolves the group icon
        # after versioned executable paths change. This CLI opens no UI/library.
        $identityProcess = Start-Process -FilePath (Join-Path $versionPath 'BiliClass.exe') -ArgumentList @('--register-shortcut',('"' + $ownedShortcutPath + '"')) -WindowStyle Hidden -Wait -PassThru
        if ($identityProcess.ExitCode -ne 0) { throw 'Could not register the BiliClass shortcut identity.' }
    }
    New-Item -Path $uninstallKey -Force | Out-Null
    $uninstallProperties = @{
        DisplayName='BiliClass'; DisplayVersion=$manifest.version; Publisher='Nguyen Dieu Linh';
        InstallLocation=$installPath; DisplayIcon=(Join-Path $versionPath 'BiliClass.exe');
        UninstallString=('powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + (Join-Path $installPath 'Install-BiliClass.ps1') + '" -InstallRoot "' + $installPath + '" -Uninstall')
    }
    foreach ($name in $uninstallProperties.Keys) {
        New-ItemProperty -LiteralPath $uninstallKey -Name $name -Value $uninstallProperties[$name] -PropertyType String -Force | Out-Null
    }
    New-ItemProperty -LiteralPath $uninstallKey -Name NoModify -Value 1 -PropertyType DWord -Force | Out-Null
    New-ItemProperty -LiteralPath $uninstallKey -Name NoRepair -Value 1 -PropertyType DWord -Force | Out-Null
}
Write-Output ('Installed BiliClass ' + $manifest.version + ' at ' + $versionPath)
Write-Output 'Lesson data is preserved across installs. Start BiliClass from the Start menu.'
if ($LaunchAfterInstall) {
    Start-Process -FilePath (Join-Path $versionPath 'BiliClass.exe') -WorkingDirectory $versionPath
}
} finally {
    if ($archive) { $archive.Dispose() }
}
