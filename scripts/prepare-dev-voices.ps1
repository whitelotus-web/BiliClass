$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$sourcePath = Join-Path $projectRoot '.runtime\vieneu-hf'
$provenancePath = Join-Path $sourcePath 'PROVENANCE.json'
if (-not (Test-Path -LiteralPath $provenancePath)) { throw 'Prepare the local VieNeu model pack first.' }
$provenanceHash = (Get-FileHash -LiteralPath $provenancePath -Algorithm SHA256).Hash.ToLowerInvariant()
$cachePath = Join-Path $env:LOCALAPPDATA ('BiliClass\dev-runtime\voices-' + $provenanceHash.Substring(0,16))
$readyPath = Join-Path $cachePath 'ready.json'
$kokoroSource = Join-Path $projectRoot '.runtime\kokoro\kokoro-multi-lang-v1_0'
$kokoroCache = Join-Path $cachePath 'kokoro-multi-lang-v1_0'
if (-not (Test-Path -LiteralPath (Join-Path $kokoroSource 'model.onnx'))) { throw 'Prepare the local Kokoro model pack first.' }
if (Test-Path -LiteralPath $readyPath) {
    $ready = Get-Content -LiteralPath $readyPath -Raw | ConvertFrom-Json
    if ($ready.provenance -eq $provenanceHash -and $ready.kokoro -eq 'kokoro-v1_0-sherpa-1.13.8' -and (Test-Path -LiteralPath (Join-Path $kokoroCache 'model.onnx'))) { Write-Output $cachePath; exit 0 }
}
New-Item -ItemType Directory -Path $cachePath -Force | Out-Null
# Copy local model files once to the Windows user disk. No downloads, no
# teacher data, and no moves/deletions of the original model cache.
& robocopy $sourcePath $cachePath /E /MT:4 /R:1 /W:1 /NFL /NDL /NJH /NJS /NP /XD '.locks' | Out-Null
if ($LASTEXITCODE -ge 8 -or $LASTEXITCODE -lt 0) { throw 'Voice cache copy failed. Retry this script.' }
$copiedHash = (Get-FileHash -LiteralPath (Join-Path $cachePath 'PROVENANCE.json') -Algorithm SHA256).Hash.ToLowerInvariant()
if ($copiedHash -ne $provenanceHash) { throw 'Voice model provenance changed during copying.' }
& robocopy $kokoroSource $kokoroCache /E /MT:4 /R:1 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8 -or $LASTEXITCODE -lt 0) { throw 'English voice cache copy failed. Retry this script.' }
$env:BILICLASS_VIENEU_DIR = $cachePath
$env:BILICLASS_KOKORO_DIR = $kokoroCache
Push-Location -LiteralPath $projectRoot
try {
    & .\.venv\Scripts\python.exe -c 'from app.speech import vieneu_ready, kokoro_ready; assert vieneu_ready() and kokoro_ready(), "Incomplete local voice cache"'
    if ($LASTEXITCODE -ne 0) { throw 'Voice cache is incomplete.' }
} finally { Pop-Location }
@{provenance=$provenanceHash; kokoro='kokoro-v1_0-sherpa-1.13.8'; source=$sourcePath; created=(Get-Date).ToString('o')} |
    ConvertTo-Json | Set-Content -LiteralPath $readyPath -Encoding utf8
Write-Output $cachePath
