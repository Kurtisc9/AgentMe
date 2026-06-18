from __future__ import annotations

import sys
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import get_settings


def main() -> None:
    settings = get_settings()
    migrations_dir = Path("migrations")
    migration_files = sorted(migrations_dir.glob("*.sql"))
    if not migration_files:
        raise SystemExit("No migration files found.")

    with psycopg.connect(settings.postgres_url) as connection:
        for migration in migration_files:
            sql = migration.read_text(encoding="utf-8")
            with connection.cursor() as cursor:
                cursor.execute(sql)
            connection.commit()
            print(f"Applied {migration.name}")


if __name__ == "__main__":
    main()
