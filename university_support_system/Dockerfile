# syntax=docker/dockerfile:1.7
ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

ARG INSTALL_BUILD_TOOLS=false
ARG TORCH_VARIANT=cpu
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    mkdir -p /models/huggingface/hub \
    && if [ "$INSTALL_BUILD_TOOLS" = "true" ]; then \
        apt-get update \
        && apt-get install -y --no-install-recommends build-essential curl \
        && rm -rf /var/lib/apt/lists/*; \
    fi

COPY requirements.txt pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    python -m pip install --upgrade pip \
    && if [ "$TORCH_VARIANT" = "cpu" ]; then \
        python -c "from pathlib import Path; source = Path('requirements.txt').read_text(encoding='utf-8'); source = source.replace('torch==2.6.0', 'torch==2.6.0+cpu'); Path('/tmp/requirements-docker.txt').write_text(source, encoding='utf-8')" \
        && python -m pip install --extra-index-url https://download.pytorch.org/whl/cpu -r /tmp/requirements-docker.txt; \
    else \
        python -c "from pathlib import Path; lines = Path('requirements.txt').read_text(encoding='utf-8').splitlines(); filtered = [line for line in lines if not line.startswith('torch==')]; Path('/tmp/requirements-docker.txt').write_text('\n'.join(filtered) + '\n', encoding='utf-8')" \
        && python -m pip install -r /tmp/requirements-docker.txt; \
    fi

ENV HF_HOME=/models/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/models/huggingface/hub

COPY alembic.ini ./
COPY migrations ./migrations
COPY scripts ./scripts
COPY src ./src
COPY data ./data

ARG APP_VERSION=1.0.0
ARG BUILD_ID=dev
ARG BUILD_TIMESTAMP=unknown
ARG GIT_SHA=unknown
ARG IMAGE_REF=university_support_system-app:latest

# Build metadata changes every rollout; keep it after dependency layers so
# changing BUILD_ID/timestamp does not force apt/pip reinstall work.
ENV SERVER_APP_VERSION=${APP_VERSION} \
    SERVER_BUILD_ID=${BUILD_ID} \
    SERVER_BUILD_TIMESTAMP=${BUILD_TIMESTAMP} \
    SERVER_GIT_SHA=${GIT_SHA} \
    SERVER_IMAGE_REF=${IMAGE_REF}

CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
