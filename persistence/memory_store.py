from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, desc, select

from persistence.db import create_sqlite_engine, session_factory
from persistence.models import Conversation, MemoryBase, Message


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
        self.engine = create_sqlite_engine(db_path, sqlite_wal=True)
        self.session_factory = session_factory(self.engine)
        self._init()

    def _init(self) -> None:
        MemoryBase.metadata.create_all(self.engine)

    def create_conversation(self, conv_id: str, title: Optional[str] = None) -> None:
        now = _now_iso()
        with self.session_factory() as session:
            conversation = session.get(Conversation, conv_id)
            if conversation is None:
                conversation = Conversation(
                    id=conv_id,
                    title=title or "",
                    summary="",
                    created_at=now,
                    updated_at=now,
                )
                session.add(conversation)
            else:
                conversation.title = title or ""
                conversation.updated_at = now
            session.commit()

    def list_conversations(self, limit: int = 20) -> List[Dict[str, Any]]:
        stmt = (
            select(Conversation)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
        )
        with self.session_factory() as session:
            rows = session.scalars(stmt).all()
            return [
                {
                    "id": row.id,
                    "title": row.title,
                    "summary_preview": row.summary[:80],
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                }
                for row in rows
            ]

    def append_message(self, conv_id: str, role: str, content: str) -> None:
        ts = _now_iso()
        with self.session_factory() as session:
            conversation = session.get(Conversation, conv_id)
            if conversation is None:
                conversation = Conversation(
                    id=conv_id,
                    title="",
                    summary="",
                    created_at=ts,
                    updated_at=ts,
                )
                session.add(conversation)
            session.add(
                Message(
                    conversation_id=conv_id,
                    role=role,
                    content=content,
                    ts=ts,
                )
            )
            conversation.updated_at = ts
            session.commit()

    def load_messages(self, conv_id: str, limit: int = 50) -> List[StoredMessage]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conv_id)
            .order_by(desc(Message.id))
            .limit(limit)
        )
        with self.session_factory() as session:
            rows = list(session.scalars(stmt))

        rows.reverse()
        return [
            StoredMessage(role=row.role, content=row.content, ts=row.ts)
            for row in rows
        ]

    def get_summary(self, conv_id: str) -> str:
        with self.session_factory() as session:
            conversation = session.get(Conversation, conv_id)
            if conversation is None:
                return ""
            return conversation.summary or ""

    def set_summary(self, conv_id: str, summary: str) -> None:
        with self.session_factory() as session:
            conversation = session.get(Conversation, conv_id)
            if conversation is None:
                return
            conversation.summary = summary
            conversation.updated_at = _now_iso()
            session.commit()

    def clear_conversation(self, conv_id: str) -> None:
        with self.session_factory() as session:
            session.execute(delete(Message).where(Message.conversation_id == conv_id))
            conversation = session.get(Conversation, conv_id)
            if conversation is not None:
                conversation.summary = ""
                conversation.updated_at = _now_iso()
            session.commit()
