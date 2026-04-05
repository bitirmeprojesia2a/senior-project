"""
Uygulama Sabitleri

Departman isimleri, görev tipleri, yönlendirme stratejileri ve diğer sabitler.
Enum kullanarak tip güvenliği sağlar.

Not:
    Bu dosyadaki sabitlerin bir bölümü aktif çekirdekte doğrudan kullanılır.
    Bir bölümü ise planlı veya kısmi entegrasyon katmanları için hazır tutulur.

NOT: A2A protokolüne ait tipler (TaskState, Message, Artifact vb.)
     resmi a2a-sdk paketinden import edilmelidir.

Kullanım:
    from src.core.constants import Department, TaskType
"""

from dataclasses import dataclass
from enum import Enum


# ── Departmanlar ─────────────────────────────────
class Department(str, Enum):
    """Mevcut çekirdek sözleşmede tanımlı departmanlar."""

    FINANCE = "finance"
    STUDENT_AFFAIRS = "student_affairs"
    ACADEMIC_PROGRAMS = "academic_programs"

    @property
    def display_name(self) -> str:
        """Türkçe görüntüleme adı."""
        return get_department_config(self).display_name

@dataclass(frozen=True)
class DepartmentConfig:
    """Departmanın tüm çekirdek tanım bilgisini tek yerde tutar."""

    display_name: str
    routing_description: str
    keywords: tuple[str, ...]
    source_dirs: tuple[str, ...] = ()


# Yönlendirme anahtar kelimeleri: aynı soruda birden fazla departman skoru çıkabilir;
# DepartmentRouter en yüksek skoru ve eşik farkını kullanır; belirsizlikte LLM veya PARALLEL devreye girer.
# Ayrım mantığı: Öğrenci işleri = idari süreç (kayıt, sınav, staj, not, transkript, mezuniyet…).
# Akademik programlar = müfredat kuralı (önkoşul, AKTS, yönerge, yarıyıl, seçmeli, ders kodu).
# "ders" tek başına eklenmedi; "dersler/dersleri" çoğunlukla müfredat/liste bağlamı için kullanılır.
# "ders kaydı" tipi ifadeler kayıt/kayd ile öğrenci işlerine gider (akademik skor genelde düşük kalır).
DEPARTMENT_CONFIGS: dict[Department, DepartmentConfig] = {
    Department.FINANCE: DepartmentConfig(
        display_name="Finans",
        routing_description="Harç, burs, yurt ödemeleri, dekont, taksitlendirme ile ilgili sorular.",
        keywords=("harç", "ucret", "ücret", "burs", "odeme", "ödeme", "dekont", "taksit"),
    ),
    Department.STUDENT_AFFAIRS: DepartmentConfig(
        display_name="Öğrenci İşleri",
        routing_description="Ders kaydı, akademik takvim, notlar, yatay/dikey geçiş, diploma ve staj işlemleri.",
        keywords=(
            "ders kaydi", "ders kaydı", "kayit donemi", "kayıt dönemi", "akademik takvim",
            "kayit", "kayıt", "kayd", "not", "gno", "transkript", "mezuniyet", "diploma",
            "bagil", "bağıl", "yaz okulu",
            "yatay", "dikey", "staj", "sinav", "sınav", "itiraz", "devamsızlık", "devamsizlik",
            "muafiyet", "intibak",
        ),
    ),
    Department.ACADEMIC_PROGRAMS: DepartmentConfig(
        display_name="Akademik Programlar",
        routing_description="Müfredat, önkoşul, ders planı, AKTS, ÇAP/YAP, Erasmus ve akademik kurallar.",
        keywords=(
            "mufredat", "müfredat", "ders icerigi", "ders içeriği",
            "akts", "ects", "kredi",
            "onkosul", "önkoşul", "on kosul", "ön koşul", "on sart", "ön şart",
            "yarimyil", "yarıyıl", "yarim yil",
            "secmeli", "seçmeli", "teknik", "zorunlu",
            "dersler", "dersleri",
            "yonetmelik", "yönetmelik", "yonerge", "yönerge",
            "politika", "prosedur", "prosedür", "genelge",
            "cap", "çap", "yandal", "yan dal",
            "erasmus", "uluslararasi", "uluslararası", "yabanci", "yabancı",
            "ikamet", "denklik", "tomer", "tömer", "yos", "yös", "kontenjan",
            "azami", "bütünleme", "butunleme", "devam zorunlulugu", "devam zorunluluğu", "not sistemi",
        ),
    ),
}


DEPARTMENT_ALIASES: dict[str, str] = {}


def normalize_department_value(department: Department | str) -> str:
    """Departman veya alias değerini resmi departman değerine çevirir."""
    department_value = department.value if isinstance(department, Department) else department
    return DEPARTMENT_ALIASES.get(department_value, department_value)


def get_department_config(department: Department | str) -> DepartmentConfig:
    """Departman ayarlarını döndürür."""
    normalized = department if isinstance(department, Department) else Department(normalize_department_value(department))
    return DEPARTMENT_CONFIGS[normalized]


def department_values() -> list[str]:
    """CLI ve şema seçimleri için resmi departman değerleri."""
    return [department.value for department in Department]


def known_department_directory_names() -> set[str]:
    """Kaynak klasörlerinde tanınacak departman klasör adları."""
    names: set[str] = set()
    for department in Department:
        config = get_department_config(department)
        names.add(department.value)
        names.update(config.source_dirs)
    return names


def build_department_routing_descriptions() -> list[str]:
    """Prompt üretmek için departman açıklamalarını döndürür."""
    return [
        f'- "{department.value}": {get_department_config(department).routing_description}'
        for department in Department
    ]


def collection_name_for_department(department: Department | str) -> str:
    """Departman adına göre ChromaDB koleksiyon adını üretir."""
    return f"{normalize_department_value(department)}_docs"


# ── Görev Tipleri ────────────────────────────────
class TaskType(str, Enum):
    """Ajan görev tipleri."""

    # Finans
    TUITION_QUERY = "tuition_query"           # Harç sorgulama
    SCHOLARSHIP_QUERY = "scholarship_query"    # Burs sorgulama
    PAYMENT_QUERY = "payment_query"            # Ödeme sorgulama

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
    """Hazır tutulan ajan rolleri."""

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

# RAG direkt yanıt eşikleri (LLM bypass)
RAG_DIRECT_SCORE_THRESHOLD = 0.45
RAG_DIRECT_MIN_CONTENT_LEN = 60

# Kuyruk ayarları
# Not: Bu sabitler planlı veya kısmi kuyruk entegrasyonları için korunur.
QUEUE_MAX_RETRIES = 3
QUEUE_TTL_SECONDS = 1800  # 30 dakika
QUEUE_RETRY_DELAYS = [3, 10, 30]  # Kademeli bekleme (saniye)

# Önbellek ayarları
# Not: Aktif retrieval önbelleği şu anda retriever içinde in-memory çalışır.
CACHE_DEFAULT_TTL = 300  # 5 dakika
CACHE_LLM_RESPONSE_TTL = 300

# Rate limiting
RATE_LIMIT_PER_USER_PER_MINUTE = 10
MAX_QUERY_LENGTH = 500

# Performans hedefleri
RAG_RESPONSE_TIME_TARGET_MS = 100
LLM_RESPONSE_TIME_TARGET_MS = 3000
E2E_RESPONSE_TIME_TARGET_MS = 5000
