"""
Uygulama Konfigürasyonu

Tüm ortam değişkenlerini ve uygulama ayarlarını merkezi olarak yönetir.
Pydantic Settings v2 kullanarak tip güvenli konfigürasyon sağlar.

Not:
    Bu dosyadaki bazı ayarlar aktif RAG/LLM çekirdeği tarafından doğrudan
    kullanılır; bazıları ise planlı veya kısmi entegrasyonlar için hazır tutulur.

Her alt sınıf kendi env_prefix'ini tanımlar:
    POSTGRES_HOST, REDIS_PORT, OLLAMA_MODEL, vb.

Kullanım:
    from src.core.config import settings
    settings.postgres.async_url
    settings.rag.top_k
"""

from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    """PostgreSQL veritabanı ayarları."""

    model_config = SettingsConfigDict(env_prefix="POSTGRES_", extra="ignore")

    host: str = "localhost"
    port: int = 5432
    db: str = "university_support"
    user: str = "postgres"
    password: str = "postgres123"

    # Bağlantı havuzu
    pool_size: int = 10
    max_overflow: int = 5

    @computed_field  # type: ignore[prop-decorator]
    @property
    def async_url(self) -> str:
        """Async SQLAlchemy bağlantı URL'si (asyncpg)."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sync_url(self) -> str:
        """Sync SQLAlchemy bağlantı URL'si (psycopg2)."""
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class RedisSettings(BaseSettings):
    """Hazır Redis ayarları.

    Aktif retrieval önbelleği şu anda process içi in-memory çalışır.
    Bu ayarlar harici önbellek veya kuyruk entegrasyonları için korunur.
    """

    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="ignore")

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    enabled: bool = Field(default=True, validation_alias="USE_REDIS")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def url(self) -> str:
        """Redis bağlantı URL'si."""
        return f"redis://{self.host}:{self.port}/{self.db}"


class OllamaSettings(BaseSettings):
    """Ollama (yerel LLM) ayarları."""

    model_config = SettingsConfigDict(env_prefix="OLLAMA_", extra="ignore")

    host: str = "http://localhost:11434"
    model: str = "qwen2.5:7b"
    timeout: int = 30
    max_retries: int = 3


class OpenAISettings(BaseSettings):
    """Opsiyonel OpenAI ayarları.

    Yerel Ollama istemcileri tercih edilir; OpenAI anahtarı varsa yedek veya
    alternatif istemci akışlarında kullanılabilir.
    """

    model_config = SettingsConfigDict(env_prefix="OPENAI_", extra="ignore")

    api_key: Optional[str] = None
    model: str = "gpt-4o-mini"

    @property
    def is_available(self) -> bool:
        """OpenAI API anahtarı tanımlı mı?"""
        return bool(self.api_key)


class ChromaSettings(BaseSettings):
    """ChromaDB vektör veritabanı ayarları."""

    model_config = SettingsConfigDict(env_prefix="CHROMA_", extra="ignore")

    host: str = "localhost"
    port: int = 8100

    @computed_field  # type: ignore[prop-decorator]
    @property
    def url(self) -> str:
        """ChromaDB HTTP URL'si."""
        return f"http://{self.host}:{self.port}"


class EmbeddingSettings(BaseSettings):
    """Gömme modeli ayarları."""

    model_config = SettingsConfigDict(env_prefix="EMBEDDING_", extra="ignore")

    # BAAI/bge-m3: 1024-D, 8192 token, dense+sparse+multi-vector
    # MIRACL benchmark'ta state-of-the-art, Turkce dahil 100+ dil
    model: str = "BAAI/bge-m3"
    dimension: int = 1024
    device: Literal["auto", "cpu", "cuda"] = "auto"


class RAGSettings(BaseSettings):
    """RAG hattı ayarları."""

    model_config = SettingsConfigDict(env_prefix="RAG_", extra="ignore")

    chunk_size: int = 1024
    chunk_overlap: int = 128
    top_k: int = 5
    min_similarity: float = 0.0  # Cross-encoder skorlari negatif olabilir, 0 = filtre yok


class RerankerSettings(BaseSettings):
    """Cross-encoder reranker ayarları."""

    model_config = SettingsConfigDict(env_prefix="RERANKER_", extra="ignore")

    model: str = "seroe/bge-reranker-v2-m3-turkish-triplet"
    max_length: int = 512
    batch_size: int = 16
    device: Literal["auto", "cpu", "cuda"] = "auto"


class SlackSettings(BaseSettings):
    """Slack entegrasyon ayarları.

    Repo içinde Slack tarafı henüz iskelet veya kısmi durumdadır; buna rağmen
    yapılandırma anahtarları şimdiden merkezi olarak tutulur.
    """

    model_config = SettingsConfigDict(env_prefix="SLACK_", extra="ignore")

    bot_token: Optional[str] = None
    signing_secret: Optional[str] = None
    app_token: Optional[str] = None

    @property
    def is_configured(self) -> bool:
        """Gerekli Slack kimlik bilgileri tanımlı mı?"""
        return bool(self.bot_token and self.signing_secret)


class ServerSettings(BaseSettings):
    """Sunucu ayarları.

    Geliştirme ve ileride eklenecek servis katmanları için ortak tutulur.
    """

    model_config = SettingsConfigDict(env_prefix="SERVER_", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    log_level: str = "INFO"


class Settings(BaseSettings):
    """
    Ana konfigürasyon sınıfı.

    Tüm alt ayarları birleştirir ve merkezi erişim noktası sağlar.
    Her alt grup her çalıştırma senaryosunda aktif olarak kullanılmayabilir.

    Kullanım:
        from src.core.config import settings

        settings.postgres.async_url   # PostgreSQL URL
        settings.embedding.model      # Gömme modeli
        settings.rag.top_k            # RAG top-k parametresi
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Alt konfigürasyonlar
    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    chroma: ChromaSettings = Field(default_factory=ChromaSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    rag: RAGSettings = Field(default_factory=RAGSettings)
    reranker: RerankerSettings = Field(default_factory=RerankerSettings)
    slack: SlackSettings = Field(default_factory=SlackSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)

    # Yollar
    base_dir: Path = Path(__file__).parent.parent.parent  # Proje ana klasörü
    data_dir: Path = base_dir / "data"
    raw_data_dir: Path = data_dir / "raw"
    docs_dir: Path = base_dir / "docs"


# Singleton instance: tüm modüller bu örneği kullanır
settings = Settings()
