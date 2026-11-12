# Start in this project folder. Requires Python 3.10+; no pip packages for local mode.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pulsePython = (Get-Command python -ErrorAction Stop).Source
& $pulsePython -c 'import sys; assert sys.version_info >= (3,10), "Python 3.10+ required"'
if ($LASTEXITCODE -ne 0) { throw 'Python 3.10+ required' }
Write-Host 'Open http://127.0.0.1:8877 after startup.'
Write-Host 'In a second terminal: python tools/simulator.py --scenario high'
& $pulsePython backend/server.py
