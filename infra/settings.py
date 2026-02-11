from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    MCP_URL: str = "http://127.0.0.1:8000/mcp"
    OLLAMA_MODEL: str = "qwen3:0.6b"
    MEMORY_DB: str = "memory.db"
    DB_PATH: str = "factory.db"


settings = Settings()
