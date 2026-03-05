"""
Uygulama Sabitleri

Departman isimleri, görev tipleri, yönlendirme stratejileri ve diğer sabitler.
Enum kullanarak tip güvenliği sağlar.

NOT: A2A protokolüne ait tipler (TaskState, Message, Artifact vb.)
     resmi a2a-sdk paketinden import edilmelidir.

Kullanım:
    from src.core.constants import Department, TaskType
"""

from enum import Enum


# ── Departmanlar ─────────────────────────────────
class Department(str, Enum):
    """Sistem departmanları."""

    FINANCE = "finance"
    IT = "it"
    STUDENT_AFFAIRS = "student_affairs"

    @property
    def display_name(self) -> str:
        """Türkçe görüntüleme adı."""
        names = {
            "finance": "Finans",
            "it": "Bilgi İşlem",
            "student_affairs": "Öğrenci İşleri",
        }
        return names.get(self.value, self.value)


# ── Görev Tipleri ────────────────────────────────
class TaskType(str, Enum):
    """Ajan görev tipleri."""

    # Finans
    TUITION_QUERY = "tuition_query"           # Harç sorgulama
    SCHOLARSHIP_QUERY = "scholarship_query"    # Burs sorgulama
    PAYMENT_QUERY = "payment_query"            # Ödeme sorgulama

    # IT
    TECH_SUPPORT = "tech_support"              # Teknik destek
    EMAIL_SUPPORT = "email_support"            # E-posta sorunları
    ACCOUNT_SUPPORT = "account_support"        # Hesap işlemleri

    # Öğrenci İşleri
    COURSE_QUERY = "course_query"              # Ders sorguları
    REGISTRATION_QUERY = "registration_query"  # Kayıt işlemleri
    ACADEMIC_QUERY = "academic_query"          # Akademik durum

    # Genel
    PROCEDURE_QUERY = "procedure_query"        # Prosedür sorgusu (RAG)
    DATA_QUERY = "data_query"                  # Veri sorgusu (SQL)
    HYBRID_QUERY = "hybrid_query"              # Hibrit sorgu (RAG + SQL)


# ── İç Görev Durumları ───────────────────────────
# NOT: A2A protokolünün resmi TaskState'i a2a-sdk'dan gelir.
#      Bu enum, iç süreçler (routing, orchestration) için ek
#      durumları tanımlar ve SDK'nın TaskState'ini GENİŞLETMEZ.
class InternalTaskStatus(str, Enum):
    """İç süreç görev durumları (A2A dışı)."""

    ROUTING = "routing"              # Yönlendirilme aşamasında
    QUEUED = "queued"                # Kuyrukta bekliyor
    RETRYING = "retrying"            # Yeniden deniyor
    TIMEOUT = "timeout"              # Zaman aşımı


# ── Yönlendirme Stratejileri ─────────────────────
class RoutingStrategy(str, Enum):
    """Sorgu yönlendirme stratejileri."""

    DIRECT = "direct"                # Doğrudan tek departmana
    PARALLEL = "parallel"            # Birden fazla departmana paralel
    SEQUENTIAL = "sequential"        # Bağımlı görevler sıralı
    CLARIFICATION = "clarification"  # Kullanıcıdan netleştirme iste


# ── Güven Seviyeleri ─────────────────────────────
class ConfidenceLevel(str, Enum):
    """Yönlendirme güven seviyeleri."""

    HIGH = "high"        # >0.7 — doğrudan yönlendir
    MEDIUM = "medium"    # 0.4-0.7 — kullanıcı onayı iste
    LOW = "low"          # <0.4 — netleştirme iste


# ── Ajan Rolleri ─────────────────────────────────
class AgentRole(str, Enum):
    """Ajan rolleri."""

    MAIN_ORCHESTRATOR = "main_orchestrator"
    DEPARTMENT_ORCHESTRATOR = "department_orchestrator"
    SPECIALIST_AGENT = "specialist_agent"


# NOT: MessageRole (user/agent) artık a2a-sdk'dan gelir.
#      from a2a.types import Role


# ── Öncelik Seviyeleri ───────────────────────────
class Priority(int, Enum):
    """Görev öncelik seviyeleri."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


# ── Sabit Değerler ──────────────────────────────
# Yönlendirme eşik değerleri
ROUTING_HIGH_CONFIDENCE_THRESHOLD = 0.7
ROUTING_LOW_CONFIDENCE_THRESHOLD = 0.4
KEYWORD_MATCH_THRESHOLD = 0.6

# Kuyruk ayarları
QUEUE_MAX_RETRIES = 3
QUEUE_TTL_SECONDS = 1800  # 30 dakika
QUEUE_RETRY_DELAYS = [3, 10, 30]  # Kademeli bekleme (saniye)

# Cache ayarları
CACHE_DEFAULT_TTL = 300  # 5 dakika
CACHE_LLM_RESPONSE_TTL = 300

# Rate limiting
RATE_LIMIT_PER_USER_PER_MINUTE = 10
MAX_QUERY_LENGTH = 500

# Performans hedefleri
RAG_RESPONSE_TIME_TARGET_MS = 100
LLM_RESPONSE_TIME_TARGET_MS = 3000
E2E_RESPONSE_TIME_TARGET_MS = 5000
