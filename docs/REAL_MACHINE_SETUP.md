# Real Machine Setup

This document is for PC1 and PC2 production bring-up. It does not add features; it lists the machine setup required before final validation can pass.

## Baseline On Each PC

Run PowerShell on the target PC. If the repo is not already cloned, clone it from GitHub first:

```powershell
cd C:\Users\kurti
git clone https://github.com/Kurtisc9/AgentMe.git
cd AgentMe
git checkout phase-4-1-validation
git pull
```

If the repo already exists, enter it directly:

```powershell
cd C:\Users\kurti\AgentMe
git checkout phase-4-1-validation
git pull
```

Confirm you are in the repo root:

```powershell
Get-Location
Test-Path docker-compose.prod.yml
```

Expected result:

```text
Path ends with \AgentMe
True
```

Then configure the environment:

```powershell
Copy-Item .env.example .env
notepad .env
```

Set real non-default production values:

```text
SAGE_ENVIRONMENT=production
SAGE_API_KEY=<strong-local-api-key>
POSTGRES_PASSWORD=<strong-postgres-password>
N8N_ENCRYPTION_KEY=<strong-n8n-encryption-key>
SAGE_OLLAMA_BASE_URL=http://host.docker.internal:11434
SAGE_LM_STUDIO_BASE_URL=http://host.docker.internal:1234/v1
```

Start Sage:

```powershell
docker compose -f docker-compose.prod.yml up -d --build
docker exec agentme-backend python scripts/migrate.py
```

Set an API key variable for protected API checks:

```powershell
$ApiKey = "<strong-local-api-key>"
$Headers = @{ "X-API-Key" = $ApiKey }
```

## OBS WebSocket / Bridge Port 4456

Status: **DISABLED / SKIPPED FOR NOW**

OBS setup is documented for later re-enable, but it is not required for the current validation pass.

Sage OBS desktop profiles call a local OBS control bridge at:

```text
http://127.0.0.1:4456
```

Required PC setup:

1. Install OBS Studio.
2. Enable/configure the OBS WebSocket or OBS control bridge used by this machine.
3. Set the bridge/listener port to `4456`.
4. Start OBS before running OBS validation.
5. Confirm the bridge is reachable:

```powershell
Test-NetConnection 127.0.0.1 -Port 4456
```

Expected result:

```text
TcpTestSucceeded : True
```

Validate Sage OBS routing:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/voice-desktop/route `
  -Method Post `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body '{"text":"Sage start recording"}'
```

Pass criteria:

- `matched` is `true`
- `profile_id` is `pc1_obs_start_recording`
- `result.success` is `true`

## Wallpaper Engine Path

Default PC1 profiles expect Wallpaper Engine to be available as:

```text
wallpaper64.exe
```

Common Steam path:

```text
C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine\wallpaper64.exe
```

Validate the executable:

```powershell
$WallpaperPath = "C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine\wallpaper64.exe"
Test-Path $WallpaperPath
```

If `Test-Path` returns `False`, locate Wallpaper Engine:

```powershell
Get-ChildItem "C:\" -Filter wallpaper64.exe -Recurse -ErrorAction SilentlyContinue
```

Make the command available to Sage either by adding the folder to the machine PATH or by updating the relevant profile command to the absolute path.

Validate from the API:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/desktop/execute `
  -Method Post `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body '{"profile_id":"pc1_wallpaper_pause"}'
```

Pass criteria:

- `profile_id` is `pc1_wallpaper_pause`
- `success` is `true`

## Ollama

Install and start Ollama on the host.

Validate locally:

```powershell
ollama list
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

Pull expected models if missing:

```powershell
ollama pull llama3.1:8b
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text
```

Validate Docker can reach Ollama through the production URL:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/providers/health -Headers $Headers
```

Pass criteria:

- `ollama` is `true`

## LM Studio Local Server

In LM Studio:

1. Open the local server panel.
2. Start the OpenAI-compatible local server.
3. Use port `1234`.
4. Confirm the base URL is:

```text
http://127.0.0.1:1234/v1
```

Validate locally:

```powershell
Invoke-RestMethod http://127.0.0.1:1234/v1/models
```

Validate through Sage:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/providers/health -Headers $Headers
```

Pass criteria:

- `lm_studio` is `true`

## NVIDIA `nvidia-smi`

Status: **DISABLED / SKIPPED FOR NOW**

NVIDIA telemetry is documented for later re-enable, but it is not required for the current validation pass. Sage telemetry tolerates missing `nvidia-smi` by returning empty GPU fields.

Validate GPU tooling on each machine:

```powershell
nvidia-smi
```

If the command is missing:

1. Install or repair the NVIDIA driver.
2. Restart the PC.
3. Re-run `nvidia-smi`.

Pass criteria:

- Command exits successfully.
- GPU name, driver version, and memory usage are displayed.

## Windows Desktop Execution

Sage desktop execution uses Windows commands:

- URI profiles use `cmd /c start`
- folder profiles use `explorer`
- PowerShell profiles use `powershell -NoProfile -Command`
- application profiles launch the configured executable path

Validate low-risk Windows URI execution:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/desktop/execute `
  -Method Post `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body '{"profile_id":"pc1_display_settings"}'
```

Pass criteria:

- Windows Display Settings opens.
- API result has `success: true`.

Validate medium-risk approval behavior:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/desktop/execute `
  -Method Post `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body '{"profile_id":"pc1_restart_obs"}'
```

Pass criteria:

- Request fails without an approval ID.
- Response says KurtisC approval is required.

## PC1 Validation Checklist

Run on PC1:

```powershell
docker compose -f docker-compose.prod.yml ps
docker exec agentme-backend python scripts/migrate.py
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/ready
Invoke-WebRequest http://127.0.0.1:8080 -UseBasicParsing
Invoke-RestMethod http://127.0.0.1:8000/desktop/profiles?device=PC1 -Headers $Headers
Invoke-RestMethod http://127.0.0.1:8000/providers/health -Headers $Headers
ollama list
Invoke-RestMethod http://127.0.0.1:1234/v1/models
```

Pass criteria:

- Backend container is healthy.
- Frontend container is running.
- Migration completes.
- `/health` returns healthy.
- `/ready` returns `ready: true`.
- Mission Control returns HTTP 200 and loads in the browser.
- PC1 desktop profiles load.
- OBS bridge port `4456` is skipped for now.
- Wallpaper Engine profile executes.
- Voice route for `Sage open display settings` matches `pc1_display_settings`.
- OBS voice routes are skipped for now.
- Ollama and LM Studio are true in `/providers/health`.
- NVIDIA telemetry is skipped for now.

## PC2 Validation Checklist

Run on PC2:

```powershell
docker compose -f docker-compose.prod.yml ps
docker exec agentme-backend python scripts/migrate.py
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/ready
Invoke-WebRequest http://127.0.0.1:8080 -UseBasicParsing
Invoke-RestMethod http://127.0.0.1:8000/desktop/profiles?device=PC2 -Headers $Headers
Invoke-RestMethod http://127.0.0.1:8000/providers/health -Headers $Headers
ollama list
Invoke-RestMethod http://127.0.0.1:1234/v1/models
```

Pass criteria:

- Backend container is healthy.
- Frontend container is running.
- Migration completes.
- `/health` returns healthy.
- `/ready` returns `ready: true`.
- Mission Control returns HTTP 200 and loads in the browser.
- PC2 desktop profiles load, including `pc2_touch_panel` and `pc2_sound_settings`.
- Voice route for `Sage PC2 touch panel browser` matches `pc2_touch_panel`.
- Voice route for `Sage PC2 sound settings` matches `pc2_sound_settings`.
- OBS voice routes are skipped for now.
- Ollama and LM Studio are true in `/providers/health`.
- NVIDIA telemetry is skipped for now.

## Final Lock Criteria

The real-machine phase can lock only when both PC1 and PC2 have:

- production stack running
- migration applied
- Mission Control loading
- backend health and readiness passing
- frontend production build verified
- desktop profile editor verified
- OBS bridge skipped for now
- Wallpaper Engine path verified where configured
- voice command mapper matching and executing machine profiles
- Ollama and/or LM Studio available as intended
- NVIDIA telemetry skipped for now
