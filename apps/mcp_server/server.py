import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, text as sql_text
from sqlalchemy.engine import Engine, URL
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "factory.db")

mcp = FastMCP("Factory SQL MCP")


def _sqlite_read_only_url(db_path: str) -> URL:
    path = Path(db_path).expanduser()
    normalized = path.as_posix() if path.is_absolute() else db_path.replace("\\", "/")
    return URL.create(
        "sqlite",
        database=f"file:{normalized}",
        query={"mode": "ro", "uri": "true"},
    )


ENGINE: Engine = create_engine(_sqlite_read_only_url(DB_PATH), pool_pre_ping=True)


def _is_safe_select(sql: str) -> bool:
    s = sql.strip().lower()

    if ";" in s:
        return False

    if not s.startswith("select"):
        return False

    banned = [
        "pragma",
        "attach",
        "detach",
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "create",
    ]
    return not any(b in s for b in banned)


def _error_payload(exc: Exception) -> List[Dict[str, str]]:
    message = str(exc)
    return [{"error": message, "text": message}]


@mcp.tool()
def run_sql(
    query: str, params: Optional[Dict[str, Any]] = None, limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Executa SQL read-only e retorna linhas em JSON.
    """
    if limit < 1 or limit > 200:
        limit = 50

    if not _is_safe_select(query):
        return [
            {
                "error": "Query bloqueada. Permitido apenas SELECT sem ';' e sem comandos."
            }
        ]

    try:
        with ENGINE.connect() as conn:
            result = conn.execute(sql_text(query), params or {})
            rows = result.mappings().fetchmany(limit)
            return [dict(row) for row in rows]
    except SQLAlchemyError as exc:
        return _error_payload(exc)


@mcp.tool()
def search_sop(text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Busca simples em SOPs (LIKE) para simular recuperacao de documentacao.
    """
    if top_k < 1 or top_k > 20:
        top_k = 5

    stmt = sql_text(
        """
        SELECT id, title, area, substr(content, 1, 160) AS snippet
        FROM sop
        WHERE title LIKE :q OR content LIKE :q
        ORDER BY id DESC
        LIMIT :k
        """
    )

    try:
        with ENGINE.connect() as conn:
            rows = conn.execute(
                stmt,
                {"q": f"%{text}%", "k": top_k},
            ).mappings()
            return [dict(row) for row in rows]
    except SQLAlchemyError as exc:
        return _error_payload(exc)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
