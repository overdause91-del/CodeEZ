# CodeEZ Launcher - trouve Python meme s'il n'est pas dans le PATH
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Chercher python partout
$pythonCandidates = @(
    "python3.exe", "python.exe"
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe"
    "C:\Python313\python.exe", "C:\Python312\python.exe"
    "C:\Python311\python.exe", "C:\Python310\python.exe"
    "C:\Program Files\Python313\python.exe"
    "C:\Program Files\Python312\python.exe"
)

$python = $null
foreach ($cmd in $pythonCandidates) {
    $ver = & $cmd --version 2>$null
    if ($ver -match "Python 3\.(1[0-9]|[2-9][0-9])") {
        $python = $cmd
        break
    }
}

if (-not $python) {
    Write-Host "Python 3.10+ introuvable." -ForegroundColor Red
    Write-Host "Telecharge-le sur https://python.org" -ForegroundColor Yellow
    pause
    exit 1
}

& $python "$scriptDir\codeez.py" @args
