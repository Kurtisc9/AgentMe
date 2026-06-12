# AgentMe / Sage Local Validation

## Goal

This checklist validates Sage on PC1 after all phases are installed.

## 1. Install

Run PowerShell as Administrator:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
./scripts/install_pc1.ps1
```

## 2. Validate

```powershell
./scripts/validate_pc1.ps1
```

## 3. Manual checks

Open Mission Control:

```text
http://127.0.0.1:8080
```

Confirm these pages load:

- Dashboard
- Inbox
- Approvals
- Agents
- Memory
- Voice
- Desktop
- Logs
- Settings

## 4. API checks

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/telemetry/system
Invoke-RestMethod http://127.0.0.1:8000/desktop/profiles
```

## 5. Safety checks

LOW-risk test:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/desktop/execute -Method Post -ContentType "application/json" -Body '{"profile_id":"pc1_display_settings"}'
```

MEDIUM-risk test should fail without approval:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/desktop/execute -Method Post -ContentType "application/json" -Body '{"profile_id":"pc1_restart_obs"}'
```

Voice-to-desktop test:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/voice-desktop/route -Method Post -ContentType "application/json" -Body '{"text":"Sage open display settings"}'
```

## 6. Model checks

Make sure Ollama is running:

```powershell
ollama list
```

Make sure LM Studio local server is running at:

```text
http://127.0.0.1:1234/v1
```

## 7. Backup test

```powershell
./scripts/backup.ps1
```

Confirm a zip appears in:

```text
backups/
```

## 8. Final pass criteria

Sage is considered locally validated when:

- HUD opens
- API health returns healthy
- telemetry works
- desktop profiles load
- LOW desktop command works
- MEDIUM desktop command requires approval
- voice desktop command routes
- backup creates a zip
- pytest passes
- frontend build passes

## 9. Commands

```powershell
pytest -v
npm run build --prefix frontend
./scripts/validate_pc1.ps1
```
