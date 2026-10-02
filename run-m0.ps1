$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
& (Join-Path $projectRoot '.venv\Scripts\python.exe') -X utf8 -m biliclass_m0
exit $LASTEXITCODE
