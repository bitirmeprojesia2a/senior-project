#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Kullanim: scripts/run_api_profile.sh <env-dosyasi>"
  echo "Ornek: scripts/run_api_profile.sh deploy/azure/api.cpu.env"
  exit 1
fi

ENV_FILE="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ ! -f "${ROOT_DIR}/${ENV_FILE}" && ! -f "${ENV_FILE}" ]]; then
  echo "Env dosyasi bulunamadi: ${ENV_FILE}"
  exit 1
fi

if [[ -f "${ROOT_DIR}/${ENV_FILE}" ]]; then
  RESOLVED_ENV_FILE="${ROOT_DIR}/${ENV_FILE}"
else
  RESOLVED_ENV_FILE="${ENV_FILE}"
fi

cd "${ROOT_DIR}"
source .venv/bin/activate

set -a
source "${RESOLVED_ENV_FILE}"
set +a

echo "Runtime baslatiliyor: ${SERVER_RUNTIME_LABEL:-default}"
echo "Port: ${SERVER_PORT:-8000}"
echo "Embedding device: ${EMBEDDING_DEVICE:-auto}"
echo "Reranker device: ${RERANKER_DEVICE:-auto}"
echo "Ollama host: ${OLLAMA_HOST:-http://localhost:11434}"

exec uvicorn src.api.main:app --host "${SERVER_HOST:-0.0.0.0}" --port "${SERVER_PORT:-8000}"
