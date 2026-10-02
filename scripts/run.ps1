$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$env:BILICLASS_MODEL_DIR = Join-Path $projectRoot '.runtime\models'
$runtimeCache = & (Join-Path $projectRoot 'scripts\prepare-dev-runtime.ps1') -CheckOnly
if ($runtimeCache) {
    $cachedPaths = @($runtimeCache, (Join-Path $runtimeCache 'win32'), (Join-Path $runtimeCache 'win32\lib'), (Join-Path $runtimeCache 'pywin32_system32'))
    if ($env:PYTHONPATH) { $cachedPaths += $env:PYTHONPATH }
    $env:PYTHONPATH = $cachedPaths -join [IO.Path]::PathSeparator
}
Push-Location -LiteralPath $projectRoot
try {
    & .\.venv\Scripts\python.exe -m app @args
    exit $LASTEXITCODE
} finally { Pop-Location }
