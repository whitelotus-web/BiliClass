param([string]$DistRoot)
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
      --collect-data omegaconf --collect-submodules omegaconf --copy-metadata omegaconf `
      --collect-data antlr4 --collect-submodules antlr4 --copy-metadata antlr4-python3-runtime `
      --collect-data playwright --collect-binaries playwright --collect-submodules playwright --copy-metadata playwright `
      --hidden-import uvicorn.loops.auto --hidden-import uvicorn.protocols.http.h11_impl `
      --hidden-import uvicorn.protocols.websockets.websockets_sansio_impl --hidden-import uvicorn.lifespan.on `
      --exclude-module torch --exclude-module matplotlib --exclude-module jwt `
      --exclude-module gradio --exclude-module gradio_client `
      --exclude-module ctranslate2 --exclude-module sentencepiece --exclude-module rapidocr --exclude-module winrt `
      --exclude-module app.translation --exclude-module app.bulk_translation --exclude-module app.ocr `
      --exclude-module app.local_ocr --exclude-module app.model_packs --exclude-module biliclass_m0 `
      --collect-data sherpa_onnx --collect-binaries sherpa_onnx --collect-submodules sherpa_onnx `
      --copy-metadata sherpa-onnx --copy-metadata sherpa-onnx-core `
      --collect-data vieneu --collect-data sea_g2p --copy-metadata vieneu --copy-metadata sea-g2p `
      --hidden-import vieneu.v3turbo --hidden-import vieneu._v3_turbo_engine.onnx_runtime_lite `
      scripts/app_entry.py
    if ($LASTEXITCODE -ne 0) { throw 'Build failed.' }
    & (Join-Path $projectRoot 'scripts\finalize-build.ps1') -DistRoot $distPath
} finally { Pop-Location }
