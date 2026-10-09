param([switch]$CheckOnly)
$ErrorActionPreference = 'Stop'
# Use this shell's module when launched from a different PowerShell version.
Import-Module (Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Utility') -ErrorAction Stop
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$sitePackages = Join-Path $projectRoot '.venv\Lib\site-packages'
$lockHash = (Get-FileHash -LiteralPath (Join-Path $projectRoot 'requirements-lock.txt') -Algorithm SHA256).Hash
$venvHash = (Get-FileHash -LiteralPath (Join-Path $projectRoot '.venv\pyvenv.cfg') -Algorithm SHA256).Hash
$distributions = ((Get-ChildItem -LiteralPath $sitePackages -Directory -Filter '*.dist-info').Name | Sort-Object) -join '|'
$signatureText = $projectRoot + '|speech-cache-v2|' + $lockHash + '|' + $venvHash + '|' + $distributions
$hasher = [Security.Cryptography.SHA256]::Create()
try { $signature = [BitConverter]::ToString($hasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($signatureText))).Replace('-','').ToLowerInvariant() }
finally { $hasher.Dispose() }
$cacheRoot = Join-Path $env:LOCALAPPDATA ('BiliClass\dev-runtime\source-' + $signature.Substring(0,16))
$readyFile = Join-Path $cacheRoot 'ready.json'
$metadataReadyFile = Join-Path $cacheRoot 'metadata-ready.json'
function Copy-DependencyMetadata {
    $llvmShared = Join-Path $sitePackages 'llvmlite.libs'
    $llvmReady = Join-Path $cacheRoot 'llvm-dependencies-ready.json'
    if ((Test-Path -LiteralPath $llvmShared) -and -not (Test-Path -LiteralPath $llvmReady)) {
        & robocopy $llvmShared (Join-Path $cacheRoot 'llvmlite.libs') /E /MT:4 /R:1 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
        if ($LASTEXITCODE -ge 8 -or $LASTEXITCODE -lt 0) { throw 'LLVM dependency cache failed.' }
        @{signature=$signature; created=(Get-Date).ToString('o')} |
            ConvertTo-Json | Set-Content -LiteralPath $llvmReady -Encoding utf8
    }
    $zonesReady = Join-Path $cacheRoot 'timezone-data-ready.json'
    if (-not (Test-Path -LiteralPath $zonesReady)) {
        foreach ($namespace in @('pytz','tzdata')) {
            $namespaceSource = Join-Path $sitePackages $namespace
            if (-not (Test-Path -LiteralPath $namespaceSource)) { continue }
            & robocopy $namespaceSource (Join-Path $cacheRoot $namespace) /E /MT:8 /R:1 /W:1 /NFL /NDL /NJH /NJS /NP /XD '__pycache__' | Out-Null
            if ($LASTEXITCODE -ge 8 -or $LASTEXITCODE -lt 0) { throw ('Timezone data cache failed: ' + $namespace) }
        }
        @{signature=$signature; created=(Get-Date).ToString('o')} |
            ConvertTo-Json | Set-Content -LiteralPath $zonesReady -Encoding utf8
    }
    if (Test-Path -LiteralPath $metadataReadyFile) { return }
    foreach ($metadata in (Get-ChildItem -LiteralPath $sitePackages -Directory -Filter '*.dist-info')) {
        & robocopy $metadata.FullName (Join-Path $cacheRoot $metadata.Name) /E /MT:4 /R:1 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
        if ($LASTEXITCODE -ge 8 -or $LASTEXITCODE -lt 0) { throw ('Dependency metadata copy failed: ' + $metadata.Name) }
    }
    @{signature=$signature; created=(Get-Date).ToString('o')} |
        ConvertTo-Json | Set-Content -LiteralPath $metadataReadyFile -Encoding utf8
}
$essentialFiles = @('PySide6\QtCore.pyd','PySide6\plugins\platforms\qwindows.dll','shiboken6\__init__.py','pydantic\__init__.py','typing_extensions.py','numpy\__init__.py','vieneu\__init__.py','vieneu_utils\__init__.py','onnxruntime\__init__.py','librosa\__init__.py')
$complete = @($essentialFiles | Where-Object { -not (Test-Path -LiteralPath (Join-Path $cacheRoot $_)) }).Count -eq 0
if ($complete -and (Test-Path -LiteralPath $readyFile)) {
    try { $ready = Get-Content -LiteralPath $readyFile -Raw | ConvertFrom-Json }
    catch { $ready = $null }
    if ($ready -and $ready.signature -eq $signature) {
        if (-not $CheckOnly) { Copy-DependencyMetadata }
        Write-Output $cacheRoot; exit 0
    }
}
if ($CheckOnly) { exit 0 }

New-Item -ItemType Directory -Force -Path $cacheRoot | Out-Null
# Cache only libraries used at startup. Models and the teacher library stay in their existing folders.
$packages = @('PySide6','shiboken6','pydantic','pydantic_core','psutil','annotated_types','typing_inspection',
              'fastapi','starlette','httpx','httpcore','h11','anyio','sniffio','uvicorn','click','certifi',
              'annotated_doc','cryptography','win32','win32com','win32comext','pywin32_system32','playwright','pyee','greenlet',
              'numpy','numpy.libs','scipy','scipy.libs','vieneu','vieneu_utils','onnxruntime','sherpa_onnx','huggingface_hub',
              'tokenizers','safetensors','sea_g2p','librosa','numba','llvmlite','llvmlite.libs','soundfile','_soundfile_data',
              'nltk','regex','joblib','soxr','lazy_loader','audioread','pooch','platformdirs','tqdm','filelock',
              'packaging','yaml','fsspec','requests','urllib3','charset_normalizer','idna','omegaconf','antlr4',
              'pandas','pandas.libs','sklearn','sklearn.libs','threadpoolctl','sounddevice','_sounddevice_data',
              'cffi','pycparser','einops','dill','unidecode','inflect','num2words','wcwidth','rich','pygments',
              'PIL','pptx','docx','lxml','pypdf','qrcode','typing_extensions')
foreach ($packageName in $packages) {
    $source = Join-Path $sitePackages $packageName
    if (-not (Test-Path -LiteralPath $source)) { continue }
    & robocopy $source (Join-Path $cacheRoot $packageName) /E /MT:8 /R:1 /W:1 /NFL /NDL /NJH /NJS /NP /XD '__pycache__' 'include' 'glue' 'typesystems' 'examples' 'scripts' 'doc' 'metatypes' 'translations' | Out-Null
    if ($LASTEXITCODE -ge 8 -or $LASTEXITCODE -lt 0) { throw "Runtime copy failed for $packageName. Run this script again to retry." }
}
foreach ($fileName in @('typing_extensions.py','pythoncom.py','pywintypes.py','_cffi_backend.cp312-win_amd64.pyd','soundfile.py','sounddevice.py','decorator.py','six.py','docopt.py')) {
    $source = Join-Path $sitePackages $fileName
    if (Test-Path -LiteralPath $source) { Copy-Item -LiteralPath $source -Destination $cacheRoot -Force }
}
# A partial cache is never enabled by run.ps1.
foreach ($fileName in $essentialFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $cacheRoot $fileName))) { throw "Runtime cache is missing $fileName. Run this script again to retry." }
}
Copy-DependencyMetadata
@{signature=$signature; project=$projectRoot; created=(Get-Date).ToString('o')} |
    ConvertTo-Json | Set-Content -LiteralPath $readyFile -Encoding utf8
Write-Output $cacheRoot
