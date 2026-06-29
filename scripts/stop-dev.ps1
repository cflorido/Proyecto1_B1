$ErrorActionPreference = 'SilentlyContinue'

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$backendPidFile = Join-Path $repoRoot '.run\backend.pid'
$frontendPidFile = Join-Path $repoRoot '.run\frontend.pid'

function Stop-ByPidFile {
    param([string]$PidFile)

    if (Test-Path $PidFile) {
        $pid = Get-Content $PidFile | Select-Object -First 1
        if ($pid) {
            Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
        }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    }
}

function Stop-PortProcess {
    param([int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Stop-ByPidFile -PidFile $backendPidFile
Stop-ByPidFile -PidFile $frontendPidFile

# Fallback cleanup by ports
Stop-PortProcess -Port 5000
Stop-PortProcess -Port 8000

Write-Output 'Services stopped (if they were running).'
