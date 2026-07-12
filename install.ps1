# CodeEZ - Installation script for Windows
Write-Host "=== CodeEZ Installation ===" -ForegroundColor Cyan
Write-Host ""

# Check Python
$pythonCmd = $null
foreach ($cmd in @("python3", "python")) {
    $ver = & $cmd --version 2>$null
    if ($ver -match "Python 3\.(1[0-9]|[2-9][0-9])") {
        $pythonCmd = $cmd
        break
    }
    if ($ver -match "Python 3\.([0-9]+\.[0-9]+)") {
        $verParts = $ver -split " "
        $verNum = $verParts[1] -split "\."
        if ([int]$verNum[1] -ge 10) {
            $pythonCmd = $cmd
            break
        }
    }
}

if (-not $pythonCmd) {
    Write-Host "Python 3.10+ est requis. Telecharge-le sur https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Python trouve : $(& $pythonCmd --version)" -ForegroundColor Green

# Install dependencies
Write-Host "`nInstallation des dependances..." -ForegroundColor Yellow
& $pythonCmd -m pip install -e . 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    & $pythonCmd -m pip install -r requirements.txt 2>&1 | Out-Null
}
Write-Host "[OK] Dependances installees" -ForegroundColor Green

# Install CLI alias
$profilePath = $PROFILE.CurrentUserAllHosts
$aliasLine = "function codeez { python `"$(Get-Location | Select-Object -ExpandProperty Path)\main.py`" @args }"

if (Test-Path $profilePath) {
    $content = Get-Content $profilePath -Raw
    if ($content -notmatch "function codeez") {
        Add-Content $profilePath "`n$aliasLine"
    }
} else {
    New-Item -Path $profilePath -ItemType File -Force | Out-Null
    Add-Content $profilePath $aliasLine
}

Write-Host "[OK] Alias 'codeez' ajoute a votre profile PowerShell" -ForegroundColor Green
Write-Host "`nUtilise 'codeez --setup' pour configurer ta cle API !" -ForegroundColor Cyan
