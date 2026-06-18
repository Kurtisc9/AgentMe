# PC1/PC2 Production Bring-Up Validation Results

Generated: 2026-06-18 UTC

## Summary

Status: **PARTIAL PASS / PC HARDWARE VALIDATION STILL REQUIRED**

The local production Docker stack now builds, starts, runs migrations, serves Mission Control, and returns live backend health/readiness responses. This validates the containerized production path in the current workspace.

The phase is not fully lockable for PC1/PC2 yet because Windows-only and machine-local dependencies are still unavailable in this environment: OBS bridge, Wallpaper Engine, Windows desktop command execution, Ollama, LM Studio, and GPU tooling.

## Critical Fixes Applied During Validation

- Added `ProviderHealthService.check_all()` so `/ready` returns a structured provider/dependency result instead of `500`.
- Updated `Dockerfile` to create `/app/voices` instead of requiring a source `voices/` directory during image build.
- Updated `Dockerfile` to copy `config/` into the backend image so production desktop profiles load in containers.
- Updated `scripts/migrate.py` so the documented `python scripts/migrate.py` command works inside the backend container.
- Merged the existing PC2 profile pack into the production-loaded default profile config.
- Added `data/` to `.gitignore` because the production compose bind mount creates it as runtime state.

## Evidence

| Check | Status | Evidence |
| --- | --- | --- |
| Python test suite | PASS | `SAGE_ENVIRONMENT=development ... pytest -q` -> `69 passed, 2 warnings in 3.63s` |
| Frontend production build | PASS | `npm run build` -> Vite build succeeded |
| Docker production image build | PASS | `docker compose -f docker-compose.prod.yml up -d --build` built backend/frontend |
| Docker production stack | PASS | All services running: backend healthy, frontend up, postgres healthy, qdrant up, n8n up |
| Database migration | PASS | `docker exec agentme-backend python scripts/migrate.py` -> `Applied 001_initial.sql` |
| Backend `/health` live endpoint | PASS | `curl http://127.0.0.1:8000/health` -> `status: healthy` |
| Backend `/ready` live endpoint | PASS | `ready: true`; Postgres/Qdrant true; Ollama/LM Studio false |
| Mission Control live load | PASS | `curl -I http://127.0.0.1:8080` -> `HTTP/1.1 200 OK` |
| Desktop profile editor | PASS | Live PUT temp profile succeeded; live DELETE returned `204`; PC1 returns 11 profiles and PC2 returns 5 profiles |
| OBS bridge | FAIL | Live voice route to OBS matched `pc1_obs_start_recording` but command failed: bridge connection refused |
| Wallpaper Engine path | FAIL | Live desktop execute for `pc1_wallpaper_pause` failed: `wallpaper64.exe` not found |
| Voice command mapper | PARTIAL PASS | Live route matched expected PC1 and PC2 profile IDs; actual Windows execution cannot pass in Linux |
| GPU/model availability | FAIL | Provider health: Postgres/Qdrant true, Ollama false, LM Studio false; `nvidia-smi` not found |

## PC1 Checklist

| Item | Status | Result |
| --- | --- | --- |
| Docker production stack | PASS | Local production stack starts and backend is healthy. Must repeat on PC1. |
| Database migration | PASS | Migration runs successfully inside `agentme-backend`. Must repeat on PC1. |
| Mission Control loads | PASS | `http://127.0.0.1:8080` returns `200 OK`. Must visually verify on PC1. |
| Backend health endpoint | PASS | `/health` returns healthy and `/ready` returns ready with Postgres/Qdrant true. |
| Frontend production build | PASS | `npm run build` succeeds. |
| Desktop profile editor | PASS | Live profile create/delete validated; PC1 profile list exposes 11 profiles. |
| OBS bridge | FAIL | OBS bridge is not reachable at `127.0.0.1:4456` in this environment. |
| Wallpaper Engine path | FAIL | `wallpaper64.exe` is not available in this environment. |
| Voice command mapper | PARTIAL PASS | Live route matches expected PC1 profile IDs; Windows command execution must be verified on PC1. |
| GPU/model availability | FAIL | Ollama, LM Studio, and NVIDIA tooling are unavailable here. |

## PC2 Checklist

| Item | Status | Result |
| --- | --- | --- |
| Docker production stack | PASS | Local production stack starts. Must repeat on PC2 if PC2 runs the stack. |
| Database migration | PASS | Migration runs successfully inside the backend container. Must repeat on PC2 if applicable. |
| Mission Control loads | PASS | Frontend returns `200 OK`. Must visually verify on PC2. |
| Backend health endpoint | PASS | `/health` and `/ready` respond live. |
| Frontend production build | PASS | `npm run build` succeeds. |
| Desktop profile editor | PASS | Live editor works and default loaded config now exposes 5 PC2 profiles. |
| OBS bridge | FAIL | OBS bridge is not reachable at `127.0.0.1:4456` in this environment. |
| Wallpaper Engine path | NOT CONFIGURED | Default loaded PC2 profiles do not include Wallpaper Engine. |
| Voice command mapper | PARTIAL PASS | Live route matches PC2 profile IDs including `pc2_touch_panel`, `pc2_sound_settings`, and `pc2_obs_monitor`; Windows command execution must be verified on PC2. |
| GPU/model availability | FAIL | Ollama, LM Studio, and NVIDIA tooling are unavailable here. |

## Errors Found

1. `/ready` previously returned `500` because `ProviderHealthService.check_all()` was missing. Fixed.
2. Backend Docker build previously failed when source `voices/` was absent. Fixed.
3. Production backend initially loaded zero desktop profiles because `config/` was missing from the image. Fixed.
4. Documented migration command initially failed in-container with `ModuleNotFoundError: No module named 'app'`. Fixed.
5. OBS bridge is not running or reachable at `127.0.0.1:4456`.
6. Wallpaper Engine executable is not available on PATH as `wallpaper64.exe`.
7. Ollama and LM Studio servers are not reachable from the host or backend provider health.
8. GPU tooling is not available: `nvidia-smi` command not found.
9. PC2 profile loading was incomplete in the default production config. Fixed by merging the existing PC2 pack into `config/desktop_profiles.json`.

## Fixes Needed

1. On PC1, run the same production stack with a real local `.env` and real secrets.
2. Install/start the OBS bridge expected at `http://127.0.0.1:4456`, then retry OBS recording/streaming profile commands.
3. Confirm the Wallpaper Engine executable path on PC1 and either add it to PATH or update production profiles to the absolute `wallpaper64.exe` path.
4. Start Ollama on `11434` and LM Studio on `1234/v1`, then verify `/providers/health` reports them correctly.
5. Verify GPU availability on the actual PCs with `nvidia-smi` or the correct vendor tool.
6. Repeat live Mission Control, health/readiness, migration, profile editor, voice routing, OBS, Wallpaper Engine, and model/GPU checks on PC1 and PC2.

## Next Action

Run **PC1 live hardware validation** against the now-startable production stack:

1. Open `http://127.0.0.1:8080` and visually verify Mission Control.
2. Verify `http://127.0.0.1:8000/health` and `http://127.0.0.1:8000/ready`.
3. Start OBS bridge and validate OBS profiles.
4. Validate Wallpaper Engine path/profile execution.
5. Start Ollama/LM Studio and validate model availability.
6. Confirm GPU visibility.

After PC1 passes, repeat on **PC2** with the now-loaded PC2 profile set.
