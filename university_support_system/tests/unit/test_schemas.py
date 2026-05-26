"""
Pydantic Şema Unit Testleri

src/db/schemas.py modülündeki iş mantığı şemalarının doğrulama testleri.
A2A protokol şemaları a2a-sdk'dan gelir ve burada test edilmez.
"""

import pytest
from pydantic import ValidationError

from src.db.schemas import (
    RAGQuery,
    RAGResult,
    RAGSource,
    RoutingResult,
    DepartmentResponse,
    AuthenticatedUserQueryRequest,
    UserQueryRequest,
    UserQueryResponse,
    ServiceHealth,
    SystemHealthResponse,
)
from src.core.constants import (
    ConfidenceLevel,
    Department,
    RoutingStrategy,
)


class TestRAGQuerySchema:
    """RAG sorgusu şema testleri."""

    def test_valid_query(self):
        """Geçerli RAG sorgusu oluşturulabilir."""
        query = RAGQuery(query="Harç borcum ne kadar?")
        assert query.query == "Harç borcum ne kadar?"
        assert query.top_k == 5
        assert query.min_similarity == 0.6

    def test_query_with_department(self):
        """Departman belirtilen sorgu oluşturulabilir."""
        query = RAGQuery(query="Burs başvurusu", department=Department.FINANCE)
        assert query.department == Department.FINANCE

    def test_empty_query_rejected(self):
        """Boş sorgu reddedilir."""
        with pytest.raises(ValidationError):
            RAGQuery(query="")

    def test_too_long_query_rejected(self):
        """Çok uzun sorgu reddedilir (500 karakter limiti)."""
        with pytest.raises(ValidationError):
            RAGQuery(query="a" * 501)

    def test_custom_top_k(self):
        """Özel top_k değeri ayarlanabilir."""
        query = RAGQuery(query="Test", top_k=10)
        assert query.top_k == 10

    def test_invalid_top_k_rejected(self):
        """Geçersiz top_k reddedilir."""
        with pytest.raises(ValidationError):
            RAGQuery(query="Test", top_k=0)


class TestRAGResultSchema:
    """RAG sonuç şema testleri."""

    def test_valid_result(self):
        """Geçerli RAG sonucu oluşturulabilir."""
        result = RAGResult(
            answer="Harç borcunuz 5000 TL'dir.",
            sources=[
                RAGSource(
                    content="Harç ödemesi dönem başı yapılır.",
                    score=0.85,
                    metadata={"source": "harc.md"},
                )
            ],
            department="finance",
            response_time_ms=120.5,
        )
        assert result.answer == "Harç borcunuz 5000 TL'dir."
        assert len(result.sources) == 1
        assert result.sources[0].score == 0.85


class TestRoutingResultSchema:
    """Yönlendirme sonucu şema testleri."""

    def test_valid_routing_result(self):
        """Geçerli yönlendirme sonucu oluşturulabilir."""
        result = RoutingResult(
            departments=[Department.FINANCE],
            confidence=0.9,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
        )
        assert result.departments == [Department.FINANCE]
        assert result.confidence == 0.9

    def test_multi_department_routing(self):
        """Birden fazla departmana yönlendirme."""
        result = RoutingResult(
            departments=[Department.FINANCE, Department.STUDENT_AFFAIRS],
            confidence=0.75,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.PARALLEL,
        )
        assert len(result.departments) == 2

    def test_invalid_confidence_rejected(self):
        """Geçersiz güven skoru reddedilir (0-1 aralığı dışı)."""
        with pytest.raises(ValidationError):
            RoutingResult(
                departments=[Department.FINANCE],
                confidence=1.5,
                confidence_level=ConfidenceLevel.HIGH,
                strategy=RoutingStrategy.DIRECT,
            )


class TestDepartmentResponseSchema:
    """Departman yanıt şema testleri."""

    def test_valid_response(self):
        """Geçerli departman yanıtı."""
        resp = DepartmentResponse(
            department=Department.STUDENT_AFFAIRS,
            answer="Ders kaydınızı OBS üzerinden gerçekleştirebilirsiniz.",
        )
        assert resp.success is True
        assert resp.error is None


class TestUserQueryRequestSchema:
    """Kullanıcı sorgusu şema testleri."""

    def test_valid_request(self):
        """Geçerli sorgu isteği oluşturulabilir."""
        request = UserQueryRequest(query="Ders kaydı yapabilir miyim?")
        assert request.query == "Ders kaydı yapabilir miyim?"
        assert request.user_id is None

    def test_request_with_user_id(self):
        """Kullanıcı ID'li istek oluşturulabilir."""
        request = UserQueryRequest(
            query="Şifremi unuttum",
            user_id="user_123",
        )
        assert request.user_id == "user_123"

    def test_authenticated_request_can_disable_cache(self):
        request = AuthenticatedUserQueryRequest(
            query="Ders kaydi ne zaman basliyor?",
            disable_cache=True,
        )

        assert request.disable_cache is True


class TestHealthCheckSchemas:
    """Health check şema testleri."""

    def test_service_health(self):
        """Servis sağlık durumu şeması."""
        health = ServiceHealth(
            name="postgresql",
            status="healthy",
            latency_ms=5.3,
        )
        assert health.name == "postgresql"
        assert health.status == "healthy"

    def test_system_health_response(self):
        """Sistem sağlık yanıtı şeması."""
        response = SystemHealthResponse(
            status="healthy",
            services=[
                ServiceHealth(name="postgresql", status="healthy", latency_ms=5.3),
                ServiceHealth(name="redis", status="healthy", latency_ms=1.2),
            ],
        )
        assert len(response.services) == 2
        assert response.timestamp is not None
