# ================================================
# Üniversite Kurumsal Destek Sistemi - Makefile
# ================================================
# Kullanım: make <komut>
# Yardım:   make help

.PHONY: help setup install test lint format db-migrate db-downgrade seed docker-up docker-down clean

# ── Yardım ──────────────────────────────────────
help: ## Kullanılabilir komutları listeler
	@echo.
	@echo   Kullanilabilir Komutlar:
	@echo   ──────────────────────────────────────
	@echo   make setup        - Ilk kurulum (venv + bagimliliklar)
	@echo   make install      - Bagimliliklari kur
	@echo   make test         - Tum testleri calistir
	@echo   make test-unit    - Sadece unit testleri calistir
	@echo   make test-cov     - Coverage ile testleri calistir
	@echo   make lint         - Kod kalitesi kontrolu
	@echo   make format       - Kodu formatla
	@echo   make db-migrate   - Veritabani migration uygula
	@echo   make db-revision  - Yeni migration dosyasi olustur
	@echo   make seed         - Test verisi yukle
	@echo   make docker-up    - Docker servisleri baslat
	@echo   make docker-down  - Docker servisleri durdur
	@echo   make clean        - Gecici dosyalari temizle
	@echo.

# ── Kurulum ─────────────────────────────────────
setup: ## İlk kurulum
	python -m venv venv
	venv\Scripts\activate && pip install -r requirements-dev.txt
	copy .env.example .env
	@echo Kurulum tamamlandi! .env dosyasini duzenleyin.

install: ## Bağımlılıkları kur (geliştirme)
	pip install -r requirements-dev.txt

install-prod: ## Sadece runtime bağımlılıkları kur
	pip install -r requirements.txt

# ── Test ────────────────────────────────────────
test: ## Tüm testleri çalıştır
	python -m pytest tests/ -v --tb=short

test-unit: ## Sadece unit testleri çalıştır
	python -m pytest tests/unit/ -v --tb=short

test-integration: ## Entegrasyon testlerini çalıştır (ChromaDB gerekli)
	python -m pytest tests/integration/ -v --tb=short

evaluate: ## RAG değerlendirme raporu üret (ChromaDB gerekli)
	python scripts/evaluate_rag.py

test-cov: ## Coverage ile testleri çalıştır
	python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

# ── Kod Kalitesi ────────────────────────────────
lint: ## Linting kontrolleri
	python -m flake8 src/ tests/ --max-line-length=120
	python -m mypy src/ --ignore-missing-imports

format: ## Kodu formatla (black + isort)
	python -m black src/ tests/ --line-length=120
	python -m isort src/ tests/ --profile=black

# ── Veritabanı ──────────────────────────────────
db-migrate: ## Migration uygula
	python -m alembic upgrade head

db-downgrade: ## Son migration'ı geri al
	python -m alembic downgrade -1

db-revision: ## Yeni migration dosyası oluştur (MSG="açıklama" ile kullan)
	python -m alembic revision --autogenerate -m "$(MSG)"

seed: ## Test verisi yükle
	python scripts/seed_data.py

# ── Docker ──────────────────────────────────────
docker-up: ## Docker servisleri başlat
	docker compose up -d

docker-down: ## Docker servisleri durdur
	docker compose down

docker-logs: ## Docker loglarını göster
	docker compose logs -f

docker-restart: ## Docker servisleri yeniden başlat
	docker compose down && docker compose up -d

# ── Temizlik ────────────────────────────────────
clean: ## Geçici dosyaları temizle
	if exist __pycache__ rmdir /s /q __pycache__
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist .mypy_cache rmdir /s /q .mypy_cache
	if exist htmlcov rmdir /s /q htmlcov
	if exist .coverage del .coverage
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
