param([Parameter(Mandatory=$true)][string]$DistRoot)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$distPath = [IO.Path]::GetFullPath($DistRoot)
if (-not $distPath.StartsWith(([IO.Path]::GetFullPath($projectRoot).TrimEnd('\') + '\'), [StringComparison]::OrdinalIgnoreCase)) { throw 'Release must stay inside the project.' }
$manifest = Get-Content -LiteralPath (Join-Path $distPath 'app-manifest.json') -Raw | ConvertFrom-Json
if ($manifest.product -ne 'BiliClass' -or $manifest.version -notmatch '^\d+\.\d+\.\d+(?:rc\d+)?$') { throw 'Invalid release manifest.' }
$runId = $manifest.version + '-' + [Guid]::NewGuid().ToString('N').Substring(0,8)
$installRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot ('.runtime\install-validation-' + $runId)))
$dataRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot ('.runtime\release-data-' + $runId)))
$runtimeRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot '.runtime')) + '\'
if (-not $installRoot.StartsWith($runtimeRoot, [StringComparison]::OrdinalIgnoreCase) -or -not $dataRoot.StartsWith($runtimeRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'Test paths escaped workspace.' }
$reportRoot = Join-Path $projectRoot ('reports\release\' + $runId)
New-Item -ItemType Directory -Path $reportRoot -Force | Out-Null
$savedEnvironment = @{}
foreach ($name in @('BILICLASS_DATA','BILICLASS_MODEL_DIR','BILICLASS_KOKORO_DIR','BILICLASS_VIENEU_DIR','BILICLASS_EXPERIMENTAL_TEACHING','PYTHONPATH','PYTHONHOME','QT_QPA_PLATFORM')) {
    $savedEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
    [Environment]::SetEnvironmentVariable($name, $null, 'Process')
}
function Invoke-InstalledCheck([string[]]$Arguments, [int]$TimeoutSeconds = 300) {
    $probe = Start-Process -FilePath $executable -ArgumentList $Arguments -WorkingDirectory $versionPath -WindowStyle Hidden -PassThru
    if (-not $probe.WaitForExit($TimeoutSeconds * 1000)) {
        Stop-Process -Id $probe.Id -Force
        throw ('Installed check timed out: ' + ($Arguments -join ' '))
    }
    $probe.Refresh()
    if ($probe.ExitCode -ne 0) { throw ('Installed check failed: ' + ($Arguments -join ' ')) }
}
try {
    if ($env:OS -eq 'Windows_NT') { $env:QT_QPA_PLATFORM = 'windows' }
    Write-Output ('Verifying ' + $manifest.version + ': installing into an isolated Unicode path...')
    & (Join-Path $distPath 'Install-BiliClass.ps1') -InstallRoot $installRoot -NoShortcuts
    $env:BILICLASS_DATA = $dataRoot
    $versionPath = Join-Path $installRoot $manifest.version
    $executable = Join-Path $versionPath 'BiliClass.exe'
    $taskDetails = [Diagnostics.FileVersionInfo]::GetVersionInfo($executable)
    if ($taskDetails.ProductName -ne 'BiliClass' -or $taskDetails.ProductVersion -ne $manifest.version -or $taskDetails.LegalCopyright -notlike '*Nguyễn Diệu Linh*') { throw 'Installed Windows Details resource failed validation.' }
    Write-Output 'Passed Windows Properties product, version and copyright.'
    $taskShortcutReport = Join-Path $reportRoot 'shortcuts.json'
    Invoke-InstalledCheck -Arguments @('--check-shortcuts',('"' + $taskShortcutReport + '"'))
    $taskShortcutResult = Get-Content -LiteralPath $taskShortcutReport -Raw | ConvertFrom-Json
    if ($taskShortcutResult.status -ne 'passed') { throw 'Installed Unicode shortcut/pin repair failed validation.' }
    Write-Output 'Passed installed Unicode Desktop/Start/taskbar shortcut repair without modifying user shortcuts.'
    foreach ($page in @('new','word','browser-ai','settings','classroom')) {
        $shot = Join-Path $reportRoot ($page + '.png')
        Invoke-InstalledCheck -Arguments @('--smoke','--page',$page,'--size','1366x850','--screenshot',('"' + $shot + '"'))
        if (-not (Test-Path -LiteralPath $shot)) { throw ('Missing screenshot: ' + $page) }
        $taskPageState = Get-Content -LiteralPath ([IO.Path]::ChangeExtension($shot, '.json')) -Raw | ConvertFrom-Json
        if ($taskPageState.experimental_teaching -ne $false) { throw 'Packaged UI must default to submission scope.' }
        if ($page -eq 'classroom' -and $taskPageState.current_page -ne 'home') { throw 'Classroom startup route was not hidden.' }
        Write-Output ('Passed installed Qt page: ' + $page)
    }
    $report = Join-Path $reportRoot 'pipeline.json'
    Invoke-InstalledCheck -Arguments @('--self-test',('"' + $report + '"')) -TimeoutSeconds 900
    $pipeline = Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
    if ($pipeline.status -ne 'passed' -or $pipeline.tts.provider -ne 'kokoro' -or $pipeline.tts_vi.provider -ne 'vieneu' -or $pipeline.tts.voice -eq $pipeline.tts_vi.voice) { throw ('Incomplete installed pipeline: ' + $report) }
    Write-Output 'Passed bundled templates, independent Vietnamese-US speakers, classroom process and lesson backup.'
    $taskNarration = Join-Path $reportRoot 'narration-ui.json'
    Invoke-InstalledCheck -Arguments @('--check-narration-ui',('"' + $taskNarration + '"')) -TimeoutSeconds 360
    $taskVoiceResult = Get-Content -LiteralPath $taskNarration -Raw | ConvertFrom-Json
    if ($taskVoiceResult.status -ne 'passed' -or -not $taskVoiceResult.watchdog_enabled -or $taskVoiceResult.complete -ne 2) { throw 'Installed Qt narration transition failed.' }
    Write-Output 'Passed installed Qt completion to real bilingual voice, with safe stall logging enabled.'
    $marker = Get-Content -LiteralPath (Join-Path $installRoot '.biliclass-install.json') -Raw | ConvertFrom-Json
    if ($marker.root -ne $installRoot -or $marker.product -ne 'BiliClass' -or $marker.version -ne $manifest.version) { throw 'Installation marker failed validation.' }
    $buildInfo = Get-Content -LiteralPath (Join-Path $versionPath 'BUILD_INFO.json') -Raw | ConvertFrom-Json
    # Only remove this isolated installation after its absolute workspace path and marker were checked.
    & (Join-Path $distPath 'Install-BiliClass.ps1') -InstallRoot $installRoot -NoShortcuts -Uninstall
    if ((Test-Path -LiteralPath $installRoot) -or -not (Test-Path -LiteralPath (Join-Path $dataRoot 'library.db'))) { throw 'Uninstall did not preserve the separate test library.' }
    @{status='passed';version=$manifest.version;source_commit=$buildInfo.source_commit;
      checks=@('manifest verified install in Unicode workspace','installed Qt conversion and Browser AI pages',
               'all templates/previews and independent Vietnamese-US voices without development cache',
               'spawned classroom process and library backup','installed Qt completion to real bilingual narration with watchdog',
               'uninstall preserves separate lesson library');
      scope='current Windows machine; isolated install/data; no shortcuts; not a clean-Windows certification'} |
      ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $reportRoot 'installer.json') -Encoding UTF8
    Write-Output ('Release verification passed: ' + $reportRoot)
} finally {
    foreach ($name in $savedEnvironment.Keys) { [Environment]::SetEnvironmentVariable($name, $savedEnvironment[$name], 'Process') }
}
