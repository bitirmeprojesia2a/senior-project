#!/bin/sh
set -eu

ollama serve &
OLLAMA_PID=$!

cleanup() {
  if kill -0 "$OLLAMA_PID" 2>/dev/null; then
    kill "$OLLAMA_PID" 2>/dev/null || true
    wait "$OLLAMA_PID" 2>/dev/null || true
  fi
}

trap cleanup INT TERM

wait_for_ollama() {
  echo "Ollama servisi bekleniyor..."
  until ollama list >/dev/null 2>&1; do
    if ! kill -0 "$OLLAMA_PID" 2>/dev/null; then
      echo "Ollama sunucusu beklenmedik sekilde durdu." >&2
      exit 1
    fi
    sleep 2
  done
}

pull_models() {
  MODELS_CSV="${OLLAMA_PRELOAD_MODELS:-}"
  if [ -z "$MODELS_CSV" ]; then
    return 0
  fi

  OLD_IFS="$IFS"
  IFS=','
  set -- $MODELS_CSV
  IFS="$OLD_IFS"

  PULLED_MODELS=""
  for model in "$@"; do
    trimmed_model=$(printf "%s" "$model" | tr -d '[:space:]')
    if [ -z "$trimmed_model" ]; then
      continue
    fi
    case ",$PULLED_MODELS," in
      *,"$trimmed_model",*)
        continue
        ;;
    esac
    echo "Ollama modeli yukleniyor: $trimmed_model"
    ollama pull "$trimmed_model"
    PULLED_MODELS="${PULLED_MODELS},${trimmed_model}"
  done
}

wait_for_ollama
pull_models
wait "$OLLAMA_PID"
