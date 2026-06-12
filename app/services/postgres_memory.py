from __future__ import annotations

import json

import psycopg

from app.models.memory_record import MemoryRecord, MemoryType


class PostgresMemoryStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def initialize(self) -> None:
        with psycopg.connect(self.database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS memories (
                        memory_id TEXT PRIMARY KEY,
                        memory_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        tags JSONB NOT NULL DEFAULT '[]'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL
                    )
                    """
                )
            connection.commit()

    def upsert(self, record: MemoryRecord) -> None:
        with psycopg.connect(self.database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO memories (memory_id, memory_type, content, tags, created_at)
                    VALUES (%s, %s, %s, %s::jsonb, %s)
                    ON CONFLICT (memory_id) DO UPDATE SET
                        memory_type = EXCLUDED.memory_type,
                        content = EXCLUDED.content,
                        tags = EXCLUDED.tags,
                        created_at = EXCLUDED.created_at
                    """,
                    (
                        record.memory_id,
                        record.memory_type.value,
                        record.content,
                        json.dumps(record.tags),
                        record.created_at,
                    ),
                )
            connection.commit()

    def list_all(self) -> list[dict[str, object]]:
        with psycopg.connect(self.database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT memory_id, memory_type, content, tags, created_at
                    FROM memories
                    ORDER BY created_at DESC
                    """
                )
                rows = cursor.fetchall()

        return [
            {
                "memory_id": row[0],
                "memory_type": MemoryType(row[1]),
                "content": row[2],
                "tags": row[3],
                "created_at": row[4].isoformat(),
            }
            for row in rows
        ]
