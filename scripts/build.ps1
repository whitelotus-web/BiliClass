param([switch]$IncludeTrialModel, [string]$DistRoot)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$distPath = if ($DistRoot) { [IO.Path]::GetFullPath($DistRoot) } else { Join-Path $projectRoot 'dist' }
if (-not $distPath.StartsWith(([IO.Path]::GetFullPath($projectRoot).TrimEnd('\') + '\'), [StringComparison]::OrdinalIgnoreCase)) { throw 'Build output must stay inside the project.' }
Push-Location -LiteralPath $projectRoot
try {
    & .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --windowed --onedir `
      --name BiliClass --distpath $distPath --paths . `
      --add-data 'app/qml;app/qml' `
      --add-data 'app/assets;app/assets' `
      --add-data 'app/student_web;app/student_web' `
      --add-data 'biliclass_m0/assets;biliclass_m0/assets' `
      --collect-submodules winrt --collect-all pypdfium2 --collect-all pypdfium2_raw `
      --collect-all rapidocr --collect-all omegaconf --collect-all antlr4 `
      --collect-all playwright `
      --hidden-import uvicorn.loops.auto --hidden-import uvicorn.protocols.http.h11_impl `
      --hidden-import uvicorn.protocols.websockets.websockets_sansio_impl --hidden-import uvicorn.lifespan.on `
      --collect-data ctranslate2 --exclude-module torch --exclude-module matplotlib `
      --collect-all sherpa_onnx --collect-data vieneu --collect-data sea_g2p `
      --hidden-import vieneu.v3turbo --hidden-import vieneu._v3_turbo_engine.onnx_runtime_lite `
      scripts/app_entry.py
    if ($LASTEXITCODE -ne 0) { throw 'Build failed.' }
    & (Join-Path $projectRoot 'scripts\finalize-build.ps1') -IncludeTrialModel:$IncludeTrialModel -DistRoot $distPath
} finally { Pop-Location }
