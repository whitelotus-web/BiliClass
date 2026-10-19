param([string]$DistRoot)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$distPath = if ($DistRoot) { [IO.Path]::GetFullPath($DistRoot) } else { Join-Path $projectRoot 'dist' }
if (-not $distPath.StartsWith(([IO.Path]::GetFullPath($projectRoot).TrimEnd('\') + '\'), [StringComparison]::OrdinalIgnoreCase)) { throw 'Build output must stay inside the project.' }
$bundlePath = Join-Path $distPath 'BiliClass'
$runtimeDest = Join-Path $bundlePath '_internal'
if (-not (Test-Path -LiteralPath (Join-Path $runtimeDest 'python312.dll'))) { throw 'Build the application first.' }
$taskEnglishSource = Join-Path $projectRoot '.runtime\kokoro\kokoro-multi-lang-v1_0'
if (-not (Test-Path -LiteralPath (Join-Path $taskEnglishSource 'model.onnx'))) { throw 'Missing offline US English model.' }
New-Item -ItemType Directory -Path (Join-Path $bundlePath 'models') -Force | Out-Null
Copy-Item -LiteralPath $taskEnglishSource -Destination (Join-Path $bundlePath 'models') -Recurse -Force
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
# Recent llvmlite loads its DLL from the binding package's resource path.
# PyInstaller's hook can collect the same DLL at the bundle root instead.
$llvmSource = Join-Path $projectRoot '.venv\Lib\site-packages\llvmlite\binding\llvmlite.dll'
$llvmDest = Join-Path $runtimeDest 'llvmlite\binding'
if (-not (Test-Path -LiteralPath $llvmSource)) { throw 'Missing llvmlite runtime for VieNeu SDK audio utilities.' }
New-Item -ItemType Directory -Path $llvmDest -Force | Out-Null
Copy-Item -LiteralPath $llvmSource -Destination $llvmDest -Force
$llvmSharedSource = Join-Path $projectRoot '.venv\Lib\site-packages\llvmlite.libs'
if (Test-Path -LiteralPath $llvmSharedSource) {
    Copy-Item -LiteralPath $llvmSharedSource -Destination $runtimeDest -Recurse -Force
}
Copy-Item -LiteralPath (Join-Path $projectRoot 'docs\licenses') -Destination $bundlePath -Recurse -Force
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
