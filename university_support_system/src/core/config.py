"""
Uygulama konfigrasyonu.

Bu modul ortam degiskenlerinden gelen ayarlari tek yerde toplar ve
uygulamanin geri kalani icin `settings` nesnesini saglar.
"""

import os
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LLMProvider = Literal["openai_compatible", "google_ai", "anthropic"]
LLMSpeedProfile = Literal["fast", "balanced", "quality"]
LLMOperatingProfile = Literal["standard", "groq_only", "hybrid_shadow", "hybrid_quality"]
LLMRole = Literal[
    "default",
    "routing",
    "conversation",
    "query_expansion",
    "evidence_selection",
    "final_refinement",
    "specialist_synthesis",
    "global_synthesis",
    "judge",
]
CapabilityPlannerMode = Literal["off", "shadow", "pilot", "on"]
MultiIntentPlannerMode = Literal["off", "shadow", "pilot", "on"]
SourceOwnerPolicyMode = Literal["off", "advisory", "balanced", "strict"]
AnswerValidationMode = Literal["off", "shadow", "contract_enforce"]
PROJECT_ROOT = Path(__file__).resolve().parents[2]


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


class OpenAISettings(BaseSettings):
    """OpenAI-compatible provider ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="OPENAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: Optional[str] = None
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    secondary_model: Optional[str] = None
    routing_model: Optional[str] = None
    conversation_model: Optional[str] = None
    query_expansion_model: Optional[str] = None
    evidence_selection_model: Optional[str] = None
    final_refinement_model: Optional[str] = None
    specialist_synthesis_model: Optional[str] = None
    global_synthesis_model: Optional[str] = None
    reasoning_effort: Optional[str] = None
    timeout: int = 30
    provider_name: str = "openai_compatible"

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)


class GoogleAISettings(OpenAISettings):
    """Google Gemini OpenAI-compatible endpoint ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="GOOGLE_AI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    model: str = "gemini-2.5-flash"
    secondary_model: Optional[str] = "gemini-2.5-flash-lite"
    reasoning_effort: Optional[str] = "none"
    provider_name: str = "google_ai"


class AnthropicSettings(BaseSettings):
    """Anthropic Claude Messages API ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="ANTHROPIC_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: Optional[str] = None
    base_url: str = "https://api.anthropic.com"
    model: str = "claude-sonnet-4-20250514"
    secondary_model: Optional[str] = None
    routing_model: Optional[str] = None
    conversation_model: Optional[str] = None
    query_expansion_model: Optional[str] = None
    evidence_selection_model: Optional[str] = None
    final_refinement_model: Optional[str] = None
    specialist_synthesis_model: Optional[str] = None
    global_synthesis_model: Optional[str] = None
    max_tokens: int = 4096
    timeout: int = 60
    anthropic_version: str = Field(default="2023-06-01", validation_alias="ANTHROPIC_VERSION")
    temperature: Optional[float] = None
    provider_name: str = "anthropic"

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

    profile: str = "balanced"
    routing_model: Optional[str] = None
    conversation_model: Optional[str] = None
    query_expansion_model: Optional[str] = None
    evidence_selection_model: Optional[str] = None
    final_refinement_model: Optional[str] = None
    specialist_synthesis_model: Optional[str] = None
    global_synthesis_model: Optional[str] = None
    judge_model: Optional[str] = None
    routing_provider: Optional[LLMProvider] = None
    conversation_provider: Optional[LLMProvider] = None
    query_expansion_provider: Optional[LLMProvider] = None
    evidence_selection_provider: Optional[LLMProvider] = None
    final_refinement_provider: Optional[LLMProvider] = None
    specialist_synthesis_provider: Optional[LLMProvider] = None
    global_synthesis_provider: Optional[LLMProvider] = None
    judge_provider: Optional[LLMProvider] = None
    main_judge_enabled: bool = True
    specialist_synthesis_enabled: bool = False
    specialist_judge_enabled: bool = False
    query_normalization_enabled: bool = True
    query_normalization_timeout_seconds: int = 6
    specialist_synthesis_timeout_seconds: int = 120
    global_synthesis_timeout_seconds: int = 120
    primary_provider: LLMProvider = "openai_compatible"
    fallback_provider: Literal["none", "openai_compatible", "google_ai", "anthropic"] = "google_ai"
    high_value_provider: Optional[LLMProvider] = None
    high_value_roles: str = "global_synthesis,specialist_synthesis"


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
    batch_size: int = 32
    device: Literal["auto", "cpu", "cuda"] = "auto"
    torch_dtype: Literal["auto", "float32", "float16", "bfloat16"] = "auto"
    cuda_fallback_to_cpu: bool = True
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
    min_chunk_chars: int = 50
    parent_child_chunking_enabled: bool = True
    parent_chunk_size: int = 2400
    parent_context_max_chars: int = 2600
    top_k: int = 5
    min_similarity: float = 0.02
    reranker_candidate_limit_default: int = 16
    reranker_candidate_limit_finance: int = 5
    reranker_candidate_limit_student_affairs: int = 10
    reranker_candidate_limit_academic_programs: int = 12
    primary_reranker_candidate_limit: int = 8
    support_lite_top_k: int = 4
    support_lite_reranker_candidate_limit: int = 4
    primary_multi_query_max_variants: int = 1
    multi_query_variant_top_k: int = 3
    multi_query_variant_reranker_candidate_limit: int = 4
    reranker_concurrency_limit: int = 2
    llm_query_expansion_enabled: bool = False
    llm_query_expansion_timeout_seconds: int = 8
    llm_query_expansion_max_chars: int = 420
    llm_evidence_selection_enabled: bool = False
    llm_evidence_selection_timeout_seconds: int = 10
    llm_evidence_selection_min_candidates: int = 4
    llm_evidence_selection_max_candidates: int = 10
    llm_evidence_selection_max_selected: int = 5
    source_relevance_penalty_enabled: bool = True
    query_profile_source_bias_enabled: bool = True
    education_level_penalty_enabled: bool = True
    finance_source_penalty_enabled: bool = True
    student_affairs_faq_bias_enabled: bool = True
    source_constrained_recall_enabled: bool = True
    source_constrained_recall_max_per_collection: int = 10
    source_constrained_recall_max_total: int = 12
    source_constrained_reranker_extra: int = 6
    department_scoped_recall_enabled: bool = True
    department_scoped_recall_max_per_collection: int = 4
    department_scoped_recall_max_total: int = 6
    department_scoped_recall_min_lexical_score: float = 2.0
    fallback_primary_score_threshold: float = 0.2


class RerankerSettings(BaseSettings):
    """Cross-encoder reranker ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="RERANKER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    model: str = "nreimers/mmarco-mMiniLMv2-L6-H384-v1"
    max_length: int = 512
    batch_size: int = 16
    device: Literal["auto", "cpu", "cuda"] = "auto"
    torch_dtype: Literal["auto", "float32", "float16", "bfloat16"] = "auto"
    local_files_only: bool = True


class RetrievalServiceSettings(BaseSettings):
    """Merkezi retrieval/reranker servisi ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="RETRIEVAL_SERVICE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = False
    url: str = "http://retrieval-service:8140"
    timeout_seconds: float = 75.0
    fallback_to_local: bool = True

    @property
    def normalized_url(self) -> str:
        return self.url.rstrip("/")


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
    otp_request_cooldown_seconds: int = 60
    max_failed_attempts: int = 5
    session_ttl_hours: int = 12
    allowed_student_email_domain: str = "stu.omu.edu.tr"


class InstitutionSettings(BaseSettings):
    """Kurum kimligi ve sunumda degistirilebilir temel alanlar."""

    model_config = SettingsConfigDict(
        env_prefix="INSTITUTION_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    short_name: str = "OMÜ"
    short_name_ascii: str = "OMU"
    name: str = "Ondokuz Mayıs Üniversitesi"
    name_ascii: str = "Ondokuz Mayis Universitesi"
    homepage_url: str = "https://www.omu.edu.tr"
    support_bot_name: str = "OMÜ Destek Botu"
    switchboard_phone: str = "0 (362) 312 19 19"


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
    from_name: str = ""
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

    @property
    def socket_mode_configured(self) -> bool:
        return bool(self.bot_token and self.signing_secret and self.app_token)


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
    public_url: Optional[str] = None
    app_version: str = "1.0.0"
    build_id: str = "dev"
    build_timestamp: str = "unknown"
    git_sha: str = "unknown"
    image_ref: str = "unversioned"
    runtime_label: str = "default"
    debug: bool = True
    log_level: str = "INFO"
    response_debug_enabled: bool = True
    internal_api_key: Optional[str] = None
    warmup_enabled: bool = False
    warmup_include_reranker: bool = False
    warmup_collections: str = "student_affairs_docs,academic_programs_docs"
    warmup_llm_enabled: bool = True
    warmup_llm_roles: str = "routing,evidence_selection,final_refinement,specialist_synthesis"
    warmup_llm_timeout_seconds: int = 15
    warmup_llm_prompt: str = "Yalnizca OK yaz."

    def build_metadata(self) -> dict[str, str]:
        """Saglik ve rollout icin surum/build metadata'sini dondurur."""
        return {
            "version": self.app_version,
            "build_id": self.build_id,
            "build_timestamp": self.build_timestamp,
            "git_sha": self.git_sha,
            "image_ref": self.image_ref,
        }


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
    max_recent_turns: int = 3
    max_answer_summary_chars: int = 320
    max_rolling_summary_chars: int = 900
    reset_on_build: bool = True


class CacheSettings(BaseSettings):
    """Uygulama ici cache ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="CACHE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = True
    question_cache_enabled: bool = True
    question_cache_ttl_seconds: int = 300
    question_cache_max_entries: int = 512
    redis_question_cache_enabled: bool = True
    retriever_query_cache_enabled: bool = True
    retriever_query_cache_ttl_seconds: int = 300
    retriever_query_cache_max_entries: int = 512
    redis_retriever_query_cache_enabled: bool = True
    embedding_model_cache_enabled: bool = True
    reranker_model_cache_enabled: bool = True
    bm25_resource_cache_enabled: bool = True
    bm25_document_cache_max_collections: int = 6
    bm25_retriever_cache_max_entries: int = 16


class ModelCacheSettings(BaseSettings):
    """Local Hugging Face model cache settings for scripts and services."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host_dir: Optional[Path] = Field(default=None, validation_alias="MODEL_CACHE_HOST_DIR")
    set_hf_env: bool = Field(default=True, validation_alias="MODEL_CACHE_SET_HF_ENV")

    @property
    def resolved_host_dir(self) -> Optional[Path]:
        """Return the absolute project model cache root when configured."""
        if self.host_dir is None:
            return None

        path = self.host_dir.expanduser()
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path.resolve()

    @property
    def hf_home(self) -> Optional[Path]:
        root = self.resolved_host_dir
        return root / "huggingface" if root is not None else None

    @property
    def hf_hub_cache(self) -> Optional[Path]:
        hf_home = self.hf_home
        return hf_home / "hub" if hf_home is not None else None


class A2ASettings(BaseSettings):
    """Departman ajanlari arasi transport ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="A2A_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mode: Literal["inprocess", "http", "shadow"] = "inprocess"
    specialist_mode: Literal["inprocess", "http"] = "inprocess"
    transport_protocol: Literal["rest", "jsonrpc"] = "rest"
    timeout_seconds: float = 10.0
    department_timeout_seconds: float | None = None
    specialist_timeout_seconds: float | None = 60.0
    retry_count: int = 1
    retry_backoff_seconds: float = 0.25
    circuit_breaker_threshold: int = 2
    circuit_breaker_cooldown_seconds: float = 15.0
    discovery_ttl_seconds: float = 120.0
    discovery_healthcheck_enabled: bool = True
    discovery_healthcheck_timeout_seconds: float = 2.0
    discovery_healthcheck_cache_seconds: float = 15.0
    discovery_agent_card_enabled: bool = False
    discovery_agent_card_timeout_seconds: float = 2.0
    discovery_agent_card_cache_seconds: float = 60.0
    internal_api_key: Optional[str] = None
    require_service_identity: bool = False
    allowed_caller_ids: str = ""
    require_request_signature: bool = False
    request_signature_secret: Optional[str] = None
    request_signature_ttl_seconds: int = 300
    external_trust_enabled: bool = False
    external_allowed_agent_ids: str = ""
    external_agent_endpoints: str = ""
    external_agent_signature_secrets: str = ""
    external_require_request_signature: bool = True
    external_request_signature_secret: Optional[str] = None
    external_agent_card_timeout_seconds: float = 3.0
    student_affairs_url: Optional[str] = None
    academic_programs_url: Optional[str] = None
    finance_url: Optional[str] = None
    announcement_url: Optional[str] = None
    event_url: Optional[str] = None
    specialist_endpoints: str = ""

    @field_validator("department_timeout_seconds", "specialist_timeout_seconds", mode="before")
    @classmethod
    def _empty_timeout_to_none(cls, value: object) -> object:
        """Allow blank env values for optional timeout fields."""
        if value == "":
            return None
        return value

    def effective_department_timeout_seconds(self) -> float:
        """Timeout budget for main-orchestrator to department-service calls.

        Department services may spend their own specialist timeout budget before
        responding, so this can be configured separately from the generic A2A
        request timeout used by faster capability calls.
        """
        if self.department_timeout_seconds is not None:
            return max(0.1, float(self.department_timeout_seconds))
        return max(0.1, float(self.timeout_seconds))

    def endpoint_for(self, department: str) -> str | None:
        """Return the configured base URL for a department or capability service."""
        endpoints = {
            "student_affairs": self.student_affairs_url,
            "academic_programs": self.academic_programs_url,
            "finance": self.finance_url,
            "announcement": self.announcement_url,
            "event": self.event_url,
        }
        value = endpoints.get(department)
        return value.rstrip("/") if value else None

    def specialist_endpoint_for(self, agent_id: str) -> str | None:
        """Return a configured specialist-agent base URL from `A2A_SPECIALIST_ENDPOINTS`.

        Format: `tuition_agent=http://agent-finance-tuition:8110,scholarship_agent=http://...`
        """
        target = agent_id.strip()
        if not target or not self.specialist_endpoints.strip():
            return None
        for item in self.specialist_endpoints.split(","):
            if "=" not in item:
                continue
            key, value = item.split("=", 1)
            if key.strip() == target and value.strip():
                return value.strip().rstrip("/")
        return None

    def allowed_caller_id_set(self) -> set[str]:
        """Return configured A2A caller service ids."""
        return {
            item.strip()
            for item in self.allowed_caller_ids.split(",")
            if item.strip()
        }

    @staticmethod
    def _parse_key_value_list(raw: str) -> dict[str, str]:
        parsed: dict[str, str] = {}
        for item in raw.split(","):
            if "=" not in item:
                continue
            key, value = item.split("=", 1)
            cleaned_key = key.strip()
            cleaned_value = value.strip()
            if cleaned_key and cleaned_value:
                parsed[cleaned_key] = cleaned_value
        return parsed

    def external_agent_endpoint_map(self) -> dict[str, str]:
        """Return configured external A2A agent endpoints.

        Format: `partner_agent=https://partner.example,other=http://host:9000`
        """
        return self._parse_key_value_list(self.external_agent_endpoints)

    def external_agent_secret_map(self) -> dict[str, str]:
        """Return per-partner external A2A HMAC secrets.

        Format: `partner_agent=secret,other=secret2`
        """
        return self._parse_key_value_list(self.external_agent_signature_secrets)

    def external_allowed_agent_id_set(self) -> set[str]:
        """Return explicitly trusted external A2A caller ids."""
        configured = {
            item.strip()
            for item in self.external_allowed_agent_ids.split(",")
            if item.strip()
        }
        return (
            configured
            | set(self.external_agent_endpoint_map().keys())
            | set(self.external_agent_secret_map().keys())
        )

    def external_signature_secret_for(self, caller_id: str | None) -> str | None:
        """Return the HMAC secret for an external caller id."""
        if not caller_id:
            return None
        return (
            self.external_agent_secret_map().get(caller_id)
            or self.external_request_signature_secret
        )

    def resolved_request_signature_secret(self, fallback_key: str | None = None) -> str | None:
        """Return the secret used for optional A2A request signatures."""
        return (
            self.request_signature_secret
            or self.internal_api_key
            or fallback_key
        )


class AgentServiceSettings(BaseSettings):
    """Ayrik agent servisi ayarlari."""

    model_config = SettingsConfigDict(
        env_prefix="AGENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    department: Optional[
        Literal["student_affairs", "academic_programs", "finance", "announcement", "event"]
    ] = None
    specialist_id: Optional[str] = None
    service_id: str = "department-agent"
    public_url: str = "http://localhost:8101"


class CapabilityPlannerSettings(BaseSettings):
    """Feature-flagged capability planner rollout settings."""

    model_config = SettingsConfigDict(
        env_prefix="CAPABILITY_PLANNER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mode: CapabilityPlannerMode = "on"
    scope: str = "academic_programs,student_affairs,finance,announcement,event"
    timeout_seconds: float = Field(default=4.0, ge=0.5, le=30.0)
    confidence_threshold: float = Field(default=0.45, ge=0.0, le=1.0)
    pre_route_enabled: bool = False
    pre_route_confidence_threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    max_records_for_synthesis: int = Field(default=40, ge=1, le=200)
    synthesize_with_llm: bool = True

    @property
    def enabled(self) -> bool:
        return self.mode != "off"

    @property
    def should_apply(self) -> bool:
        return self.mode in {"pilot", "on"}

    @property
    def scope_set(self) -> set[str]:
        return {
            item.strip().lower()
            for item in self.scope.split(",")
            if item.strip()
        }


class MultiIntentPlannerSettings(BaseSettings):
    """Feature-flagged subtask planner for compound user questions."""

    model_config = SettingsConfigDict(
        env_prefix="MULTI_INTENT_PLANNER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mode: MultiIntentPlannerMode = "shadow"
    confidence_threshold: float = Field(default=0.72, ge=0.0, le=1.0)
    max_subtasks: int = Field(default=6, ge=2, le=8)
    timeout_seconds: float = Field(default=4.0, ge=0.5, le=30.0)
    llm_fallback_enabled: bool = False

    @property
    def enabled(self) -> bool:
        return self.mode != "off"

    @property
    def should_apply(self) -> bool:
        return self.mode in {"pilot", "on"}


class DecisionTraceSettings(BaseSettings):
    """Default-off JSONL tracing for shadow decision contract audits."""

    model_config = SettingsConfigDict(
        env_prefix="DECISION_TRACE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = False
    output_path: Path = Path("tmp/decision_traces.jsonl")
    include_answer_preview: bool = False
    max_answer_preview_chars: int = Field(default=600, ge=0, le=5000)


class SourceOwnerPolicySettings(BaseSettings):
    """Runtime source-owner evidence policy rollout settings."""

    model_config = SettingsConfigDict(
        env_prefix="SOURCE_OWNER_POLICY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mode: SourceOwnerPolicyMode = "advisory"
    min_compatible_score: float = Field(default=0.30, ge=0.0, le=1.0)


class AnswerValidationSettings(BaseSettings):
    """Final answer/evidence validation rollout settings."""

    model_config = SettingsConfigDict(
        env_prefix="ANSWER_VALIDATION_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mode: AnswerValidationMode = "shadow"


class Settings(BaseSettings):
    """Uygulama ayarlarinin kok nesnesi."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    google_ai: GoogleAISettings = Field(default_factory=GoogleAISettings)
    anthropic: AnthropicSettings = Field(default_factory=AnthropicSettings)
    llm: LLMRuntimeSettings = Field(default_factory=LLMRuntimeSettings)
    chroma: ChromaSettings = Field(default_factory=ChromaSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    rag: RAGSettings = Field(default_factory=RAGSettings)
    reranker: RerankerSettings = Field(default_factory=RerankerSettings)
    retrieval_service: RetrievalServiceSettings = Field(default_factory=RetrievalServiceSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    institution: InstitutionSettings = Field(default_factory=InstitutionSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    slack: SlackSettings = Field(default_factory=SlackSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    conversation: ConversationSettings = Field(default_factory=ConversationSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    model_cache: ModelCacheSettings = Field(default_factory=ModelCacheSettings)
    a2a: A2ASettings = Field(default_factory=A2ASettings)
    agent: AgentServiceSettings = Field(default_factory=AgentServiceSettings)
    capability_planner: CapabilityPlannerSettings = Field(
        default_factory=CapabilityPlannerSettings
    )
    multi_intent_planner: MultiIntentPlannerSettings = Field(
        default_factory=MultiIntentPlannerSettings
    )
    decision_trace: DecisionTraceSettings = Field(default_factory=DecisionTraceSettings)
    source_owner_policy: SourceOwnerPolicySettings = Field(
        default_factory=SourceOwnerPolicySettings
    )
    answer_validation: AnswerValidationSettings = Field(
        default_factory=AnswerValidationSettings
    )

    base_dir: Path = PROJECT_ROOT
    data_dir: Path = base_dir / "data"
    raw_data_dir: Path = data_dir / "raw"
    docs_dir: Path = base_dir / "docs"

    @staticmethod
    def normalize_llm_profile(profile: str | None) -> LLMSpeedProfile:
        """Desteklenen hiz/kalite profil adlarini normalize eder."""
        lowered = (profile or "").strip().lower()
        if lowered in {"fast", "balanced", "quality"}:
            return lowered  # type: ignore[return-value]
        if lowered == "hybrid_quality":
            return "quality"
        return "balanced"

    @staticmethod
    def normalize_llm_operating_profile(profile: str | None) -> LLMOperatingProfile:
        """Return the high-level provider-routing profile for observability."""
        lowered = (profile or "").strip().lower()
        if lowered in {"groq_only", "hybrid_shadow", "hybrid_quality"}:
            return lowered  # type: ignore[return-value]
        return "standard"

    def resolve_llm_model(
        self,
        *,
        role: LLMRole = "default",
        profile: str | None = None,
        provider: LLMProvider | None = None,
    ) -> str:
        """
        LLM rolune gore kullanilacak modeli cozumler.

        Cozumleme sirasi:
        1. Acik istek profili (`fast`, `quality`, `balanced`)
        2. Ayarlardaki varsayilan profil
        3. Role ozel model override'i
        4. Provider'in birincil modeli
        """
        requested_profile = self.normalize_llm_profile(profile or self.llm.profile)
        active_provider = provider or self.llm.primary_provider
        primary_model = self._resolve_provider_primary_model(active_provider)
        secondary_model = self._resolve_provider_secondary_model(active_provider)

        # Judge role bypasses profile entirely — it always uses a dedicated
        # model or falls back to the *active* provider's primary model.
        # LLM_JUDGE_MODEL is a global override that only applies to the
        # primary provider to avoid leaking model names into a different
        # provider namespace (e.g. Groq model name into Google AI).
        if role == "judge":
            if active_provider == self.llm.primary_provider and self.llm.judge_model:
                return self.llm.judge_model
            return primary_model

        if requested_profile == "fast":
            return secondary_model
        if requested_profile == "quality":
            return primary_model

        provider_override = self._resolve_provider_role_model(active_provider, role)
        if provider_override:
            return provider_override

        # Legacy LLM_* role overrides are global and usually describe the
        # primary provider. Do not leak Groq model names into Google AI
        # or another fallback provider with a different model namespace.
        if active_provider == self.llm.primary_provider:
            legacy_override = self._resolve_legacy_role_model(role)
            if legacy_override:
                return legacy_override

        if role in {"routing", "conversation"}:
            return secondary_model
        return primary_model

    def resolve_llm_provider(self, *, role: LLMRole = "default") -> LLMProvider:
        """Return the provider selected for a model role."""
        role_providers: dict[LLMRole, Optional[LLMProvider]] = {
            "routing": self.llm.routing_provider,
            "conversation": self.llm.conversation_provider,
            "query_expansion": self.llm.query_expansion_provider,
            "evidence_selection": self.llm.evidence_selection_provider,
            "final_refinement": self.llm.final_refinement_provider,
            "specialist_synthesis": self.llm.specialist_synthesis_provider,
            "global_synthesis": self.llm.global_synthesis_provider,
            "judge": self.llm.judge_provider,
            "default": None,
        }
        explicit_provider = role_providers.get(role)
        if explicit_provider:
            return explicit_provider
        operating_profile = self.normalize_llm_operating_profile(self.llm.profile)
        if operating_profile in {"groq_only", "hybrid_shadow"}:
            return self.llm.primary_provider
        if self.llm.high_value_provider and role in self._resolve_high_value_roles():
            return self.llm.high_value_provider
        return self.llm.primary_provider

    def _resolve_high_value_roles(self) -> set[LLMRole]:
        """Return roles that should use the optional high-value provider lane."""
        roles: set[LLMRole] = set()
        valid_roles = set(LLMRole.__args__)  # type: ignore[attr-defined]
        for raw_role in (self.llm.high_value_roles or "").split(","):
            role = raw_role.strip()
            if role in valid_roles:
                roles.add(role)  # type: ignore[arg-type]
        return roles

    def _resolve_legacy_role_model(self, role: LLMRole) -> Optional[str]:
        """Return old global LLM_* role override values."""
        role_overrides = {
            "routing": self.llm.routing_model,
            "conversation": self.llm.conversation_model,
            "query_expansion": self.llm.query_expansion_model,
            "evidence_selection": self.llm.evidence_selection_model,
            "final_refinement": self.llm.final_refinement_model,
            "specialist_synthesis": self.llm.specialist_synthesis_model,
            "global_synthesis": self.llm.global_synthesis_model,
            "judge": self.llm.judge_model,
            "default": None,
        }
        return role_overrides.get(role)

    def _resolve_provider_role_model(self, provider: LLMProvider, role: LLMRole) -> Optional[str]:
        """Return provider-specific role override values."""
        if provider == "openai_compatible":
            provider_settings = self.openai
        elif provider == "google_ai":
            provider_settings = self.google_ai
        elif provider == "anthropic":
            provider_settings = self.anthropic
        else:
            return None  # pragma: no cover

        role_overrides = {
            "routing": provider_settings.routing_model,
            "conversation": provider_settings.conversation_model,
            "query_expansion": provider_settings.query_expansion_model,
            "evidence_selection": provider_settings.evidence_selection_model,
            "final_refinement": provider_settings.final_refinement_model,
            "specialist_synthesis": provider_settings.specialist_synthesis_model,
            "global_synthesis": provider_settings.global_synthesis_model,
            "default": None,
        }
        return role_overrides.get(role)

    def _resolve_provider_primary_model(
        self,
        provider: LLMProvider,
    ) -> str:
        """Return the default primary model for the selected provider."""
        if provider == "openai_compatible":
            return self.openai.model
        if provider == "google_ai":
            return self.google_ai.model
        if provider == "anthropic":
            return self.anthropic.model
        return self.openai.model  # pragma: no cover

    def _resolve_provider_secondary_model(
        self,
        provider: LLMProvider,
    ) -> str:
        """Return the secondary/fast profile model for the selected provider."""
        if provider == "openai_compatible":
            return self.openai.secondary_model or self.openai.model
        if provider == "google_ai":
            return self.google_ai.secondary_model or self.google_ai.model
        if provider == "anthropic":
            return self.anthropic.secondary_model or self.anthropic.model
        return self.openai.secondary_model or self.openai.model  # pragma: no cover

    def configured_llm_models(self) -> dict[str, str]:
        """Saglik ve debug ciktilari icin cozumlenmis model haritasini dondurur."""
        def _role_model(role: LLMRole) -> str:
            provider = self.resolve_llm_provider(role=role)
            return self.resolve_llm_model(role=role, provider=provider)

        def _role_provider(role: LLMRole) -> str:
            return self.resolve_llm_provider(role=role)

        return {
            "provider": self.llm.primary_provider,
            "fallback_provider": self.llm.fallback_provider,
            "high_value_provider": self.llm.high_value_provider or "",
            "high_value_roles": ",".join(sorted(self._resolve_high_value_roles())),
            "primary": self._resolve_provider_primary_model(self.llm.primary_provider),
            "secondary": self._resolve_provider_secondary_model(self.llm.primary_provider),
            "profile": self.normalize_llm_profile(self.llm.profile),
            "operating_profile": self.normalize_llm_operating_profile(self.llm.profile),
            "routing": _role_model("routing"),
            "routing_provider": _role_provider("routing"),
            "conversation": _role_model("conversation"),
            "conversation_provider": _role_provider("conversation"),
            "query_expansion": _role_model("query_expansion"),
            "query_expansion_provider": _role_provider("query_expansion"),
            "evidence_selection": _role_model("evidence_selection"),
            "evidence_selection_provider": _role_provider("evidence_selection"),
            "final_refinement": _role_model("final_refinement"),
            "final_refinement_provider": _role_provider("final_refinement"),
            "specialist_synthesis": _role_model("specialist_synthesis"),
            "specialist_synthesis_provider": _role_provider("specialist_synthesis"),
            "specialist_synthesis_enabled": str(self.llm.specialist_synthesis_enabled),
            "global_synthesis": _role_model("global_synthesis"),
            "global_synthesis_provider": _role_provider("global_synthesis"),
            "judge": _role_model("judge"),
            "judge_provider": _role_provider("judge"),
            "main_judge_enabled": str(self.llm.main_judge_enabled),
        }

    def configured_warmup_collections(self) -> list[str]:
        """Startup warm-up icin koleksiyon listesini cozumler."""
        raw = self.server.warmup_collections
        collections = [item.strip() for item in raw.split(",") if item.strip()]
        return collections or ["student_affairs_docs", "academic_programs_docs"]


settings = Settings()


def apply_model_cache_environment() -> dict[str, str]:
    """Expose the configured project model cache to Hugging Face loaders."""
    cache = settings.model_cache
    hf_home = cache.hf_home
    hf_hub_cache = cache.hf_hub_cache
    if not cache.set_hf_env or hf_home is None or hf_hub_cache is None:
        return {}

    desired = {
        "HF_HOME": str(hf_home),
        "HF_HUB_CACHE": str(hf_hub_cache),
        "SENTENCE_TRANSFORMERS_HOME": str(hf_hub_cache),
    }
    applied: dict[str, str] = {}
    for key, value in desired.items():
        if not os.environ.get(key):
            os.environ[key] = value
            applied[key] = value
    return applied
