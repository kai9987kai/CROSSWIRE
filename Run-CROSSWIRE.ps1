param([int]$Port = 8781)
$ErrorActionPreference = 'Stop'
$taskPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) { $taskPython = 'python' }
Push-Location -LiteralPath $PSScriptRoot
try { & $taskPython -m crosswire serve --port $Port --open }
finally { Pop-Location }
