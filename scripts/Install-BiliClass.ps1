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
$ProgressPreference = 'SilentlyContinue'
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
    if (Get-Process -Id $WaitForProcessId -ErrorAction SilentlyContinue) { throw 'Hãy đóng BiliClass trước khi cài bản cập nhật.' }
}
$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$installPath = [IO.Path]::GetFullPath($InstallRoot).TrimEnd('\')
$markerPath = Join-Path $installPath '.biliclass-install.json'
if ($installPath -eq [IO.Path]::GetPathRoot($installPath).TrimEnd('\')) { throw 'Hãy tạo một thư mục riêng để cài BiliClass, ví dụ D:\BiliClass-App. Không chọn cả ổ đĩa.' }
if (Test-Path -LiteralPath (Join-Path $installPath 'library.db')) { throw 'Đây là thư viện bài giảng. Hãy chọn một thư mục khác để cài ứng dụng, ví dụ D:\BiliClass-App.' }
if (-not $Uninstall -and (Test-Path -LiteralPath $installPath) -and -not (Test-Path -LiteralPath $markerPath) -and (Get-ChildItem -LiteralPath $installPath -Force | Select-Object -First 1)) { throw ('Thư mục này đã có dữ liệu. Hãy chọn hoặc tạo một thư mục mới, trống hoàn toàn để cài BiliClass. Không chọn thư mục đang chứa bộ cài; dữ liệu hiện có được giữ nguyên. Thư mục đã chọn: ' + $installPath) }
if (-not $Uninstall -and (Test-Path -LiteralPath $markerPath)) {
    $previousMarker = Get-Content -LiteralPath $markerPath -Raw | ConvertFrom-Json
    if ($previousMarker.product -ne 'BiliClass' -or $previousMarker.root -ne $installPath) { throw 'Chưa xác nhận được bản BiliClass trong thư mục này. Hãy chọn một thư mục mới để cài; dữ liệu hiện có được giữ nguyên.' }
}
$shortcutPath = Join-Path ([Environment]::GetFolderPath('Programs')) 'BiliClass.lnk'
$desktopShortcutPath = Join-Path ([Environment]::GetFolderPath('Desktop')) 'BiliClass.lnk'
$uninstallKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\BiliClass'
if ($Uninstall) {
    if (-not (Test-Path -LiteralPath $markerPath)) { throw 'Đây không phải thư mục cài BiliClass đã được xác nhận. Chưa xóa dữ liệu.' }
    $marker = Get-Content -LiteralPath $markerPath -Raw | ConvertFrom-Json
    if ($marker.product -ne 'BiliClass' -or $marker.root -ne $installPath) { throw 'Thông tin bản cài BiliClass không khớp thư mục. Chưa xóa dữ liệu.' }
    $running = Get-Process BiliClass -ErrorAction SilentlyContinue | Where-Object { $_.Path -and $_.Path.StartsWith($installPath + '\', [StringComparison]::OrdinalIgnoreCase) }
    if ($running) { throw 'Hãy đóng bản BiliClass này trước khi gỡ cài đặt.' }
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
            throw 'Gói cài có đường dẫn không hợp lệ hoặc trùng tên. Hãy chép lại bộ cài đầy đủ.'
        }
    }
    $manifestEntry = $archive.GetEntry('app-manifest.json')
    if (-not $manifestEntry -or $manifestEntry.Length -gt 8MB) { $archive.Dispose(); throw 'Gói cài thiếu hoặc sai bảng kiểm tra dữ liệu. Hãy chép lại bộ cài đầy đủ.' }
    $reader = New-Object IO.StreamReader($manifestEntry.Open(), [Text.Encoding]::UTF8)
    try { $manifest = $reader.ReadToEnd() | ConvertFrom-Json } finally { $reader.Dispose() }
} else {
    $manifest = Get-Content -LiteralPath (Join-Path $packageRoot 'app-manifest.json') -Raw | ConvertFrom-Json
}
try {
if ($manifest.product -ne 'BiliClass' -or $manifest.version -notmatch '^\d+\.\d+\.\d+(?:rc\d+)?$') { throw 'Thông tin gói cài không hợp lệ. Hãy chép lại bộ cài đầy đủ.' }
if ($ExpectedVersion -and $manifest.version -ne $ExpectedVersion) { throw 'File ZIP khác phiên bản với bộ cài. Hãy chép đúng hai file EXE và ZIP cùng bộ.' }
$fileEntries = @($manifest.files.PSObject.Properties)
if ($fileEntries.Count -lt 1 -or $fileEntries.Count -gt 20000 -or -not $manifest.files.'BiliClass.exe') { throw 'Gói cài chưa đầy đủ. Hãy chép lại bộ cài.' }
$sourceRoot = [IO.Path]::GetFullPath((Join-Path $packageRoot 'BiliClass'))
$names = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
$requiredBytes = [long]64MB
foreach ($entry in $fileEntries) {
    if ($entry.Name -match '(^/|\\|:|(^|/)\.\.?(/|$))' -or -not $names.Add($entry.Name) -or $entry.Value -notmatch '^[a-fA-F0-9]{64}$') { throw 'Gói cài có đường dẫn không hợp lệ hoặc trùng tên. Hãy chép lại bộ cài đầy đủ.' }
    $sourceFile = [IO.Path]::GetFullPath((Join-Path $sourceRoot $entry.Name))
    if (-not $sourceFile.StartsWith($sourceRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Đường dẫn trong gói cài không hợp lệ. Hãy chép lại bộ cài đầy đủ.' }
    if ($archive) {
        $zipEntry = $archive.GetEntry('BiliClass/' + $entry.Name)
        if (-not $zipEntry) { throw ('Gói cài thiếu tệp. Hãy chép lại bộ cài đầy đủ. Tệp thiếu: ' + $entry.Name) }
        $requiredBytes += $zipEntry.Length
    } else {
        if ((Get-FileSha256 $sourceFile) -ne $entry.Value) { throw ('Tệp trong bộ cài bị thiếu hoặc thay đổi. Hãy chép lại bộ cài. Tệp: ' + $entry.Name) }
        $requiredBytes += (Get-Item -LiteralPath $sourceFile).Length
    }
}
$drive = New-Object IO.DriveInfo([IO.Path]::GetPathRoot($installPath))
if ($drive.AvailableFreeSpace -lt $requiredBytes) { throw ('Ổ cài chưa đủ dung lượng trống. Cần khoảng ' + [Math]::Round($requiredBytes / 1GB, 2) + ' GB trống; hãy chọn ổ khác hoặc giải phóng dung lượng rồi thử lại.') }
$versionPath = Join-Path $installPath $manifest.version
if (Test-Path -LiteralPath $versionPath) { throw 'Phiên bản này đã có trong thư mục đã chọn. Hãy mở bản đã cài hoặc chọn một thư mục mới.' }
$staging = Join-Path $installPath ('.staging-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $staging -Force | Out-Null
try {
$completed = 0
foreach ($entry in $fileEntries) {
    $target = [IO.Path]::GetFullPath((Join-Path $staging $entry.Name))
    if (-not $target.StartsWith($staging + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Đường dẫn cài đặt không hợp lệ. Hãy chọn một thư mục mới.' }
    New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
    if ($archive) {
        $inputStream = $archive.GetEntry('BiliClass/' + $entry.Name).Open()
        try {
            $outputStream = [IO.File]::Create($target)
            try { $inputStream.CopyTo($outputStream) } finally { $outputStream.Dispose() }
        } finally { $inputStream.Dispose() }
        if ((Get-FileSha256 $target) -ne $entry.Value) { throw ('Tệp trong bộ cài bị thiếu hoặc thay đổi. Hãy chép lại bộ cài. Tệp: ' + $entry.Name) }
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
        if ($identityProcess.ExitCode -ne 0) { throw 'Chưa tạo được biểu tượng BiliClass. Hãy đóng ứng dụng rồi thử cài lại vào một thư mục mới.' }
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
