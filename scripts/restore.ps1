param(
  [Parameter(Mandatory = $true)]
  [string]$BackupZip
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $BackupZip)) {
  throw "Backup file not found: $BackupZip"
}

$tempDir = Join-Path $env:TEMP ("agentme-restore-" + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
Expand-Archive -Path $BackupZip -DestinationPath $tempDir -Force

if (Test-Path (Join-Path $tempDir "Inbox")) {
  Remove-Item "Inbox" -Recurse -Force -ErrorAction SilentlyContinue
  Copy-Item (Join-Path $tempDir "Inbox") -Destination "." -Recurse
}
if (Test-Path (Join-Path $tempDir "logs")) {
  Remove-Item "logs" -Recurse -Force -ErrorAction SilentlyContinue
  Copy-Item (Join-Path $tempDir "logs") -Destination "." -Recurse
}
if (Test-Path (Join-Path $tempDir "data")) {
  Remove-Item "data" -Recurse -Force -ErrorAction SilentlyContinue
  Copy-Item (Join-Path $tempDir "data") -Destination "." -Recurse
}

$sqlPath = Join-Path $tempDir "agentme.sql"
if (Test-Path $sqlPath) {
  Get-Content $sqlPath -Raw | docker exec -i agentme-postgres psql -U postgres -d agentme
}

Remove-Item $tempDir -Recurse -Force
Write-Host "Restore completed from: $BackupZip"
