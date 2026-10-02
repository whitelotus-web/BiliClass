$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Push-Location -LiteralPath $projectRoot
try {
    & .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --onedir `
      --name BiliClass-M0 --paths . `
      --add-data 'biliclass_m0/qml;biliclass_m0/qml' `
      --add-data 'biliclass_m0/assets;biliclass_m0/assets' `
      --hidden-import biliclass_m0.probes.system --hidden-import biliclass_m0.probes.tts `
      --hidden-import biliclass_m0.probes.powerpoint --hidden-import biliclass_m0.probes.lan `
      --hidden-import biliclass_m0.probes.translation --hidden-import uvicorn.logging `
      --hidden-import uvicorn.loops.auto --hidden-import uvicorn.protocols.http.h11_impl `
      --hidden-import uvicorn.protocols.websockets.websockets_sansio_impl `
      --hidden-import uvicorn.lifespan.on --collect-data ctranslate2 `
      scripts/package_entry.py
    if ($LASTEXITCODE -ne 0) { throw 'Build failed.' }
    # Python's bundled VC runtime is older than Qt's. Use the matching Qt runtime
    # at the application DLL root; never modify Windows system DLLs.
    $runtimeDest = Join-Path $projectRoot 'dist\BiliClass-M0\_internal'
    foreach ($runtimeName in @('vcruntime140.dll','vcruntime140_1.dll','msvcp140.dll','msvcp140_1.dll','msvcp140_2.dll','msvcp140_codecvt_ids.dll')) {
        Copy-Item -LiteralPath (Join-Path $projectRoot ('.venv\Lib\site-packages\PySide6\' + $runtimeName)) -Destination (Join-Path $runtimeDest $runtimeName) -Force
    }
    # Qt 6.11 uses Windows' ICU API. A Poppler directory on PATH can cause
    # PyInstaller to collect an incompatible ICU with the same filename.
    $foreignIcu = Join-Path $runtimeDest 'icuuc.dll'
    if (Test-Path -LiteralPath $foreignIcu) { Remove-Item -LiteralPath $foreignIcu }
} finally {
    Pop-Location
}
