# MCP SQL SOP

AI backend project that combines a local LLM (Ollama), MCP tools, and SQL access for industrial operations data.

Built as a practical demo of how to create a production-style assistant with:
- tool calling over MCP
- read-only SQL access with SQLAlchemy
- persistent chat memory in SQLite
- synthetic factory domain data (equipment, events, alarms, maintenance, SOPs)

## Why this project

This repository shows an end-to-end pattern for enterprise AI assistants:
- keep the LLM local
- expose controlled tools via MCP
- enforce safe SQL access
- keep conversation history persistent

It is useful as a portfolio project for AI Engineering, Data/Backend Engineering, and Applied GenAI use cases.

## Architecture

1. `apps/mcp_server/server.py`
MCP server (`FastMCP`) exposing tools:
- `run_sql(query, params, limit)`
- `search_sop(text, top_k)`

2. `apps/bot_cli/main.py`
CLI chat client that:
- calls Ollama
- executes MCP tools
- uses retry/fallback logic when tool usage is needed

3. `persistence/memory_store.py`
Persistent memory store with SQLAlchemy + SQLite for conversation and message history.

4. `scripts/seed_factory_db.py`
Creates and seeds a synthetic SQLite dataset for demo scenarios.

## Tech stack

- Python 3.13+
- MCP (`mcp[cli]`)
- Ollama
- SQLAlchemy 2.x
- SQLite
- Pydantic / Pydantic Settings
- python-dotenv

## Quick start

### 1) Install dependencies

```bash
uv sync
```

### 2) (Optional) Configure environment

Create a `.env` file in the project root:

```env
MCP_URL=http://127.0.0.1:8000/mcp
OLLAMA_MODEL=qwen3:0.6b
MEMORY_DB=memory.db
DB_PATH=factory.db
```

### 3) Seed demo database

```bash
uv run python scripts/seed_factory_db.py
```

### 4) Start MCP server

```bash
uv run python -m apps.mcp_server.server
```

### 5) Start CLI bot (new terminal)

```bash
uv run python -m apps.bot_cli.main
```

To exit the bot, type:

```text
sair
```

## Example prompts

- `Liste os eventos mais recentes do COMP-01`
- `Quais alarmes criticos ocorreram ontem?`
- `Mostre o SOP de shutdown de compressor`
- `Traga as ordens de manutencao em aberto`

## SQL safety model

`run_sql` is read-only by design:
- allows only `SELECT`
- blocks `;` and DDL/DML keywords (`insert`, `update`, `delete`, `drop`, etc.)
- opens SQLite in read-only mode (`mode=ro`)
- executes with SQLAlchemy bind parameters

## Project structure

```text
apps/
  bot_cli/main.py
  mcp_server/server.py
domain/
infra/
  mcp_client.py
  settings.py
persistence/
  memory_store.py
scripts/
  seed_factory_db.py
README.md
pyproject.toml
```

## Next improvements

- add automated tests for MCP tools and memory store
- add Docker Compose for one-command startup
- add web UI and observability (logs/traces/metrics)
- add role-based SQL policies and query audit trail
