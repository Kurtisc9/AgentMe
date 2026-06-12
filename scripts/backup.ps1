param(
  [string]$OutputDir = "backups"
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$target = Join-Path $OutputDir $timestamp
New-Item -ItemType Directory -Force -Path $target | Out-Null

if (Test-Path "Inbox") { Copy-Item "Inbox" -Destination $target -Recurse }
if (Test-Path "logs") { Copy-Item "logs" -Destination $target -Recurse }
if (Test-Path "data") { Copy-Item "data" -Destination $target -Recurse }

$dumpPath = Join-Path $target "agentme.sql"
docker exec agentme-postgres pg_dump -U postgres agentme | Out-File -Encoding utf8 $dumpPath

Compress-Archive -Path "$target\*" -DestinationPath "$target.zip" -Force
Remove-Item $target -Recurse -Force
Write-Host "Backup created: $target.zip"
