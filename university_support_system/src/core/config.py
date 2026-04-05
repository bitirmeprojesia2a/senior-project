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

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

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

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

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

    model_config = SettingsConfigDict(
        env_prefix="OLLAMA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "http://localhost:11434"
    model: str = "qwen2.5:7b"
    secondary_model: str = "qwen2.5:3b"
    timeout: int = 600
    max_retries: int = 3


class OpenAISettings(BaseSettings):
    """Opsiyonel OpenAI yedek ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="OPENAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: Optional[str] = None
    model: str = "gpt-4o-mini"

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)


class LLMRuntimeSettings(BaseSettings):
    """Uygulama ici LLM cagrilarinin zaman asimi ve davranis ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    profile: Literal["fast", "balanced", "quality"] = "balanced"
    routing_model: Optional[str] = "qwen2.5:3b"
    conversation_model: Optional[str] = "qwen2.5:3b"
    specialist_synthesis_model: Optional[str] = None
    global_synthesis_model: Optional[str] = None
    specialist_synthesis_timeout_seconds: int = 600
    global_synthesis_timeout_seconds: int = 600


class ChromaSettings(BaseSettings):
    """ChromaDB ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="CHROMA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "localhost"
    port: int = 8100

    @computed_field  # type: ignore[prop-decorator]
    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


class EmbeddingSettings(BaseSettings):
    """Embedding modeli ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="EMBEDDING_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    model: str = "BAAI/bge-m3"
    dimension: int = 1024
    device: Literal["auto", "cpu", "cuda"] = "auto"
    local_files_only: bool = True


class RAGSettings(BaseSettings):
    """RAG hatti ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="RAG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    chunk_size: int = 1024
    chunk_overlap: int = 128
    top_k: int = 5
    min_similarity: float = 0.0
    reranker_candidate_limit_default: int = 16
    reranker_candidate_limit_finance: int = 5
    reranker_candidate_limit_student_affairs: int = 10
    reranker_candidate_limit_academic_programs: int = 12
    skip_reranker_for_finance_narrow_queries: bool = False
    skip_reranker_for_student_affairs_procedural: bool = True
    skip_reranker_for_academic_programs_procedural: bool = True


class RerankerSettings(BaseSettings):
    """Cross-encoder reranker ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="RERANKER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    model: str = "seroe/bge-reranker-v2-m3-turkish-triplet"
    max_length: int = 512
    batch_size: int = 16
    device: Literal["auto", "cpu", "cuda"] = "auto"
    local_files_only: bool = True


class AuthSettings(BaseSettings):
    """OTP ve oturum ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="AUTH_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    otp_length: int = 6
    otp_ttl_minutes: int = 10
    max_failed_attempts: int = 5
    session_ttl_hours: int = 12
    allowed_student_email_domain: str = "stu.omu.edu.tr"


class EmailSettings(BaseSettings):
    """SMTP tabanli e-posta gonderim ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="EMAIL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "localhost"
    port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None
    from_email: Optional[str] = None
    from_name: str = "OMU Destek Sistemi"
    use_tls: bool = True
    timeout_seconds: int = 15

    @property
    def is_configured(self) -> bool:
        return bool(self.host and self.from_email)


class SlackSettings(BaseSettings):
    """Slack entegrasyon ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="SLACK_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: Optional[str] = None
    signing_secret: Optional[str] = None
    app_token: Optional[str] = None

    @property
    def is_configured(self) -> bool:
        return bool(self.bot_token and self.signing_secret)


class ServerSettings(BaseSettings):
    """Sunucu ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="SERVER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    log_level: str = "INFO"
    warmup_enabled: bool = False
    warmup_include_reranker: bool = False
    warmup_collections: str = "student_affairs_docs,academic_programs_docs"


class ConversationSettings(BaseSettings):
    """Cok turlu konusma baglami ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="CONVERSATION_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = True
    ttl_minutes: int = 60
    rewrite_with_llm: bool = True
    rewrite_timeout_seconds: int = 20
    max_source_refs: int = 5
    max_turns_in_summary: int = 6
    max_answer_summary_chars: int = 320
    max_rolling_summary_chars: int = 900


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
    llm: LLMRuntimeSettings = Field(default_factory=LLMRuntimeSettings)
    chroma: ChromaSettings = Field(default_factory=ChromaSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    rag: RAGSettings = Field(default_factory=RAGSettings)
    reranker: RerankerSettings = Field(default_factory=RerankerSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    slack: SlackSettings = Field(default_factory=SlackSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    conversation: ConversationSettings = Field(default_factory=ConversationSettings)

    base_dir: Path = Path(__file__).parent.parent.parent
    data_dir: Path = base_dir / "data"
    raw_data_dir: Path = data_dir / "raw"
    docs_dir: Path = base_dir / "docs"

    @staticmethod
    def normalize_llm_profile(profile: str | None) -> Literal["fast", "balanced", "quality"]:
        """Desteklenen LLM profil adlarini normalize eder."""
        lowered = (profile or "").strip().lower()
        if lowered in {"fast", "balanced", "quality"}:
            return lowered  # type: ignore[return-value]
        return "balanced"

    def resolve_llm_model(
        self,
        *,
        role: Literal["default", "routing", "conversation", "specialist_synthesis", "global_synthesis"] = "default",
        profile: str | None = None,
    ) -> str:
        """
        LLM rolune gore kullanilacak Ollama modelini cozumler.

        Cozumleme sirası:
        1. Acik istek profili (`fast`, `quality`, `balanced`)
        2. Ayarlardaki varsayilan profil
        3. Role ozel model override'i
        4. Birincil Ollama modeli
        """
        requested_profile = self.normalize_llm_profile(profile or self.llm.profile)
        primary_model = self.ollama.model
        secondary_model = self.ollama.secondary_model or primary_model

        if requested_profile == "fast":
            return secondary_model
        if requested_profile == "quality":
            return primary_model

        role_overrides = {
            "routing": self.llm.routing_model,
            "conversation": self.llm.conversation_model,
            "specialist_synthesis": self.llm.specialist_synthesis_model,
            "global_synthesis": self.llm.global_synthesis_model,
            "default": None,
        }
        return role_overrides.get(role) or primary_model

    def configured_llm_models(self) -> dict[str, str]:
        """Saglik ve debug ciktilari icin cozumlenmis model haritasini dondurur."""
        return {
            "primary": self.ollama.model,
            "secondary": self.ollama.secondary_model or self.ollama.model,
            "profile": self.normalize_llm_profile(self.llm.profile),
            "routing": self.resolve_llm_model(role="routing"),
            "conversation": self.resolve_llm_model(role="conversation"),
            "specialist_synthesis": self.resolve_llm_model(role="specialist_synthesis"),
            "global_synthesis": self.resolve_llm_model(role="global_synthesis"),
        }

    def configured_warmup_collections(self) -> list[str]:
        """Startup warm-up icin koleksiyon listesini cozumler."""
        raw = self.server.warmup_collections
        collections = [item.strip() for item in raw.split(",") if item.strip()]
        return collections or ["student_affairs_docs", "academic_programs_docs"]


settings = Settings()
