"""Environment-driven backend settings."""
import os
from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("CHAT_HOST", "0.0.0.0")
    port: int = int(os.getenv("CHAT_PORT", "8000"))
    database_path: Path = Path(os.getenv("CHAT_DB_PATH", str(Path(__file__).parent / "chat.db")))
    upload_dir: Path = Path(os.getenv("CHAT_UPLOAD_DIR", str(Path(__file__).parent / "uploads")))
    token_days: int = int(os.getenv("CHAT_TOKEN_DAYS", "30"))
    max_upload_bytes: int = int(os.getenv("CHAT_MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
    cors_origins: tuple = tuple(x.strip() for x in os.getenv("CHAT_CORS_ORIGINS", "http://localhost").split(",") if x.strip())
    log_level: str = os.getenv("CHAT_LOG_LEVEL", "INFO")
settings = Settings()
