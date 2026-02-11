from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine, URL


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


@dataclass
class StoredMessage:
    role: str
    content: str
    ts: str


class ChatMemoryStore:
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        path = Path(db_path).expanduser()
        normalized = path.as_posix() if path.is_absolute() else db_path.replace("\\", "/")
        self.engine: Engine = create_engine(
            URL.create("sqlite", database=normalized),
            pool_pre_ping=True,
        )
        event.listen(self.engine, "connect", self._set_sqlite_pragmas)
        self._init()

    @staticmethod
    def _set_sqlite_pragmas(dbapi_connection: Any, _: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()

    def _init(self) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS conversations (
                        id TEXT PRIMARY KEY,
                        title TEXT,
                        summary TEXT DEFAULT '',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        ts TEXT NOT NULL,
                        FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_messages_conv
                    ON messages(conversation_id, id)
                    """
                )
            )

    def create_conversation(self, conv_id: str, title: Optional[str] = None) -> None:
        now = _now_iso()
        stmt = text(
            """
            INSERT INTO conversations (id, title, summary, created_at, updated_at)
            VALUES (:id, :title, '', :now, :now)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                updated_at = excluded.updated_at
            """
        )
        with self.engine.begin() as conn:
            conn.execute(stmt, {"id": conv_id, "title": title or "", "now": now})

    def list_conversations(self, limit: int = 20) -> List[Dict[str, Any]]:
        stmt = text(
            """
            SELECT id, title, substr(summary, 1, 80) AS summary_preview, created_at, updated_at
            FROM conversations
            ORDER BY updated_at DESC
            LIMIT :limit
            """
        )
        with self.engine.connect() as conn:
            rows = conn.execute(stmt, {"limit": limit}).mappings().all()
            return [dict(row) for row in rows]

    def append_message(self, conv_id: str, role: str, content: str) -> None:
        ts = _now_iso()
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO messages (conversation_id, role, content, ts)
                    VALUES (:conv_id, :role, :content, :ts)
                    """
                ),
                {"conv_id": conv_id, "role": role, "content": content, "ts": ts},
            )
            conn.execute(
                text(
                    """
                    UPDATE conversations
                    SET updated_at = :ts
                    WHERE id = :conv_id
                    """
                ),
                {"ts": ts, "conv_id": conv_id},
            )

    def load_messages(self, conv_id: str, limit: int = 50) -> List[StoredMessage]:
        stmt = text(
            """
            SELECT role, content, ts
            FROM messages
            WHERE conversation_id = :conv_id
            ORDER BY id DESC
            LIMIT :limit
            """
        )
        with self.engine.connect() as conn:
            rows = conn.execute(stmt, {"conv_id": conv_id, "limit": limit}).mappings().all()

        rows.reverse()
        return [
            StoredMessage(role=row["role"], content=row["content"], ts=row["ts"])
            for row in rows
        ]

    def get_summary(self, conv_id: str) -> str:
        stmt = text(
            """
            SELECT summary
            FROM conversations
            WHERE id = :conv_id
            """
        )
        with self.engine.connect() as conn:
            row = conn.execute(stmt, {"conv_id": conv_id}).mappings().first()
            return (row["summary"] if row else "") or ""

    def set_summary(self, conv_id: str, summary: str) -> None:
        stmt = text(
            """
            UPDATE conversations
            SET summary = :summary, updated_at = :updated_at
            WHERE id = :conv_id
            """
        )
        with self.engine.begin() as conn:
            conn.execute(
                stmt,
                {"summary": summary, "updated_at": _now_iso(), "conv_id": conv_id},
            )

    def clear_conversation(self, conv_id: str) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text("DELETE FROM messages WHERE conversation_id = :conv_id"),
                {"conv_id": conv_id},
            )
            conn.execute(
                text(
                    """
                    UPDATE conversations
                    SET summary = '', updated_at = :updated_at
                    WHERE id = :conv_id
                    """
                ),
                {"updated_at": _now_iso(), "conv_id": conv_id},
            )
