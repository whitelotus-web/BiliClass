param(
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA 'Programs\BiliClass'),
    [switch]$NoShortcuts,
    [switch]$Uninstall,
    [int]$WaitForProcessId = 0,
    [switch]$LaunchAfterInstall,
    [string]$PackageZip = '',
    [string]$ExpectedVersion = '',
    [int]$WaitForExitSeconds = 120
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
try {
# Publish the verified new version beside the old one first. RC155 may keep a
# worker alive after closing; this must not leave a complete download unapplied.
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
$versionPath = Join-Path $installPath $manifest.version
$repairExisting = Test-Path -LiteralPath $versionPath
if ($repairExisting) {
    foreach ($entry in $fileEntries) {
        $existingFile = Join-Path $versionPath $entry.Name
        $checkedPath = $existingFile
        while ($checkedPath -and $checkedPath.Length -ge $versionPath.Length) {
            if ((Get-Item -LiteralPath $checkedPath -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Bản cài hiện có chứa liên kết thư mục; chưa sửa dữ liệu. Hãy chọn thư mục mới.' }
            $checkedPath = Split-Path -Parent $checkedPath
        }
        if ((Get-FileSha256 $existingFile) -ne $entry.Value) { throw 'Phiên bản này đã có nhưng tệp không khớp bộ cài. Dữ liệu được giữ nguyên; hãy chọn một thư mục mới.' }
    }
    Write-Output 'Existing version verified; refreshing launch shortcuts without replacing files.'
} else {
if ($drive.AvailableFreeSpace -lt $requiredBytes) { throw ('Ổ cài chưa đủ dung lượng trống. Cần khoảng ' + [Math]::Round($requiredBytes / 1GB, 2) + ' GB trống; hãy chọn ổ khác hoặc giải phóng dung lượng rồi thử lại.') }
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
}
@{product='BiliClass';root=$installPath;version=$manifest.version} | ConvertTo-Json | Set-Content -LiteralPath $markerPath -Encoding UTF8
Copy-Item -LiteralPath $MyInvocation.MyCommand.Path -Destination (Join-Path $installPath 'Install-BiliClass.ps1') -Force
@'
@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-BiliClass.ps1" -InstallRoot "%~dp0." -Uninstall
pause
'@ | Set-Content -LiteralPath (Join-Path $installPath 'Uninstall-BiliClass.cmd') -Encoding ASCII
if (-not $NoShortcuts) {
    # IShellLinkW keeps Vietnamese paths intact and updates owned taskbar pins.
    # This helper does not open the app or the teacher's library.
    $identityProcess = Start-Process -FilePath (Join-Path $versionPath 'BiliClass.exe') -ArgumentList @('--repair-shortcuts',('"' + $installPath + '"')) -WindowStyle Hidden -Wait -PassThru
    if ($identityProcess.ExitCode -ne 0) { throw 'Bản mới đã được lưu nhưng chưa cập nhật được biểu tượng. Chạy lại bộ cài vào đúng thư mục này để sửa, hoặc mở BiliClass.exe trong thư mục phiên bản mới.' }
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
    if ($WaitForProcessId -gt 0 -and (Get-Process -Id $WaitForProcessId -ErrorAction SilentlyContinue)) {
        Wait-Process -Id $WaitForProcessId -Timeout ([Math]::Max(1, [Math]::Min(120, $WaitForExitSeconds))) -ErrorAction SilentlyContinue
    }
    if ($WaitForProcessId -gt 0 -and (Get-Process -Id $WaitForProcessId -ErrorAction SilentlyContinue)) {
        Write-Output ('Installed successfully; previous process has not exited: ' + $WaitForProcessId)
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.MessageBox]::Show(('Đã cài BiliClass ' + $manifest.version + '.' + [Environment]::NewLine + 'Bản cũ chưa thoát hết. Đóng BiliClass cũ rồi mở từ biểu tượng Desktop/Start đã cập nhật.' + [Environment]::NewLine + 'Bản mới: ' + (Join-Path $versionPath 'BiliClass.exe')), 'Đã cập nhật BiliClass', [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information) | Out-Null
    } else {
        Start-Process -FilePath (Join-Path $versionPath 'BiliClass.exe') -WorkingDirectory $versionPath
    }
}
} finally {
    if ($archive) { $archive.Dispose() }
}
} catch {
    $updateFailure = $_
    if ($LaunchAfterInstall) {
        try {
            Add-Type -AssemblyName System.Windows.Forms
            $updateLog = Join-Path (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)) 'install.log'
            [System.Windows.Forms.MessageBox]::Show(('Chưa hoàn tất cập nhật BiliClass.' + [Environment]::NewLine + [Environment]::NewLine + $updateFailure.Exception.Message + [Environment]::NewLine + [Environment]::NewLine + 'Chi tiết: ' + $updateLog), 'Cập nhật BiliClass', [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning) | Out-Null
        } catch { }
    }
    throw $updateFailure
}
