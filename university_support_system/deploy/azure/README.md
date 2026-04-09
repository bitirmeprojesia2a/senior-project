# Azure CPU ve GPU Runtime Profilleri

Bu klasor, ayni GPU destekli Azure VM uzerinde iki farkli API profili calistirmak icin ornek dosyalar icerir:

- `api.cpu.env.example`
- `api.gpu.env.example`

Amac:

- `cpu` profili ile daha hafif ve karsilastirma odakli calisma
- `gpu` profili ile hizli embedding, reranker ve gerekirse daha buyuk model kullanimi

## 1. Ornek env dosyalarini kopyala

Azure SSH:

```bash
cd ~/app
cp deploy/azure/api.cpu.env.example deploy/azure/api.cpu.env
cp deploy/azure/api.gpu.env.example deploy/azure/api.gpu.env
chmod +x scripts/run_api_profile.sh
```

## 2. CPU runtime

```bash
tmux new -s uss-cpu
cd ~/app
scripts/run_api_profile.sh deploy/azure/api.cpu.env
```

## 3. GPU runtime

```bash
tmux new -s uss-gpu
cd ~/app
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d ollama
scripts/run_api_profile.sh deploy/azure/api.gpu.env
```

## 4. Health uzerinden dogrulama

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8001/health`

`app.runtime` alaninda su bilgileri gorunmelidir:

- `label`
- `port`
- `embedding_device`
- `reranker_device`
- `ollama_host`

## 5. Onemli not

Mevcut varsayilan CPU profilinde `OLLAMA_HOST` degeri `127.0.0.1:11434` olarak gelir ve var olan Ollama servisine baglanir.

Tam CPU ve tam GPU LLM karsilastirmasi yapmak isterseniz, daha sonra `cpu` profilindeki `OLLAMA_HOST` degerini CPU odakli ayri bir Ollama sunucusuna yonlendirebilirsiniz.
