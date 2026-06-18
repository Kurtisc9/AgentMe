# Phase 4.1 Real Machine Validation

The repository is stable. This phase validates the real PC1/PC2 hardware and local services that the existing Sage stack depends on.

Do not build new features during this phase.

## Prerequisites

Run PowerShell from the AgentMe repo root on the target machine.

```powershell
git pull
docker compose -f docker-compose.prod.yml up -d --build
docker exec agentme-backend python scripts/migrate.py
```

Set the API key header for protected endpoints:

```powershell
$ApiKey = "<value-from-.env-SAGE_API_KEY>"
$Headers = @{ "X-API-Key" = $ApiKey }
```

Confirm the baseline stack:

```powershell
docker compose -f docker-compose.prod.yml ps
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/ready
Invoke-WebRequest http://127.0.0.1:8080 -UseBasicParsing
```

Expected results:

- Backend container is healthy.
- PostgreSQL is healthy.
- Qdrant is running.
- Frontend returns HTTP 200.
- `/health` returns `status: healthy`.
- `/ready` returns `ready: true`.

## 1. OBS WebSocket

### Validation Steps

1. Start OBS Studio.
2. Start or enable the OBS control bridge/WebSocket listener.
3. Confirm it listens on `127.0.0.1:4456`.
4. Validate Sage can route an OBS command.

### Commands

```powershell
Test-NetConnection 127.0.0.1 -Port 4456
```

```powershell
Invoke-RestMethod http://127.0.0.1:8000/voice-desktop/route `
  -Method Post `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body '{"text":"Sage start recording"}'
```

### Expected Results

- `TcpTestSucceeded` is `True`.
- Voice route response has `matched: true`.
- `profile_id` is `pc1_obs_start_recording`.
- `result.success` is `true`.
- OBS starts recording.

### Failure Conditions

- `TcpTestSucceeded` is `False`.
- Response says `OBS bridge unavailable`.
- `matched` is `false`.
- `result.success` is `false`.
- OBS does not start recording.

### Recovery Steps

1. Confirm OBS is running.
2. Confirm the bridge/WebSocket service is installed and started.
3. Confirm the listener port is `4456`, not the default OBS WebSocket port unless the bridge maps it.
4. Check Windows Firewall for blocked local connections.
5. Restart OBS and the bridge.
6. Re-run `Test-NetConnection 127.0.0.1 -Port 4456`.

## 2. Wallpaper Engine

### Validation Steps

1. Confirm Wallpaper Engine is installed.
2. Locate `wallpaper64.exe`.
3. Confirm the executable can be called by Sage.
4. Validate the existing PC1 Wallpaper profile.

### Commands

```powershell
$WallpaperPath = "C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine\wallpaper64.exe"
Test-Path $WallpaperPath
```

If needed:

```powershell
Get-ChildItem "C:\" -Filter wallpaper64.exe -Recurse -ErrorAction SilentlyContinue
```

Validate through Sage:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/desktop/execute `
  -Method Post `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body '{"profile_id":"pc1_wallpaper_pause"}'
```

### Expected Results

- `Test-Path` returns `True`.
- API response has `profile_id: pc1_wallpaper_pause`.
- API response has `success: true`.
- Wallpaper Engine pauses.

### Failure Conditions

- `wallpaper64.exe` cannot be found.
- API response says `Wallpaper Engine unavailable`.
- API response has `success: false`.
- Wallpaper Engine does not respond.

### Recovery Steps

1. Install Wallpaper Engine through Steam if missing.
2. Launch Wallpaper Engine once manually.
3. Add the Wallpaper Engine folder to PATH, or update the profile command to the absolute executable path.
4. Restart the production backend after profile changes:

```powershell
docker compose -f docker-compose.prod.yml restart backend
```

5. Re-run the API validation.

## 3. Ollama

### Validation Steps

1. Install Ollama.
2. Start Ollama on the host.
3. Confirm local host access.
4. Confirm Sage sees Ollama through provider health.

### Commands

```powershell
ollama list
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

Pull expected models if absent:

```powershell
ollama pull llama3.1:8b
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text
```

Validate through Sage:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/providers/health -Headers $Headers
```

### Expected Results

- `ollama list` returns installed models.
- `/api/tags` returns model data.
- Sage provider health returns `ollama: true`.

### Failure Conditions

- `ollama` command is not recognized.
- Port `11434` is not reachable.
- No required models are listed.
- Sage provider health returns `ollama: false`.

### Recovery Steps

1. Install or repair Ollama.
2. Start Ollama from the Start menu or service manager.
3. Pull missing models.
4. Confirm `.env` uses:

```text
SAGE_OLLAMA_BASE_URL=http://host.docker.internal:11434
```

5. Restart the backend:

```powershell
docker compose -f docker-compose.prod.yml restart backend
```

6. Re-run provider health.

## 4. LM Studio

### Validation Steps

1. Install LM Studio.
2. Open LM Studio.
3. Load a local model.
4. Enable the OpenAI-compatible local server.
5. Confirm the local server uses `127.0.0.1:1234`.
6. Confirm Sage sees LM Studio through provider health.

### Commands

```powershell
Invoke-RestMethod http://127.0.0.1:1234/v1/models
```

```powershell
Invoke-RestMethod http://127.0.0.1:8000/providers/health -Headers $Headers
```

### Expected Results

- `/v1/models` returns model data.
- Sage provider health returns `lm_studio: true`.

### Failure Conditions

- `127.0.0.1:1234` refuses connection.
- LM Studio local server is disabled.
- No model is loaded.
- Sage provider health returns `lm_studio: false`.

### Recovery Steps

1. Start LM Studio.
2. Load a model.
3. Enable the local server.
4. Confirm port `1234`.
5. Confirm `.env` uses:

```text
SAGE_LM_STUDIO_BASE_URL=http://host.docker.internal:1234/v1
```

6. Restart the backend:

```powershell
docker compose -f docker-compose.prod.yml restart backend
```

7. Re-run provider health.

## 5. NVIDIA Telemetry

### Validation Steps

1. Confirm NVIDIA driver installation.
2. Confirm `nvidia-smi` works from PowerShell.
3. Confirm the GPU appears with driver, utilization, and memory fields.

### Commands

```powershell
nvidia-smi
```

Optional telemetry check through Sage:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/telemetry/system -Headers $Headers
```

### Expected Results

- `nvidia-smi` exits successfully.
- Output shows GPU name.
- Output shows driver version.
- Output shows memory usage.
- Sage telemetry endpoint responds.

### Failure Conditions

- `nvidia-smi` is not recognized.
- `nvidia-smi` reports driver failure.
- GPU is missing from output.
- Telemetry endpoint fails.

### Recovery Steps

1. Install or repair the NVIDIA driver.
2. Reboot the PC.
3. Re-run `nvidia-smi`.
4. If the command is still missing, confirm the NVIDIA install directory is on PATH.
5. Restart Sage after driver repair:

```powershell
docker compose -f docker-compose.prod.yml restart backend
```

## 6. PC1 Profile

### Validation Steps

1. Confirm PC1 profiles load.
2. Validate low-risk Windows URI execution.
3. Validate OBS profile routing.
4. Validate Wallpaper Engine profile execution.
5. Validate medium-risk approval gating.

### Commands

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/desktop/profiles?device=PC1" -Headers $Headers
```

```powershell
Invoke-RestMethod http://127.0.0.1:8000/desktop/execute `
  -Method Post `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body '{"profile_id":"pc1_display_settings"}'
```

```powershell
Invoke-RestMethod http://127.0.0.1:8000/voice-desktop/route `
  -Method Post `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body '{"text":"Sage start recording"}'
```

```powershell
Invoke-RestMethod http://127.0.0.1:8000/desktop/execute `
  -Method Post `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body '{"profile_id":"pc1_restart_obs"}'
```

### Expected Results

- PC1 profile list includes `pc1_display_settings`, `pc1_obs_start_recording`, and `pc1_wallpaper_pause`.
- Display Settings opens.
- OBS recording route succeeds when bridge is running.
- Wallpaper profile succeeds when Wallpaper Engine path is valid.
- `pc1_restart_obs` requires KurtisC approval when no approval ID is supplied.

### Failure Conditions

- PC1 profile list is empty.
- URI execution fails with missing `cmd`.
- OBS route fails with bridge unavailable.
- Wallpaper route fails with missing `wallpaper64.exe`.
- Medium-risk profile runs without approval.

### Recovery Steps

1. Rebuild backend if profiles are missing:

```powershell
docker compose -f docker-compose.prod.yml up -d --build backend
```

2. Confirm `config/desktop_profiles.json` exists and includes PC1 profiles.
3. Confirm Windows command execution works outside Docker.
4. Fix OBS bridge and Wallpaper Engine setup using the sections above.
5. Re-run profile validation.

## 7. PC2 Profile

### Validation Steps

1. Confirm PC2 profiles load.
2. Validate PC2 voice routes.
3. Validate PC2 desktop execution where applicable.

### Commands

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/desktop/profiles?device=PC2" -Headers $Headers
```

```powershell
Invoke-RestMethod http://127.0.0.1:8000/voice-desktop/route `
  -Method Post `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body '{"text":"Sage PC2 touch panel browser"}'
```

```powershell
Invoke-RestMethod http://127.0.0.1:8000/voice-desktop/route `
  -Method Post `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body '{"text":"Sage PC2 sound settings"}'
```

```powershell
Invoke-RestMethod http://127.0.0.1:8000/voice-desktop/route `
  -Method Post `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body '{"text":"Sage PC2 OBS monitor"}'
```

### Expected Results

- PC2 profile list includes:
  - `pc2_stream_tools`
  - `pc2_obs_monitor`
  - `pc2_touch_panel`
  - `pc2_sound_settings`
  - `pc2_restart_touch_panel`
- Touch panel route matches `pc2_touch_panel`.
- Sound settings route matches `pc2_sound_settings`.
- OBS monitor route matches `pc2_obs_monitor`.
- On PC2, applicable Windows actions execute successfully.

### Failure Conditions

- PC2 profile list is empty or missing expected IDs.
- Voice route returns `matched: false`.
- Voice route matches the wrong profile.
- URI execution fails with missing `cmd`.
- OBS monitor path does not exist.

### Recovery Steps

1. Confirm the latest commit is present:

```powershell
git log -2 --oneline
```

2. Rebuild the backend image so the latest `config/desktop_profiles.json` is copied in:

```powershell
docker compose -f docker-compose.prod.yml up -d --build backend
```

3. Confirm the PC2 OBS path exists:

```powershell
Test-Path "C:\Program Files\obs-studio\bin\64bit\obs64.exe"
```

4. Re-run PC2 profile and voice route validation.

## Final Validation Checklist

Record pass/fail for each item on both machines.

| Item | PC1 | PC2 |
| --- | --- | --- |
| Docker stack running |  |  |
| Database migration applied |  |  |
| Mission Control loads |  |  |
| Backend `/health` passes |  |  |
| Backend `/ready` passes |  |  |
| Desktop profiles load |  |  |
| Desktop profile editor works |  |  |
| OBS port `4456` reachable |  |  |
| OBS Sage route succeeds |  |  |
| Wallpaper Engine path valid |  |  |
| Wallpaper Sage route succeeds |  |  |
| Ollama local API works |  |  |
| Sage provider health shows Ollama |  |  |
| LM Studio local server works |  |  |
| Sage provider health shows LM Studio |  |  |
| `nvidia-smi` works |  |  |
| Voice routes match expected profiles |  |  |
| Windows desktop execution works |  |  |

The phase is complete only when all configured items pass on the actual machines, or a machine-specific item is explicitly marked not applicable.
