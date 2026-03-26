"""
Uygulama konfigrasyonu.

Bu modul ortam degiskenlerinden gelen ayarlari tek yerde toplar ve
uygulamanin geri kalani icin `settings` nesnesini saglar.
"""

from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    """PostgreSQL ayarlari."""

    model_config = SettingsConfigDict(env_prefix="POSTGRES_", extra="ignore")

    host: str = "localhost"
    port: int = 5432
    db: str = "university_support"
    user: str = "postgres"
    password: str = "postgres123"
    pool_size: int = 10
    max_overflow: int = 5

    @computed_field  # type: ignore[prop-decorator]
    @property
    def async_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sync_url(self) -> str:
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class RedisSettings(BaseSettings):
    """Opsiyonel entegrasyonlar icin saklanan Redis ayarlari."""

    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="ignore")

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    enabled: bool = Field(default=True, validation_alias="USE_REDIS")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"


class OllamaSettings(BaseSettings):
    """Yerel LLM ayarlari."""

    model_config = SettingsConfigDict(env_prefix="OLLAMA_", extra="ignore")

    host: str = "http://localhost:11434"
    model: str = "qwen2.5:7b"
    timeout: int = 30
    max_retries: int = 3


class OpenAISettings(BaseSettings):
    """Opsiyonel OpenAI yedek ayarlari."""

    model_config = SettingsConfigDict(env_prefix="OPENAI_", extra="ignore")

    api_key: Optional[str] = None
    model: str = "gpt-4o-mini"

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)


class ChromaSettings(BaseSettings):
    """ChromaDB ayarlari."""

    model_config = SettingsConfigDict(env_prefix="CHROMA_", extra="ignore")

    host: str = "localhost"
    port: int = 8100

    @computed_field  # type: ignore[prop-decorator]
    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


class EmbeddingSettings(BaseSettings):
    """Embedding modeli ayarlari."""

    model_config = SettingsConfigDict(env_prefix="EMBEDDING_", extra="ignore")

    model: str = "BAAI/bge-m3"
    dimension: int = 1024
    device: Literal["auto", "cpu", "cuda"] = "auto"


class RAGSettings(BaseSettings):
    """RAG hatti ayarlari."""

    model_config = SettingsConfigDict(env_prefix="RAG_", extra="ignore")

    chunk_size: int = 1024
    chunk_overlap: int = 128
    top_k: int = 5
    min_similarity: float = 0.0


class RerankerSettings(BaseSettings):
    """Cross-encoder reranker ayarlari."""

    model_config = SettingsConfigDict(env_prefix="RERANKER_", extra="ignore")

    model: str = "seroe/bge-reranker-v2-m3-turkish-triplet"
    max_length: int = 512
    batch_size: int = 16
    device: Literal["auto", "cpu", "cuda"] = "auto"


class AuthSettings(BaseSettings):
    """OTP ve oturum ayarlari."""

    model_config = SettingsConfigDict(env_prefix="AUTH_", extra="ignore")

    otp_length: int = 6
    otp_ttl_minutes: int = 10
    max_failed_attempts: int = 5
    session_ttl_hours: int = 12


class SlackSettings(BaseSettings):
    """Slack entegrasyon ayarlari."""

    model_config = SettingsConfigDict(env_prefix="SLACK_", extra="ignore")

    bot_token: Optional[str] = None
    signing_secret: Optional[str] = None
    app_token: Optional[str] = None

    @property
    def is_configured(self) -> bool:
        return bool(self.bot_token and self.signing_secret)


class ServerSettings(BaseSettings):
    """Sunucu ayarlari."""

    model_config = SettingsConfigDict(env_prefix="SERVER_", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    log_level: str = "INFO"


class Settings(BaseSettings):
    """Uygulama ayarlarinin kok nesnesi."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    chroma: ChromaSettings = Field(default_factory=ChromaSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    rag: RAGSettings = Field(default_factory=RAGSettings)
    reranker: RerankerSettings = Field(default_factory=RerankerSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    slack: SlackSettings = Field(default_factory=SlackSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)

    base_dir: Path = Path(__file__).parent.parent.parent
    data_dir: Path = base_dir / "data"
    raw_data_dir: Path = data_dir / "raw"
    docs_dir: Path = base_dir / "docs"


settings = Settings()
