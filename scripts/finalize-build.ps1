param([string]$DistRoot)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$distPath = if ($DistRoot) { [IO.Path]::GetFullPath($DistRoot) } else { Join-Path $projectRoot 'dist' }
if (-not $distPath.StartsWith(([IO.Path]::GetFullPath($projectRoot).TrimEnd('\') + '\'), [StringComparison]::OrdinalIgnoreCase)) { throw 'Build output must stay inside the project.' }
$bundlePath = Join-Path $distPath 'BiliClass'
$runtimeDest = Join-Path $bundlePath '_internal'
if (-not (Test-Path -LiteralPath (Join-Path $runtimeDest 'python312.dll'))) { throw 'Build the application first.' }
$kokoroSource = Join-Path $projectRoot '.runtime\kokoro\kokoro-multi-lang-v1_0'
$kokoroDest = Join-Path $bundlePath 'models\kokoro-multi-lang-v1_0'
foreach ($required in @('model.onnx','voices.bin','tokens.txt','lexicon-us-en.txt','espeak-ng-data\phontab','LICENSE')) {
    if (-not (Test-Path -LiteralPath (Join-Path $kokoroSource $required))) { throw ('Missing Kokoro model file: ' + $required) }
}
New-Item -ItemType Directory -Path $kokoroDest -Force | Out-Null
foreach ($name in @('model.onnx','voices.bin','tokens.txt','lexicon-us-en.txt','LICENSE','README.md')) {
    Copy-Item -LiteralPath (Join-Path $kokoroSource $name) -Destination (Join-Path $kokoroDest $name) -Force
}
Copy-Item -LiteralPath (Join-Path $kokoroSource 'espeak-ng-data') -Destination $kokoroDest -Recurse -Force
$vieneuSource = Join-Path $projectRoot '.runtime\vieneu-hf\hub'
$vieneuDest = Join-Path $bundlePath 'models\vieneu-hf\hub'
if (-not (Test-Path -LiteralPath (Join-Path $vieneuSource 'models--pnnbao-ump--VieNeu-TTS-v3-Turbo\refs\main'))) { throw 'Missing VieNeu model cache.' }
if (-not (Test-Path -LiteralPath (Join-Path $vieneuSource 'models--OpenMOSS-Team--MOSS-Audio-Tokenizer-Nano-ONNX\refs\main'))) { throw 'Missing VieNeu audio codec cache.' }
New-Item -ItemType Directory -Path $vieneuDest -Force | Out-Null
foreach ($cacheName in @('models--pnnbao-ump--VieNeu-TTS-v3-Turbo','models--OpenMOSS-Team--MOSS-Audio-Tokenizer-Nano-ONNX')) {
    Copy-Item -LiteralPath (Join-Path $vieneuSource $cacheName) -Destination $vieneuDest -Recurse -Force
}
Copy-Item -LiteralPath (Join-Path $projectRoot '.runtime\vieneu-hf\PROVENANCE.json') -Destination (Join-Path $bundlePath 'models\vieneu-hf\PROVENANCE.json') -Force
foreach ($runtimeName in @('vcruntime140.dll','vcruntime140_1.dll','msvcp140.dll','msvcp140_1.dll','msvcp140_2.dll','msvcp140_codecvt_ids.dll')) {
    Copy-Item -LiteralPath (Join-Path $projectRoot ('.venv\Lib\site-packages\PySide6\' + $runtimeName)) -Destination (Join-Path $runtimeDest $runtimeName) -Force
}
# Remove only a generated bundle artifact, never a Windows system library.
$foreignIcu = Join-Path $runtimeDest 'icuuc.dll'
if (Test-Path -LiteralPath $foreignIcu) { Remove-Item -LiteralPath $foreignIcu }
# Both Python VieNeu and sherpa-onnx use a DLL named onnxruntime.dll.
# PyInstaller may resolve sherpa's older copy first in a speech worker.
# Ship the installed Python runtime at both locations; validate both
# speech engines with the packaged self-test after finalization.
$onnxRuntimeSource = Join-Path $projectRoot '.venv\Lib\site-packages\onnxruntime\capi\onnxruntime.dll'
$sherpaRuntimeDest = Join-Path $runtimeDest 'sherpa_onnx\lib\onnxruntime.dll'
if (-not (Test-Path -LiteralPath $onnxRuntimeSource) -or -not (Test-Path -LiteralPath $sherpaRuntimeDest)) { throw 'Missing shared ONNX runtime in build.' }
Copy-Item -LiteralPath $onnxRuntimeSource -Destination $sherpaRuntimeDest -Force
Copy-Item -LiteralPath (Join-Path $projectRoot 'docs\THIRD_PARTY.md') -Destination (Join-Path $bundlePath 'THIRD_PARTY.md') -Force
$fontNotices = Join-Path $bundlePath 'licenses\Be-Vietnam-Pro'
New-Item -ItemType Directory -Path $fontNotices -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $projectRoot 'app\assets\OFL.txt') -Destination $fontNotices -Force
& (Join-Path $projectRoot '.venv\Scripts\python.exe') (Join-Path $projectRoot 'scripts\collect_licenses.py') $bundlePath
if ($LASTEXITCODE -ne 0) { throw 'License collection failed.' }
$ttsNotices = Join-Path $bundlePath 'licenses\Kokoro-TTS-stack'
New-Item -ItemType Directory -Path $ttsNotices -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $projectRoot 'docs\licenses\espeak-ng-COPYING.txt') -Destination $ttsNotices -Force
Copy-Item -LiteralPath (Join-Path $projectRoot 'docs\licenses\onnxruntime-LICENSE.txt') -Destination $ttsNotices -Force
Copy-Item -LiteralPath (Join-Path $projectRoot 'docs\licenses\onnxruntime-ThirdPartyNotices.txt') -Destination $ttsNotices -Force
