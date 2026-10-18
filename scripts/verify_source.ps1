param([switch]$Qt, [switch]$Office, [switch]$Quick)
$ErrorActionPreference = 'Stop'
$taskProject = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskProject
$taskPython = Join-Path $taskProject '.venv/Scripts/python.exe'
$taskRuff = Join-Path $taskProject '.venv/Scripts/ruff.exe'
if (-not (Test-Path -LiteralPath $taskPython)) { throw 'Create the project .venv and install .[dev] first.' }
$env:PYTHONUTF8 = '1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
$env:PYDANTIC_DISABLE_PLUGINS = '__all__'
$taskReport = Join-Path $taskProject ('reports/verification/' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $taskReport -Force | Out-Null
$taskChecks = [System.Collections.Generic.List[string]]::new()
function Invoke-Check([string]$Name, [string]$Program, [string[]]$Parameters) {
    Write-Output ('Checking ' + $Name + '...')
    & $Program @Parameters *> (Join-Path $taskReport ($Name + '.log'))
    if ($LASTEXITCODE -ne 0) { throw ('Failed ' + $Name + '; inspect ' + $taskReport) }
    $taskChecks.Add($Name)
}
Invoke-Check 'lint-source' $taskRuff @('check', 'app', 'scripts', 'tests')
Invoke-Check 'compile' $taskPython @('-m', 'compileall', '-q', 'app', 'scripts')
$taskTests = @('-m', 'pytest', '-vv', '-o', 'faulthandler_timeout=90', '--tb=short')
if ($Quick) {
    $taskTests += @('tests/test_backup_safety.py', 'tests/test_library_location.py',
        'tests/test_narration_workspace.py', 'tests/test_narration_preparation.py',
        'tests/test_office_tasks.py', 'tests/test_support_report.py', 'tests/test_slide_dependency_cache.py')
    Invoke-Check 'pytest-quick' $taskPython $taskTests
} else {
    # Each browser group gets a fresh driver/event loop. A monolithic Windows
    # run stalled after many Chrome restarts; isolated groups remain measurable.
    Invoke-Check 'pytest-core' $taskPython ($taskTests + @('--ignore=tests/test_browser_ai.py', '--ignore=tests/test_browser_translation.py'))
    Invoke-Check 'pytest-browser-ai' $taskPython ($taskTests + @('tests/test_browser_ai.py'))
    Invoke-Check 'pytest-browser-translation' $taskPython ($taskTests + @('tests/test_browser_translation.py'))
}
if ($Qt) {
    foreach ($taskFlow in @('qt_conversion_layout_smoke', 'qt_narration_workspace_smoke',
        'qt_save_dialog_smoke', 'qt_result_preview_mascot_smoke',
        'qt_storage_voice_smoke', 'qt_home_smoke', 'qt_library_views_smoke',
        'qt_teaching_session_smoke', 'qt_classroom_flow_smoke', 'qt_conversion_responsiveness_smoke')) {
        Invoke-Check $taskFlow $taskPython @('-m', ('scripts.' + $taskFlow))
    }
}
# Office integration is deliberately sequential, after unit/Qt checks.
if ($Office) { Invoke-Check 'quality-corpus-native' $taskPython @('-m', 'scripts.verify_quality_corpus', '--native') }
@{ status='passed'; checks=$taskChecks; quick=[bool]$Quick; qt=[bool]$Qt; office=[bool]$Office;
    commit=(git rev-parse HEAD); dirty=[bool](git status --porcelain); python=$taskPython } |
    ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $taskReport 'result.json') -Encoding UTF8
Write-Output ('Verification passed: ' + $taskReport)
