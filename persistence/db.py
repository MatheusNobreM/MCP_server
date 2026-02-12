from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import sessionmaker


def normalize_sqlite_path(db_path: str) -> str:
    path = Path(db_path).expanduser()
    if path.is_absolute():
        return path.as_posix()
    return db_path.replace("\\", "/")


def sqlite_url(db_path: str, read_only: bool = False) -> URL:
    normalized = normalize_sqlite_path(db_path)
    if read_only:
        return URL.create(
            "sqlite",
            database=f"file:{normalized}",
            query={"mode": "ro", "uri": "true"},
        )
    return URL.create("sqlite", database=normalized)


def create_sqlite_engine(
    db_path: str,
    *,
    read_only: bool = False,
    sqlite_wal: bool = False,
) -> Engine:
    engine = create_engine(
        sqlite_url(db_path, read_only=read_only),
        pool_pre_ping=True,
    )

    event.listen(
        engine,
        "connect",
        _sqlite_pragmas(sqlite_wal=sqlite_wal),
    )
    return engine


def session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _sqlite_pragmas(sqlite_wal: bool):
    def _listener(dbapi_connection: Any, _: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        if sqlite_wal:
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()

    return _listener
