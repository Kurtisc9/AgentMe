$ErrorActionPreference = "Continue"

Write-Host "=== AgentMe / Sage PC1 Validation ===" -ForegroundColor Cyan

$checks = @()
function Add-Check($Name, $Passed, $Detail) {
  $script:checks += [pscustomobject]@{ Name = $Name; Passed = $Passed; Detail = $Detail }
}

Add-Check "Git" ([bool](Get-Command git -ErrorAction SilentlyContinue)) "git command"
Add-Check "Docker" ([bool](Get-Command docker -ErrorAction SilentlyContinue)) "docker command"
Add-Check "Python" ([bool](Get-Command python -ErrorAction SilentlyContinue)) "python command"
Add-Check "Node" ([bool](Get-Command node -ErrorAction SilentlyContinue)) "node command"
Add-Check "Env file" (Test-Path ".env") ".env exists"
Add-Check "Desktop profiles" (Test-Path "config/desktop_profiles.json") "desktop profiles exist"

try {
  $health = Invoke-RestMethod http://127.0.0.1:8000/health -TimeoutSec 5
  Add-Check "API health" ($health.ok -eq $true) "health endpoint"
} catch {
  Add-Check "API health" $false $_.Exception.Message
}

try {
  $hud = Invoke-WebRequest http://127.0.0.1:8080 -UseBasicParsing -TimeoutSec 5
  Add-Check "HUD" ($hud.StatusCode -eq 200) "frontend reachable"
} catch {
  Add-Check "HUD" $false $_.Exception.Message
}

try {
  $models = Invoke-RestMethod http://127.0.0.1:8000/telemetry/system -TimeoutSec 5
  Add-Check "Telemetry" ($null -ne $models.hostname) "system telemetry"
} catch {
  Add-Check "Telemetry" $false $_.Exception.Message
}

$checks | Format-Table -AutoSize

if ($checks.Passed -contains $false) {
  Write-Host "Validation failed. Fix failed checks above." -ForegroundColor Red
  exit 1
}

Write-Host "Validation passed." -ForegroundColor Green
