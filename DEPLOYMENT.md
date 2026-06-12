# AgentMe / Sage Production Deployment

## 1. Prerequisites

- Windows 11 with Docker Desktop
- Python 3.12 for local maintenance scripts
- Ollama and/or LM Studio running on the host
- Piper voice model at `voices/en_US-lessac-medium.onnx`

## 2. Configure secrets

```powershell
Copy-Item .env.example .env
```

Set strong values in `.env`:

```text
SAGE_ENVIRONMENT=production
SAGE_API_KEY=<long-random-secret>
POSTGRES_PASSWORD=<strong-database-password>
N8N_ENCRYPTION_KEY=<long-random-secret>
```

Do not leave `replace_me` values in production.

## 3. Build and start

```powershell
docker compose -f docker-compose.prod.yml up -d --build
```

## 4. Apply database migrations

```powershell
docker exec agentme-backend python scripts/migrate.py
```

## 5. Verify services

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/ready
```

Mission Control:

```text
http://127.0.0.1:8080
```

n8n:

```text
http://127.0.0.1:5678
```

## 6. API authentication

In production, protected API requests require:

```text
X-API-Key: <SAGE_API_KEY>
```

The root, health, readiness, and OpenAPI documentation endpoints remain public.

## 7. Local model access

The production backend reaches host-based model servers through:

```text
http://host.docker.internal:11434
http://host.docker.internal:1234/v1
```

Ollama and LM Studio must allow connections from Docker Desktop.

## 8. Backup

```powershell
./scripts/backup.ps1
```

Backups include PostgreSQL, Inbox records, logs, and local data files.

## 9. Restore

Stop AgentMe application traffic before restoration, then run:

```powershell
./scripts/restore.ps1 -BackupZip backups/<backup-file>.zip
```

Restart the stack afterward:

```powershell
docker compose -f docker-compose.prod.yml restart
```

## 10. Updates

```powershell
git pull
docker compose -f docker-compose.prod.yml up -d --build
docker exec agentme-backend python scripts/migrate.py
```

## 11. Logs

```powershell
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
```

Structured application errors are also written to:

```text
logs/errors.jsonl
```

## 12. Security boundaries

- LOW-risk actions may execute automatically.
- MEDIUM-risk actions require a matching approval record decided by KurtisC.
- HIGH-risk actions remain blocked.
- API keys authenticate access but do not override Sage safety policy.
- Do not expose ports 8000, 5678, 6333, or 5432 directly to the public internet.
