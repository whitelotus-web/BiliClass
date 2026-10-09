$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$env:BILICLASS_MODEL_DIR = Join-Path $projectRoot '.runtime\models'
$runtimeCache = & (Join-Path $projectRoot 'scripts\prepare-dev-runtime.ps1') -CheckOnly
if ($runtimeCache) {
    $cachedPaths = @($runtimeCache, (Join-Path $runtimeCache 'win32'), (Join-Path $runtimeCache 'win32\lib'), (Join-Path $runtimeCache 'pywin32_system32'))
    if ($env:PYTHONPATH) { $cachedPaths += $env:PYTHONPATH }
    $env:PYTHONPATH = $cachedPaths -join [IO.Path]::PathSeparator
}
$voiceProvenance = Join-Path $projectRoot '.runtime\vieneu-hf\PROVENANCE.json'
if (-not $env:BILICLASS_VIENEU_DIR -and (Test-Path -LiteralPath $voiceProvenance)) {
    $voiceHash = (Get-FileHash -LiteralPath $voiceProvenance -Algorithm SHA256).Hash.ToLowerInvariant()
    $voiceCache = Join-Path $env:LOCALAPPDATA ('BiliClass\dev-runtime\voices-' + $voiceHash.Substring(0,16))
    if (Test-Path -LiteralPath (Join-Path $voiceCache 'ready.json')) {
        $env:BILICLASS_VIENEU_DIR = $voiceCache
        $kokoroCache = Join-Path $voiceCache 'kokoro-multi-lang-v1_0'
        if (-not $env:BILICLASS_KOKORO_DIR -and (Test-Path -LiteralPath (Join-Path $kokoroCache 'model.onnx'))) { $env:BILICLASS_KOKORO_DIR = $kokoroCache }
    }
}
Push-Location -LiteralPath $projectRoot
try {
    & .\.venv\Scripts\python.exe -m app @args
    exit $LASTEXITCODE
} finally { Pop-Location }
