$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$env:BILICLASS_MODEL_DIR = Join-Path $projectRoot '.runtime\models'
Push-Location -LiteralPath $projectRoot
try {
    & .\.venv\Scripts\python.exe -m app @args
    exit $LASTEXITCODE
} finally { Pop-Location }
