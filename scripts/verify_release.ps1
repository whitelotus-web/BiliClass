$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$installRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot '.runtime\install-validation'))
$dataRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot '.runtime\release-validation-data'))
$runtimeRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot '.runtime')) + '\'
if (-not $installRoot.StartsWith($runtimeRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'Test install path escaped workspace.' }
if (Test-Path -LiteralPath $installRoot) { throw 'Validation directory already exists; inspect it before another run.' }
$previousData = $env:BILICLASS_DATA
$previousModels = $env:BILICLASS_MODEL_DIR
try {
    & (Join-Path $projectRoot 'dist\Install-BiliClass.ps1') -InstallRoot $installRoot -NoShortcuts
    $env:BILICLASS_DATA = $dataRoot
    $env:BILICLASS_MODEL_DIR = ''
    $executable = Join-Path $installRoot '1.0.0rc1\BiliClass.exe'
    $shot = Join-Path $projectRoot 'reports\app\installed-no-model.png'
    $probe = Start-Process -FilePath $executable -ArgumentList @('--smoke','--page','settings','--size','1366x768','--screenshot',('"' + $shot + '"')) -WindowStyle Hidden -Wait -PassThru
    if ($probe.ExitCode -ne 0) { throw 'Installed app failed without optional model packs.' }
    & (Join-Path $projectRoot '.venv\Scripts\python.exe') -m scripts.verify_model_packs
    if ($LASTEXITCODE -ne 0) { throw 'Optional model installation failed.' }
    $report = Join-Path $projectRoot 'reports\app\installed-v1-pipeline.json'
    $probe = Start-Process -FilePath $executable -ArgumentList @('--self-test',('"' + $report + '"')) -WindowStyle Hidden -Wait -PassThru
    if ($probe.ExitCode -ne 0) { throw 'Installed pipeline failed.' }
    $marker = Get-Content -LiteralPath (Join-Path $installRoot '.biliclass-install.json') -Raw | ConvertFrom-Json
    if ($marker.root -ne $installRoot -or $marker.product -ne 'BiliClass') { throw 'Installation marker failed validation.' }
    # Explicit workspace target and its product marker checked before recursive uninstall.
    & (Join-Path $projectRoot 'dist\Install-BiliClass.ps1') -InstallRoot $installRoot -NoShortcuts -Uninstall
    if ((Test-Path -LiteralPath $installRoot) -or -not (Test-Path -LiteralPath (Join-Path $dataRoot 'library.db'))) { throw 'Uninstall did not preserve the separate test library.' }
    @{status='passed';checks=@('manifest verified install in Unicode workspace','native settings without optional models','both real model packs installed offline','installed executable full pipeline','uninstall preserves separate lesson library');scope='current Windows machine, isolated install and library, no shortcuts'} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $projectRoot 'reports\app\installer.json') -Encoding UTF8
} finally {
    $env:BILICLASS_DATA = $previousData
    $env:BILICLASS_MODEL_DIR = $previousModels
}
