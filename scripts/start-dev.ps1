$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$pythonExe = Join-Path $repoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $pythonExe)) {
    Write-Error "Python virtual environment not found at .venv. Create it first: python -m venv .venv"
}

function Stop-PortProcess {
    param([int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        try {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        } catch {
            Write-Warning "Could not stop process $($conn.OwningProcess) on port $Port"
        }
    }
}

function Wait-HttpOk {
    param(
        [string]$Url,
        [int]$Retries = 20,
        [int]$DelaySeconds = 1
    )

    for ($i = 0; $i -lt $Retries; $i++) {
        try {
            $response = Invoke-WebRequest $Url -UseBasicParsing -TimeoutSec 3
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $true
            }
        } catch {
            Start-Sleep -Seconds $DelaySeconds
        }
    }

    return $false
}

# Clean only required ports before start
Stop-PortProcess -Port 5000
Stop-PortProcess -Port 8000

$runtimeDir = Join-Path $repoRoot '.run'
if (-not (Test-Path $runtimeDir)) {
    New-Item -ItemType Directory -Path $runtimeDir | Out-Null
}

$backendLog = Join-Path $runtimeDir 'backend.log'
$backendErr = Join-Path $runtimeDir 'backend.err.log'
$frontendLog = Join-Path $runtimeDir 'frontend.log'
$frontendErr = Join-Path $runtimeDir 'frontend.err.log'
$backendPidFile = Join-Path $runtimeDir 'backend.pid'
$frontendPidFile = Join-Path $runtimeDir 'frontend.pid'

$backend = Start-Process -FilePath $pythonExe -ArgumentList '-m','uvicorn','backend.api.main:app','--reload','--port','8000' -PassThru -RedirectStandardOutput $backendLog -RedirectStandardError $backendErr
$frontend = Start-Process -FilePath $pythonExe -ArgumentList 'frontend\webapp\app.py' -PassThru -RedirectStandardOutput $frontendLog -RedirectStandardError $frontendErr

$backend.Id | Set-Content $backendPidFile
$frontend.Id | Set-Content $frontendPidFile

$backendOk = Wait-HttpOk -Url 'http://127.0.0.1:8000/docs'
$frontendOk = Wait-HttpOk -Url 'http://127.0.0.1:5000/'

if ($backendOk -and $frontendOk) {
    Write-Output 'Services started successfully.'
    Write-Output 'Frontend: http://127.0.0.1:5000'
    Write-Output 'Backend:  http://127.0.0.1:8000/docs'
    Write-Output "Backend log: $backendLog"
    Write-Output "Backend err: $backendErr"
    Write-Output "Frontend log: $frontendLog"
    Write-Output "Frontend err: $frontendErr"
} else {
    Write-Warning 'One or both services failed to start. Check logs:'
    Write-Warning "Backend log: $backendLog"
    Write-Warning "Backend err: $backendErr"
    Write-Warning "Frontend log: $frontendLog"
    Write-Warning "Frontend err: $frontendErr"
    exit 1
}
