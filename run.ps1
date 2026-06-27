$pythonExe = "C:\python312\python.exe"

# Windows launcher: use the local Python 3.12 install instead of WindowsApps python alias.
if (-not (Test-Path -LiteralPath $pythonExe)) {
    Write-Host "Python not found: $pythonExe"
    Write-Host "Please install Python or edit `$pythonExe in run.ps1."
    exit 1
}

& $pythonExe main.py @args
