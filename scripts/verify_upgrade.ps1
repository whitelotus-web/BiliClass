$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$runtimeRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot '.runtime')).TrimEnd('\') + '\'
$installRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot '.runtime\upgrade-validation'))
$dataRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot '.runtime\upgrade-validation-data'))
if (-not $installRoot.StartsWith($runtimeRoot, [StringComparison]::OrdinalIgnoreCase) -or -not $dataRoot.StartsWith($runtimeRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'Validation paths escaped the workspace.' }
if ((Test-Path -LiteralPath $installRoot) -or (Test-Path -LiteralPath $dataRoot)) { throw 'Upgrade validation paths already exist; inspect them before reusing.' }
$oldRelease = Join-Path $projectRoot 'dist'
$newRelease = Join-Path $projectRoot 'dist\rc2'
if (-not (Test-Path -LiteralPath (Join-Path $newRelease 'app-manifest.json'))) { throw 'Build and package RC2 first.' }
$previousData = $env:BILICLASS_DATA
$previousModels = $env:BILICLASS_MODEL_DIR
try {
    & (Join-Path $oldRelease 'Install-BiliClass.ps1') -InstallRoot $installRoot -NoShortcuts
    if (-not (Test-Path -LiteralPath (Join-Path $installRoot '1.0.0rc1\BiliClass.exe'))) { throw 'RC1 missing after installation.' }
    $env:BILICLASS_DATA = $dataRoot
    & (Join-Path $projectRoot '.venv\Scripts\python.exe') -c 'from app.library import Library; import os; x=Library(os.environ["BILICLASS_DATA"]); x.create("Preserved lesson", "Custom subject", "THPT", "12", [("Part", "VI source")]); x.close()'
    if ($LASTEXITCODE -ne 0) { throw 'Cannot seed the isolated user library.' }
    & (Join-Path $newRelease 'Install-BiliClass.ps1') -InstallRoot $installRoot -NoShortcuts
    $newExecutable = Join-Path $installRoot '1.0.0rc2\BiliClass.exe'
    if (-not (Test-Path -LiteralPath $newExecutable)) { throw 'RC2 missing after upgrade.' }
    $marker = Get-Content -LiteralPath (Join-Path $installRoot '.biliclass-install.json') -Raw | ConvertFrom-Json
    if ($marker.root -ne $installRoot -or $marker.product -ne 'BiliClass' -or $marker.version -ne '1.0.0rc2') { throw 'Upgraded installation marker is incorrect.' }
    $env:BILICLASS_MODEL_DIR = ''
    $shot = Join-Path $projectRoot 'reports\app\upgraded-settings.png'
    $probe = Start-Process -FilePath $newExecutable -ArgumentList @('--smoke','--page','settings','--size','1366x768','--screenshot',('"' + $shot + '"')) -WindowStyle Hidden -Wait -PassThru
    if ($probe.ExitCode -ne 0) { throw 'Upgraded app failed to open.' }
    & (Join-Path $projectRoot '.venv\Scripts\python.exe') -c 'from app.library import Library; import os; x=Library(os.environ["BILICLASS_DATA"]); assert any(v["title"] == "Preserved lesson" for v in x.list_lessons()); x.close()'
    if ($LASTEXITCODE -ne 0) { throw 'The user lesson did not survive the upgrade.' }
    # The install root is inside .runtime; its exact absolute path and BiliClass marker were verified above.
    & (Join-Path $newRelease 'Install-BiliClass.ps1') -InstallRoot $installRoot -NoShortcuts -Uninstall
    if (Test-Path -LiteralPath $installRoot) { throw 'Uninstaller left the application folder.' }
    & (Join-Path $projectRoot '.venv\Scripts\python.exe') -c 'from app.library import Library; import os; x=Library(os.environ["BILICLASS_DATA"]); assert any(v["title"] == "Preserved lesson" for v in x.list_lessons()); x.close()'
    if ($LASTEXITCODE -ne 0) { throw 'The user lesson did not survive uninstall.' }
    @{status='passed';versions=@('1.0.0rc1','1.0.0rc2');checks=@('RC1 installed from its signed-off manifest','RC2 installed alongside RC1 without replacing the lesson DB','upgraded executable opened','same lesson survived upgrade and uninstall');scope='same Windows development PC, isolated install and user library; not clean-Windows certification'} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $projectRoot 'reports\app\upgrade.json') -Encoding UTF8
} finally {
    $env:BILICLASS_DATA = $previousData
    $env:BILICLASS_MODEL_DIR = $previousModels
}
