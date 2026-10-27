# Dot-source from the project root before source tests, then use .venv's Python.
$taskProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$env:PYTHONUTF8 = '1'
$env:PYDANTIC_DISABLE_PLUGINS = '__all__'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
$env:BILICLASS_EXPERIMENTAL_TEACHING = '0'
$env:QT_QPA_PLATFORM = 'windows'
$taskPaths = @($taskProjectRoot, (Join-Path $taskProjectRoot 'scripts'), (Join-Path $taskProjectRoot 'tests'))
$taskExistingRuntime = & (Join-Path $taskProjectRoot 'scripts\prepare-dev-runtime.ps1') -CheckOnly
if ($taskExistingRuntime) {
    $taskPaths += @($taskExistingRuntime, (Join-Path $taskExistingRuntime 'win32'),
        (Join-Path $taskExistingRuntime 'win32\lib'), (Join-Path $taskExistingRuntime 'pywin32_system32'))
}
$env:PYTHONPATH = $taskPaths -join [IO.Path]::PathSeparator
