"""
Pydantic semalari.

Bu dosya RAG, routing, auth ve API seviyesinde kullanilan ortak veri
dogrulama modellerini tutar.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.core.constants import ConfidenceLevel, Department, RoutingStrategy, TaskType


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RAGQuery(BaseModel):
    """RAG sorgusu girdi modeli."""

    query: str = Field(..., min_length=1, max_length=500, description="Kullanici sorusu")
    department: Optional[Department] = Field(None, description="Hedef departman")
    top_k: int = Field(default=5, ge=1, le=20, description="Dondurulecek sonuc sayisi")
    min_similarity: float = Field(default=0.6, ge=0.0, le=1.0, description="Minimum benzerlik esigi")


class RAGSource(BaseModel):
    """RAG kaynak parcasi."""

    content: str = Field(..., description="Kaynak icerigi")
    score: float = Field(..., description="Benzerlik skoru")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Kaynak meta verisi")


class RAGResult(BaseModel):
    """RAG sorgu sonucu."""

    answer: str = Field(..., description="Uretilen yanit")
    sources: list[RAGSource] = Field(default_factory=list, description="Kaynaklar")
    department: Optional[str] = Field(None, description="Aranan departman")
    response_time_ms: Optional[float] = Field(None, description="Yanit suresi")


class RoutingResult(BaseModel):
    """Sorgu yonlendirme sonucu."""

    departments: list[Department] = Field(..., description="Hedef departmanlar")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Guven skoru")
    confidence_level: ConfidenceLevel = Field(..., description="Guven seviyesi")
    strategy: RoutingStrategy = Field(..., description="Yonlendirme stratejisi")
    reasoning: Optional[str] = Field(None, description="Yonlendirme gerekcesi")
    task_type: Optional[TaskType] = Field(None, description="Belirlenen gorev tipi")


class DepartmentResponse(BaseModel):
    """Departman bazli ortak yanit modeli."""

    department: Department
    answer: str
    sources: list[RAGSource] = Field(default_factory=list)
    db_data: Optional[dict[str, Any]] = None
    success: bool = True
    response_time_ms: Optional[float] = None
    error: Optional[str] = None


class UserQueryRequest(BaseModel):
    """Kullanici sorgusu girdi semasi."""

    query: str = Field(..., min_length=1, max_length=500, description="Kullanici sorusu")
    user_id: Optional[str] = Field(None, description="Kullanici kimligi")
    context_id: Optional[str] = Field(None, description="Konusma baglam kimligi")


class AuthenticatedUserQueryRequest(UserQueryRequest):
    """Kimlik baglamini da tasiyabilen kullanici sorgusu semasi."""

    student_id: Optional[int] = Field(None, description="Dogrulanmis ogrenci veritabani kimligi")
    is_authenticated: bool = Field(False, description="Kimlik dogrulama durumu")
    session_token: Optional[str] = Field(None, description="Dogrulama oturum anahtari")
    slack_user_id: Optional[str] = Field(None, description="Slack kullanici kimligi")


class UserQueryResponse(BaseModel):
    """Kullanici sorgusu yanit semasi."""

    answer: str = Field(..., description="Nihai yanit")
    departments_involved: list[str] = Field(default_factory=list)
    sources: list[RAGSource] = Field(default_factory=list)
    response_time_ms: float
    query_id: str


class OTPRequestPayload(BaseModel):
    """Ogrenci icin yeni OTP isteme semasi."""

    student_number: str = Field(..., min_length=4, max_length=20)
    slack_user_id: Optional[str] = None


class OTPRequestResponse(BaseModel):
    """OTP isteme yaniti."""

    success: bool
    message: str
    student_number: Optional[str] = None
    masked_email: Optional[str] = None
    expires_at: Optional[str] = None
    delivery_channel: Optional[str] = None
    otp_preview_code: Optional[str] = None


class OTPVerifyPayload(BaseModel):
    """OTP kodu dogrulama semasi."""

    student_number: str = Field(..., min_length=4, max_length=20)
    otp_code: str = Field(..., min_length=4, max_length=12)
    slack_user_id: Optional[str] = None


class OTPVerifyResponse(BaseModel):
    """OTP dogrulama yaniti."""

    success: bool
    message: str
    student_id: Optional[int] = None
    student_number: Optional[str] = None
    full_name: Optional[str] = None
    is_authenticated: bool = False
    session_token: Optional[str] = None
    expires_at: Optional[str] = None


class AuthResolvePayload(BaseModel):
    """Session veya Slack kimliginden auth baglami cozumleme semasi."""

    session_token: Optional[str] = None
    slack_user_id: Optional[str] = None


class AuthResolveResponse(BaseModel):
    """Cozumlenmis auth baglami yaniti."""

    is_authenticated: bool
    student_id: Optional[int] = None
    student_number: Optional[str] = None
    full_name: Optional[str] = None
    slack_user_id: Optional[str] = None
    session_token: Optional[str] = None
    expires_at: Optional[str] = None


class LogoutPayload(BaseModel):
    """Oturum kapatma semasi."""

    session_token: str = Field(..., min_length=8)


class LogoutResponse(BaseModel):
    """Oturum kapatma yaniti."""

    success: bool
    message: str


class OfficeContactResponse(BaseModel):
    """Ofis iletisim bilgisi cikti semasi."""

    unit_name: str
    department: str
    person_name: Optional[str] = None
    title: Optional[str] = None
    phone_ext: Optional[str] = None
    email: Optional[str] = None
    related_agents: list[str] = Field(default_factory=list)


class ServiceHealth(BaseModel):
    """Servis saglik durumu."""

    name: str
    status: str
    latency_ms: Optional[float] = None
    details: Optional[str] = None


class SystemHealthResponse(BaseModel):
    """Sistem genel saglik durumu."""

    status: str
    services: list[ServiceHealth]
    timestamp: datetime = Field(default_factory=_utcnow)
