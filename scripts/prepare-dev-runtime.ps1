param([switch]$CheckOnly)
$ErrorActionPreference = 'Stop'
# Use this shell's module when launched from a different PowerShell version.
Import-Module (Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Utility') -ErrorAction Stop
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$sitePackages = Join-Path $projectRoot '.venv\Lib\site-packages'
$lockHash = (Get-FileHash -LiteralPath (Join-Path $projectRoot 'requirements-lock.txt') -Algorithm SHA256).Hash
$venvHash = (Get-FileHash -LiteralPath (Join-Path $projectRoot '.venv\pyvenv.cfg') -Algorithm SHA256).Hash
$distributions = ((Get-ChildItem -LiteralPath $sitePackages -Directory -Filter '*.dist-info').Name | Sort-Object) -join '|'
$signatureText = $projectRoot + '|' + $lockHash + '|' + $venvHash + '|' + $distributions
$hasher = [Security.Cryptography.SHA256]::Create()
try { $signature = [BitConverter]::ToString($hasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($signatureText))).Replace('-','').ToLowerInvariant() }
finally { $hasher.Dispose() }
$cacheRoot = Join-Path $env:LOCALAPPDATA ('BiliClass\dev-runtime\source-' + $signature.Substring(0,16))
$readyFile = Join-Path $cacheRoot 'ready.json'
$essentialFiles = @('PySide6\QtCore.pyd','PySide6\plugins\platforms\qwindows.dll','shiboken6\__init__.py','pydantic\__init__.py','typing_extensions.py','jwt\__init__.py','cryptography\__init__.py')
$complete = @($essentialFiles | Where-Object { -not (Test-Path -LiteralPath (Join-Path $cacheRoot $_)) }).Count -eq 0
if ($complete -and (Test-Path -LiteralPath $readyFile)) {
    try { $ready = Get-Content -LiteralPath $readyFile -Raw | ConvertFrom-Json }
    catch { $ready = $null }
    if ($ready -and $ready.signature -eq $signature) { Write-Output $cacheRoot; exit 0 }
}
if ($CheckOnly) { exit 0 }

New-Item -ItemType Directory -Force -Path $cacheRoot | Out-Null
# Cache only libraries used at startup. Models and the teacher library stay in their existing folders.
$packages = @('PySide6','shiboken6','pydantic','pydantic_core','psutil','annotated_types','typing_inspection',
              'fastapi','starlette','httpx','httpcore','h11','anyio','sniffio','uvicorn','click','certifi',
              'annotated_doc','jwt','cryptography','win32','win32com','win32comext','pywin32_system32','playwright','pyee','greenlet')
foreach ($packageName in $packages) {
    $source = Join-Path $sitePackages $packageName
    if (-not (Test-Path -LiteralPath $source)) { continue }
    & robocopy $source (Join-Path $cacheRoot $packageName) /E /MT:8 /R:1 /W:1 /NFL /NDL /NJH /NJS /NP /XD '__pycache__' 'include' 'glue' 'typesystems' 'examples' 'scripts' 'doc' 'metatypes' 'translations' | Out-Null
    if ($LASTEXITCODE -ge 8 -or $LASTEXITCODE -lt 0) { throw "Runtime copy failed for $packageName. Run this script again to retry." }
}
foreach ($fileName in @('typing_extensions.py','pythoncom.py','pywintypes.py')) {
    $source = Join-Path $sitePackages $fileName
    if (Test-Path -LiteralPath $source) { Copy-Item -LiteralPath $source -Destination $cacheRoot -Force }
}
# A partial cache is never enabled by run.ps1.
foreach ($fileName in $essentialFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $cacheRoot $fileName))) { throw "Runtime cache is missing $fileName. Run this script again to retry." }
}
@{signature=$signature; project=$projectRoot; created=(Get-Date).ToString('o')} |
    ConvertTo-Json | Set-Content -LiteralPath $readyFile -Encoding utf8
Write-Output $cacheRoot
