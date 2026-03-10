"""
Pydantic Şemaları (Request/Response)

İş mantığı katmanı için veri doğrulama şemaları.

Not:
    Bu dosyadaki şemaların bir bölümü aktif RAG ve yönlendirme çekirdeğinde
    kullanılır; bir bölümü ise planlı veya kısmi arayüz katmanları için hazırdır.

NOT: A2A protokolüne ait tipler (Task, Message, Artifact, AgentCard vb.)
     resmi a2a-sdk paketinden kullanılmaktadır:
         from a2a.types import (
             AgentCard, Task, TaskState, Message, Artifact,
             TextPart, DataPart, FilePart, Part, Role
         )

     Bu dosyada yalnızca projemize özel iş mantığı şemaları bulunur:
     RAG, routing, departman yanıtları, kullanıcı API'si ve health check.

Kullanım:
    from src.db.schemas import RAGQuery, RAGResult, RoutingResult
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.core.constants import (
    ConfidenceLevel,
    Department,
    RoutingStrategy,
    TaskType,
)


def _utcnow() -> datetime:
    """Timezone-aware UTC zaman damgası üretir."""
    return datetime.now(timezone.utc)


# ═══════════════════════════════════════════════════
# RAG Şemaları
# ═══════════════════════════════════════════════════

class RAGQuery(BaseModel):
    """RAG sorgusu girdi şeması."""

    query: str = Field(..., min_length=1, max_length=500, description="Kullanıcı sorusu")
    department: Optional[Department] = Field(None, description="Hedef departman")
    top_k: int = Field(default=5, ge=1, le=20, description="Döndürülecek sonuç sayısı")
    min_similarity: float = Field(default=0.6, ge=0.0, le=1.0, description="Minimum benzerlik eşiği")


class RAGSource(BaseModel):
    """RAG kaynak belgesi."""

    content: str = Field(..., description="Belge içeriği")
    score: float = Field(..., description="Benzerlik skoru")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Belge meta verisi")


class RAGResult(BaseModel):
    """RAG sorgusu sonuç şeması."""

    answer: str = Field(..., description="Üretilen yanıt")
    sources: List[RAGSource] = Field(default_factory=list, description="Kaynak belgeler")
    department: Optional[str] = Field(None, description="Aranan departman")
    response_time_ms: Optional[float] = Field(None, description="Yanıt süresi (ms)")


# ═══════════════════════════════════════════════════
# Yönlendirme Şemaları
# ═══════════════════════════════════════════════════

class RoutingResult(BaseModel):
    """Sorgu yönlendirme sonucu."""

    departments: List[Department] = Field(..., description="Hedef departmanlar")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Güven skoru")
    confidence_level: ConfidenceLevel = Field(..., description="Güven seviyesi")
    strategy: RoutingStrategy = Field(..., description="Yönlendirme stratejisi")
    reasoning: Optional[str] = Field(None, description="Yönlendirme gerekçesi")
    task_type: Optional[TaskType] = Field(None, description="Belirlenen görev tipi")


# ═══════════════════════════════════════════════════
# Departman Yanıt Şeması
# ═══════════════════════════════════════════════════

class DepartmentResponse(BaseModel):
    """Departman bazlı işlem sonucunu taşıyan ortak yanıt modeli."""

    department: Department
    answer: str
    sources: List[RAGSource] = Field(default_factory=list)
    db_data: Optional[Dict[str, Any]] = None
    success: bool = True
    response_time_ms: Optional[float] = None
    error: Optional[str] = None


# ═══════════════════════════════════════════════════
# Dış Arayüz Şemaları
# ═══════════════════════════════════════════════════

class UserQueryRequest(BaseModel):
    """Kullanıcı sorgusu girdi şeması."""

    query: str = Field(..., min_length=1, max_length=500, description="Kullanıcı sorusu")
    user_id: Optional[str] = Field(None, description="Kullanıcı ID")
    context_id: Optional[str] = Field(None, description="Konuşma bağlam ID")


class UserQueryResponse(BaseModel):
    """Kullanıcı sorgusu yanıt şeması."""

    answer: str = Field(..., description="Nihai yanıt")
    departments_involved: List[str] = Field(default_factory=list)
    sources: List[RAGSource] = Field(default_factory=list)
    response_time_ms: float
    query_id: str


# ═══════════════════════════════════════════════════
# Health Check Şemaları
# ═══════════════════════════════════════════════════

class ServiceHealth(BaseModel):
    """Servis sağlık durumu."""

    name: str
    status: str  # "healthy" | "unhealthy"
    latency_ms: Optional[float] = None
    details: Optional[str] = None


class SystemHealthResponse(BaseModel):
    """Sistem genel sağlık durumu."""

    status: str  # "healthy" | "degraded" | "unhealthy"
    services: List[ServiceHealth]
    timestamp: datetime = Field(default_factory=_utcnow)
