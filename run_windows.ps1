$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonCandidates = @(
    "C:\Users\nguye\AppData\Local\Programs\Python\Python313-32\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python313-32\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312-32\python.exe",
    "python"
)

$Python = $null
foreach ($Candidate in $PythonCandidates) {
    try {
        if ($Candidate -eq "python") {
            $Command = Get-Command python -ErrorAction Stop
            $Python = $Command.Source
            break
        }
        if (Test-Path $Candidate) {
            $Python = $Candidate
            break
        }
    } catch {
        continue
    }
}

if (-not $Python) {
    throw "Python was not found. Re-run the Python installer and enable 'Add Python to environment variables'."
}

Set-Location $ProjectRoot
Write-Host "Using Python: $Python"

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    & $Python -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".\.venv\Scripts\python.exe" run_research.py "Research multi-agent AI systems"
