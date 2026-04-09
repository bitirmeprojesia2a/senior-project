# Azure VM Runbook

Bu dokuman, projenin Azure uzerinde bastan sona nasil ayağa kaldirilacagini ve daha sonra nasil yeniden erisilecegini tek yerde toplar.

Bu runbook mevcut Azure kurulumu baz alinarak hazirlandi:

- Abonelik: `Azure for Students`
- VM: `vm-uss-gpu-01`
- Resource group: `rg-uss-azure`
- Bolge: `Switzerland North`
- VM boyutu: `Standard_D4s_v3`
- Isletim sistemi: `Ubuntu 24.04`

## 1. Mevcut Kurulum Ozet

Azure uzerinde su bilesenler calisacak sekilde kurulum yapildi:

- Ubuntu tabanli bir sanal makine
- Docker
- `postgres`, `redis`, `chromadb`, `ollama` servisleri
- Python sanal ortami (`.venv`)
- FastAPI uygulamasi

Canli uygulama dizini:

```bash
~/app
```

## 2. Neden Git Clone Kullanilmadi

Repo private oldugu icin Azure VM uzerinden dogrudan `git clone` sirasinda GitHub kimlik dogrulamasi istendi.

Bu nedenle kurulum su yolla yapildi:

1. Proje Windows uzerinde zip haline getirildi
2. `scp` ile Azure VM'e kopyalandi
3. VM uzerinde `~/app` altina acildi

Bu nedenle VM uzerindeki proje dizini bir Git calisma kopyasi degildir. Guncelleme gerekiyorsa ayni zip + `scp` akisi tekrar uygulanir.

## 3. Windows'tan Azure VM'e Baglanma

SSH anahtar dosyasi Windows tarafinda saklanir.

Ornek dizin:

```powershell
C:\Users\ÖMER FARUK DERİN\Desktop\önemli
```

Anahtar dosyasini otomatik bulmak icin:

```powershell
$key = (Get-ChildItem "C:\Users\ÖMER FARUK DERİN\Desktop\önemli\*.pem" | Select-Object -First 1 -ExpandProperty FullName)
```

VM'e baglanmak icin:

```powershell
ssh -i $key azureuser@51.103.219.2
```

Ilk baglantida host key sorusu gelirse:

```text
yes
```

## 4. API'ye Tarayicidan Guvenli Erisim

API portu dis dunyaya acilmadi. Bu bilincli olarak boyle birakildi.

Tarayicidan erismek icin Windows tarafinda SSH tuneli kullanilir:

```powershell
$key = (Get-ChildItem "C:\Users\ÖMER FARUK DERİN\Desktop\önemli\*.pem" | Select-Object -First 1 -ExpandProperty FullName)
ssh -i $key -L 8000:127.0.0.1:8000 azureuser@51.103.219.2
```

Ardindan tarayicidan su adresler acilir:

- `http://localhost:8000/`
- `http://localhost:8000/health`
- `http://localhost:8000/docs`

## 5. Ilk Kurulum Sirasi

Bu bolum, ayni kurulumun sifirdan tekrar edilmesi gerekirse kullanilir.

### 5.1 Temel paketler

Azure SSH oturumunda:

```bash
sudo apt update
sudo apt install -y git curl ca-certificates gnupg lsb-release unzip build-essential python3-venv python3-pip tmux
```

### 5.2 Docker kurulumu

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

Kontrol:

```bash
docker --version
docker compose version
```

### 5.3 Projeyi Windows'tan zip ile tasima

Bu komutlar Windows PowerShell uzerinde calistirilir:

```powershell
$src = "C:\Users\ÖMER FARUK DERİN\Desktop\bitirme projesi\university_support_system\university_support_system"
$stage = "$env:TEMP\uss-azure-upload"
$zip = "C:\Users\ÖMER FARUK DERİN\Desktop\önemli\uss-azure-upload.zip"

Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $stage | Out-Null

robocopy $src $stage /E /XD venv .git .pytest_cache .pytest-run .pytest-tmp .pytest_tmp .codex_pytest_tmp /XF .coverage .env

Remove-Item $zip -Force -ErrorAction SilentlyContinue
Compress-Archive -Path "$stage\*" -DestinationPath $zip -Force

$key = (Get-ChildItem "C:\Users\ÖMER FARUK DERİN\Desktop\önemli\*.pem" | Select-Object -First 1 -ExpandProperty FullName)
scp -i $key $zip azureuser@51.103.219.2:~/
```

Ardindan Azure SSH oturumunda:

```bash
mkdir -p ~/app
unzip -q ~/uss-azure-upload.zip -d ~/app
cd ~/app
```

### 5.4 Veri klasoru izinleri

Zip acildiktan sonra `data/raw` altinda izin sorunu gorulurse:

```bash
sudo chown -R azureuser:azureuser ~/app/data
chmod -R u+rwX,go-rwx ~/app/data
```

### 5.5 Python sanal ortami

```bash
cd ~/app
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 6. Azure CPU VM Icin Kullanilan .env Ayarlari

Mevcut VM GPU'suz oldugu icin uygulama daha hafif bir profille calistirildi.

`.env.example` dosyasindan `.env` olusturulduktan sonra bu satirlar guncellendi:

```dotenv
OLLAMA_MODEL=qwen2.5:1.5b
OLLAMA_SECONDARY_MODEL=qwen2.5:1.5b
OLLAMA_PRELOAD_MODELS=qwen2.5:1.5b

LLM_PROFILE=fast
LLM_ROUTING_MODEL=qwen2.5:1.5b
LLM_CONVERSATION_MODEL=qwen2.5:1.5b

EMBEDDING_DEVICE=cpu
RERANKER_DEVICE=cpu
RERANKER_BATCH_SIZE=4

SERVER_DEBUG=false
CONVERSATION_REWRITE_WITH_LLM=false

EMBEDDING_LOCAL_FILES_ONLY=false
RERANKER_LOCAL_FILES_ONLY=false
```

Son iki satir ozellikle kritiktir. Azure VM uzerinde `BAAI/bge-m3` ve reranker modeli indirilebilsin diye `local_files_only` kapatildi.

## 7. Docker Servislerini Baslatma

```bash
cd ~/app
docker compose up -d
docker compose ps
docker compose logs --tail=50 ollama
```

Beklenen servisler:

- `uni_postgres`
- `uni_redis`
- `uni_chromadb`
- `uni_ollama`

## 8. Veritabani Migration

```bash
cd ~/app
source .venv/bin/activate
python -m alembic upgrade head
python -m alembic current
```

Beklenen sonuc:

```text
<latest-revision> (head)
```

## 9. Structured Seed Verileri

Azure uzerinde sadece indeksleme yapmak yetmez. Su komutlar PostgreSQL icindeki
structured verileri doldurur:

```bash
cd ~/app
source .venv/bin/activate
python -m scripts.seed_curriculum_data
python -m scripts.seed_synthetic_data
```

Bu adim ozellikle su sorgular icin gereklidir:

- `BIL104 dersinin on kosulu nedir?`
- `1. yariyil dersleri nelerdir?`
- kayit yenileme / aktif donem sorulari
- harc / burs sorulari

Not:

- `seed_synthetic_data` demo duyuru ve ofis iletisim kayitlari da ekler.
- Bu kayitlar demo fixture niteligindedir; gercek ortama geciste kurumsal kaynaklarla degistirilmelidir.

## 10. Indeksleme Komutlari

Uygulamanin anlamli sonuc vermesi icin dokumanlarin Azure VM uzerinde yeniden indekslenmesi gerekir.

Oncesinde:

```bash
cd ~/app
source .venv/bin/activate
```

### 10.1 Student Affairs

```bash
python scripts/index_documents.py --reindex
```

### 10.2 Academic Programs

```bash
python scripts/index_documents.py --source data/raw/academic_programs --collection academic_programs_docs --reindex
```

### 10.3 Finance

```bash
python scripts/index_documents.py --source data/raw/finance --collection finance_docs --reindex
```

Notlar:

- CPU uzerinde embedding islemleri yavas olabilir
- ilk calistirmada Hugging Face modelleri indirilecegi icin sure uzayabilir
- `mup_fakülte_kurulu_kararı.pdf` benzeri bozuk PDF'ler loglanip atlanabilir; bu beklenen davranistir

## 11. API'yi Ayaga Kaldirma

API'nin SSH kapaninca dusmemesi icin `tmux` kullanildi.

### 11.1 Yeni tmux oturumu acma

```bash
tmux new -s uss
```

### 11.2 API baslatma

```bash
cd ~/app
source .venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### 11.3 tmux'tan cikmadan oturumu arka plana alma

Tusa sirayla bas:

```text
Ctrl+b
d
```

### 11.4 Geri baglanma

```bash
tmux attach -t uss
```

Var olan tmux oturumlarini listelemek icin:

```bash
tmux ls
```

## 11. API Saglik Kontrolu

Windows tarafinda SSH tuneli acildiktan sonra:

- `http://localhost:8000/`
- `http://localhost:8000/health`
- `http://localhost:8000/docs`

Saglik ciktisinda `ollama` ve uygulama `healthy` gorunmelidir.

## 12. Kod Guncellemesi Sonrasi Ne Yapilacak

VM uzerindeki proje dizini bir Git calisma kopyasi olmadigi icin, kod guncellemesi yapildiginda dosyalar Windows tarafindan `scp` ile tek tek veya zip ile yeniden gonderilir.

### 12.1 Windows'tan tek dosya guncelleme

Ornek:

```powershell
$key = (Get-ChildItem "$HOME\Desktop\önemli\*.pem" | Select-Object -First 1 -ExpandProperty FullName)
$root = "$HOME\Desktop\bitirme projesi\university_support_system\university_support_system"

scp -i "$key" "$root\src\agents\base.py" azureuser@51.103.219.2:~/app/src/agents/
scp -i "$key" "$root\src\orchestrators\main.py" azureuser@51.103.219.2:~/app/src/orchestrators/
```

Not:

- Bu `scp` komutlari Windows PowerShell uzerinde calistirilir
- `src/` altindaki dosyalari Azure VM'de birebir ayni klasore gondermek gerekir
- Dosya sayisi azsa tek tek `scp` en guvenli yoldur

### 12.1.b Toplu guncelleme (cok sayida dosya degistiysa)

Yerelde degisen dosya sayisi fazlaysa proje yeniden ziplenip Azure'a tekrar gonderilebilir.

Windows PowerShell:

```powershell
$src = "$HOME\Desktop\bitirme projesi\university_support_system\university_support_system"
$stage = "$env:TEMP\uss-azure-upload"
$zip = "$HOME\Desktop\önemli\uss-azure-upload.zip"
$key = (Get-ChildItem "$HOME\Desktop\önemli\*.pem" | Select-Object -First 1 -ExpandProperty FullName)

Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $stage | Out-Null
robocopy $src $stage /E /XD venv .git .pytest_cache .pytest-run .pytest-tmp .pytest_tmp .codex_pytest_tmp /XF .coverage .env
Remove-Item $zip -Force -ErrorAction SilentlyContinue
Compress-Archive -Path "$stage\*" -DestinationPath $zip -Force
scp -i "$key" "$zip" azureuser@51.103.219.2:~/
```

Azure SSH:

```bash
mkdir -p ~/app
unzip -oq ~/uss-azure-upload.zip -d ~/app
```

Bu yol, private repo kullanimi nedeniyle Azure tarafinda `git pull` yerine kullanilan toplu guncelleme yoludur.

### 12.1.c Standart guncelleme akisi

Kod degisikligi yapildiginda genel sira sudur:

1. Yerelde degisiklik yap
2. Degisen dosyalari `scp` ile Azure'a gonder veya toplu zip guncellemesi yap
3. Eger migration dosyasi degistiyse `python -m alembic upgrade head`
4. Eger seed ile ilgili veri degistiyse ilgili seed komutunu tekrar calistir
5. `src/` altindaki Python uygulama kodu degistiyse API'yi restart et
6. Windows tarafindan SSH tunnel ac
7. `health` ve ornek sorgularla tekrar test et

### 12.2 Python kodu degistiyse API restart

Azure SSH oturumunda:

```bash
tmux attach -t uss
```

Sonra `uvicorn` calisan ekranda:

```text
Ctrl+C
```

Ardindan:

```bash
cd ~/app
source .venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Arka plana almak icin:

```text
Ctrl+b
d
```

### 12.3 Sadece migration veya seed degistiysa

Azure SSH oturumunda:

```bash
cd ~/app
source .venv/bin/activate
python -m alembic upgrade head
python -m scripts.seed_synthetic_data
```

Her durumda restart gerekmeyebilir. Genel kural:

- `src/` altindaki Python uygulama kodu degistiyse API restart gerekir
- sadece seed/migration calistirildiysa ve API kodu degismediyse restart cogu zaman gerekmez

### 12.4 Bu durumda hangi komutu calistiracagim?

Hizli karar tablosu:

- `src/...` degisti:
  - Azure'a dosyayi kopyala
  - API restart yap
- `migrations/...` degisti:
  - Azure'a migration dosyasini kopyala
  - `python -m alembic upgrade head`
- `scripts/seed_...` degisti:
  - Azure'a script dosyasini kopyala
  - ilgili `python -m scripts....` komutunu calistir
- sadece `docs/...` degisti:
  - Azure tarafinda hicbir sey yapman gerekmez
- `.env` degisti:
  - Azure'da `.env` dosyasini guncelle
  - API restart yap

## 13. Canli Test Akisi

### 13.1 Windows PowerShell UTF-8 ayari

Ozellikle Turkce karakterler bozuk gorunuyorsa once su komutlari calistir:

```powershell
chcp 65001
[Console]::InputEncoding  = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding
```

### 13.2 SSH tunnel ac

Windows PowerShell:

```powershell
$key = (Get-ChildItem "$HOME\Desktop\önemli\*.pem" | Select-Object -First 1 -ExpandProperty FullName)
ssh -i $key -L 8000:127.0.0.1:8000 azureuser@51.103.219.2
```

Bu pencere acik kalmalidir.

### 13.3 Hizli saglik kontrolu

Baska bir Windows PowerShell penceresinde:

```powershell
$health = Invoke-RestMethod -Uri "http://localhost:8000/health"
$health | ConvertTo-Json -Depth 6
```

Beklenen:

- `llm.status = healthy`
- `llm.primary.model_loaded = true`
- `available_models` icinde `qwen2.5:1.5b`

### 13.4 Profil + sorgu testleri

Windows PowerShell:

```powershell
$contextId = [guid]::NewGuid().ToString()

$profileBody = @{
    query = "Merhaba, profilimi kaydet."
    context_id = $contextId
    full_name = "Test Ogrenci"
    student_number = "22060388"
    student_department = "Bilgisayar Muhendisligi"
    student_faculty = "Muhendislik Fakultesi"
    student_type = "Turk ogrenci"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -ContentType "application/json; charset=utf-8" -Body $profileBody
```

Ardindan ornek testler:

```powershell
$body1 = @{ query = "CAP basvurusu nasil yapilir?"; context_id = $contextId } | ConvertTo-Json
$body2 = @{ query = "Guncel duyurular nelerdir?"; context_id = $contextId } | ConvertTo-Json
$body3 = @{ query = "Iletisim bilgisi"; context_id = $contextId } | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -ContentType "application/json; charset=utf-8" -Body $body1
Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -ContentType "application/json; charset=utf-8" -Body $body2
Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -ContentType "application/json; charset=utf-8" -Body $body3
```

### 13.5 Beklenen kaynak davranisi

Guncel cevaplarda metnin sonunda `Kaynak Ozeti:` bolumu gorunmelidir.

Ornek kaynak tipleri:

- `Belge: ...`
- `Duyuru kaydi: ...`
- `Veritabani kaydi: ders onkosulu`
- `Veritabani kaydi: mufredat / ders plani`
- `Ofis iletisim kaydi: Akademik Programlar`

## 14. VM Otomatik Kapanirsa Ne Yapilacak

Bu VM icin Azure tarafinda otomatik kapatma acik tutuldu. Bu, krediyi bos yere harcamamasi icin bilincli olarak secildi.

VM kapandiysa su sirayla ilerlenir:

### 14.1 Azure portal uzerinden VM'i tekrar ac

Portal yolu:

1. `Virtual machines`
2. `vm-uss-gpu-01`
3. `Start`

Durum `Running` olana kadar beklenir.

### 14.2 Public IP'yi kontrol et

Mevcut kurulumda `Standard` public IP kullanildigi icin IP'nin degismemesi beklenir. Yine de `Overview` ekranindan IP kontrol edilir.

Ornek mevcut IP:

```text
51.103.219.2
```

### 14.3 SSH ile baglan

Windows PowerShell:

```powershell
$key = (Get-ChildItem "C:\Users\ÖMER FARUK DERİN\Desktop\önemli\*.pem" | Select-Object -First 1 -ExpandProperty FullName)
ssh -i $key azureuser@51.103.219.2
```

### 14.4 Docker servisleri halen acik mi kontrol et

```bash
docker compose ps
```

Eger servisler kapanmis veya yeniden baslatilmasi gerekiyorsa:

```bash
cd ~/app
docker compose up -d
```

### 14.5 API halen calisiyor mu kontrol et

```bash
tmux ls
```

Eger `uss` oturumu varsa:

```bash
tmux attach -t uss
```

Eger yoksa yeni oturum acip API'yi yeniden baslat:

```bash
tmux new -s uss
cd ~/app
source .venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Sonra yine:

```text
Ctrl+b
d
```

### 14.6 Windows'tan tunnel acip tekrar test et

```powershell
$key = (Get-ChildItem "C:\Users\ÖMER FARUK DERİN\Desktop\önemli\*.pem" | Select-Object -First 1 -ExpandProperty FullName)
ssh -i $key -L 8000:127.0.0.1:8000 azureuser@51.103.219.2
```

Ve:

- `http://localhost:8000/health`
- `http://localhost:8000/docs`

## 15. Sik Kullanilan Komutlar

### Docker durum

```bash
cd ~/app
docker compose ps
```

### Docker loglari

```bash
cd ~/app
docker compose logs --tail=100 ollama
docker compose logs --tail=100 chromadb
docker compose logs --tail=100 postgres
```

### API tekrar baslatma

```bash
tmux kill-session -t uss
tmux new -s uss
cd ~/app
source .venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### tmux cikis

```text
Ctrl+b
d
```

### Python venv aktif etme

```bash
cd ~/app
source .venv/bin/activate
```

### venv kapatma

```bash
deactivate
```

## 16. Maliyet Notu

Bu kurulumda Hugging Face veya Ollama model indirme islemleri ayri bir "model ucreti" olarak gorunmez.

Maliyet genel olarak su kalemlere yansir:

- Virtual Machine compute
- Managed Disk
- Public IP
- gerekiyorsa bandwidth

Azure Cost Analysis ekraninda veriler anlik degil, gecikmeli gorunebilir.

Kontrol icin:

1. `Azure for Students`
2. `Cost Management`
3. `Cost analysis`
4. `Resources`
5. tarih araligi `This month`

## 17. Sonraki Mantikli Iyilestirmeler

Bu kurulum calisan temel ortamdir. Ileride su iyilestirmeler yapilabilir:

- `systemd` ile API'yi servis haline getirme
- `nginx` reverse proxy
- HTTPS
- ayri bir `.env.azure` dosyasi
- gerekirse ayrik bir GPU test VM'i

## 18. Ayni VM Uzerinde CPU ve GPU Runtime Plani

Bu proje ayni VM uzerinde iki farkli runtime ile calisacak sekilde hazirlanmistir:

- `cpu` runtime
- `gpu` runtime

Onemli not:

- Mevcut VM boyutu `Standard_D4s_v3` CPU-only bir boyuttur
- GPU kullanmak icin VM'in GPU destekli bir boyuta tasinmasi gerekir
- VM GPU destekli oldugunda ayni makinede hem CPU hem GPU ile ayri servisler calistirilabilir

### 18.1 Onerilen servis yapisi

Tek GPU destekli VM uzerinde su yapi onerilir:

- `127.0.0.1:8000` -> CPU API
- `127.0.0.1:8001` -> GPU API
- `127.0.0.1:11434` -> varsayilan Ollama
- `127.0.0.1:11435` -> opsiyonel ayrik CPU Ollama

Bu yapida su altyapi bilesenleri ortak kalir:

- PostgreSQL
- Redis
- ChromaDB

### 18.2 Repo icindeki hazir dosyalar

Repo icine su yardimci dosyalar eklendi:

- `deploy/azure/api.cpu.env.example`
- `deploy/azure/api.gpu.env.example`
- `deploy/azure/README.md`
- `scripts/run_api_profile.sh`

### 18.3 Profilleri hazirlama

Azure SSH:

```bash
cd ~/app
cp deploy/azure/api.cpu.env.example deploy/azure/api.cpu.env
cp deploy/azure/api.gpu.env.example deploy/azure/api.gpu.env
chmod +x scripts/run_api_profile.sh
```

### 18.4 CPU API'yi baslatma

```bash
tmux new -s uss-cpu
cd ~/app
scripts/run_api_profile.sh deploy/azure/api.cpu.env
```

Ardindan:

```text
Ctrl+b
d
```

### 18.5 GPU API'yi baslatma

```bash
tmux new -s uss-gpu
cd ~/app
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d ollama
scripts/run_api_profile.sh deploy/azure/api.gpu.env
```

Ardindan:

```text
Ctrl+b
d
```

### 18.6 Health ile runtime dogrulama

Her iki API de `/health` icinde aktif runtime bilgisini doner.

Ornek alanlar:

- `app.runtime.label`
- `app.runtime.port`
- `app.runtime.embedding_device`
- `app.runtime.reranker_device`
- `app.runtime.ollama_host`

### 18.7 Tam CPU ve tam GPU karsilastirmasi notu

Eger yalnizca API tarafini degil LLM tarafini da ayri ayri olcmek istiyorsan:

- Varsayilan CPU profilinde `OLLAMA_HOST` mevcut Ollama servisine gider
- Tam CPU/GPU LLM karsilastirmasi icin CPU runtime'in `OLLAMA_HOST` degeri CPU odakli ayri bir Ollama sunucusuna gitmelidir
- GPU runtime'in `OLLAMA_HOST` degeri GPU odakli Ollama sunucusuna gitmelidir

Aksi halde iki API ayri portlarda calissa bile ayni Ollama host'una baglanabilir.

### 18.8 Gecis sirasi

GPU destekli boyuta gecis yapildiginda onerilen sira sudur:

1. Azure tarafinda VM boyutunu GPU destekli aileye gecir
2. Gerekli GPU suruculerini kur
3. Ollama'yi GPU override ile kaldir
4. Ollama'nin GPU kullandigini dogrula
5. `api.cpu.env` ve `api.gpu.env` dosyalarini ayarla
6. CPU ve GPU API'lerini ayri `tmux` oturumlarinda baslat
7. `health` ve ayni sorgularla iki runtime'i karsilastir

### 18.9 GPU destekli Ollama compose komutu

Repo icine `docker-compose.gpu.yml` override dosyasi eklendi.

GPU destekli VM uzerinde Ollama'yi su sekilde kaldir:

```bash
cd ~/app
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d ollama
```

Tum altyapiyi GPU override ile birlikte kaldirmak icin:

```bash
cd ~/app
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

Sonrasinda `docker compose logs --tail=100 ollama` ve `ollama ps` ile modelin GPU tarafinda calistigi kontrol edilir.

### 18.10 Windows'tan gonderilecek yeni dosyalar

Bu CPU/GPU runtime duzeni icin Azure'a su dosyalar gonderilmelidir:

- `src/core/config.py`
- `src/api/main.py`
- `.env.example`
- `docker-compose.gpu.yml`
- `scripts/run_api_profile.sh`
- `deploy/azure/api.cpu.env.example`
- `deploy/azure/api.gpu.env.example`
- `deploy/azure/README.md`
- `docs/AZURE_VM_RUNBOOK.md`

Windows PowerShell:

```powershell
$key = (Get-ChildItem "$HOME\Desktop\onemli\*.pem" | Select-Object -First 1 -ExpandProperty FullName)
$root = "$HOME\Desktop\bitirme projesi\university_support_system\university_support_system"

scp -i "$key" "$root\src\core\config.py" azureuser@51.103.219.2:~/app/src/core/
scp -i "$key" "$root\src\api\main.py" azureuser@51.103.219.2:~/app/src/api/
scp -i "$key" "$root\.env.example" azureuser@51.103.219.2:~/app/
scp -i "$key" "$root\docker-compose.gpu.yml" azureuser@51.103.219.2:~/app/
scp -i "$key" "$root\scripts\run_api_profile.sh" azureuser@51.103.219.2:~/app/scripts/
scp -i "$key" "$root\deploy\azure\api.cpu.env.example" azureuser@51.103.219.2:~/app/deploy/azure/
scp -i "$key" "$root\deploy\azure\api.gpu.env.example" azureuser@51.103.219.2:~/app/deploy/azure/
scp -i "$key" "$root\deploy\azure\README.md" azureuser@51.103.219.2:~/app/deploy/azure/
scp -i "$key" "$root\docs\AZURE_VM_RUNBOOK.md" azureuser@51.103.219.2:~/app/docs/
```

### 18.11 Ilk kaldirma ozet akisi

GPU destekli VM'e gecildikten sonra tipik ilk akÄ±s su olur:

1. Yeni dosyalari Azure'a gonder
2. GPU suruculerini kur
3. `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d`
4. `cp deploy/azure/api.cpu.env.example deploy/azure/api.cpu.env`
5. `cp deploy/azure/api.gpu.env.example deploy/azure/api.gpu.env`
6. `chmod +x scripts/run_api_profile.sh`
7. `tmux new -s uss-cpu` ile CPU API'yi baslat
8. `tmux new -s uss-gpu` ile GPU API'yi baslat
9. `/health` uzerinden runtime bilgilerini kontrol et

### 18.12 Azure portal uzerinde resize adimlari

GPU'ya gecis icin ilk aday boyut olarak su seri mantiklidir:

- `Standard_NC4as_T4_v3`

Gerekirse bir ust seviye:

- `Standard_NC8as_T4_v3`

Portal uzerinde izlenecek yol:

1. `Virtual machines`
2. `vm-uss-gpu-01`
3. `Stop` veya `Deallocate`
4. `Size`
5. `NCasT4_v3` ailesinden uygun boyutu sec
6. `Resize`
7. VM tekrar `Running` olunca baglan

Notlar:

- Hedef boyut listede gorunmezse bolge, kota veya mevcut cluster nedeniyle in-place resize desteklenmiyor olabilir
- Bu durumda yeni bir GPU VM acip mevcut `~/app` icerigini tasimak daha dogru olabilir
- Resize sonrasinda public IP'yi tekrar kontrol etmek guvenlidir

### 18.13 GPU surucu ve ilk kontrol

GPU destekli boyuta gectikten sonra:

1. Azure portal uzerinden `Extensions + applications`
2. NVIDIA GPU driver extension kur
3. Kurulum tamamlaninca VM'e SSH ile baglan

Azure SSH:

```bash
nvidia-smi
```

Beklenen:

- NVIDIA GPU gorunmeli
- Surucu yuklu olmali

### 18.14 Ollama GPU dogrulamasi

Azure SSH:

```bash
cd ~/app
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d ollama
docker compose logs --tail=100 ollama
ollama ps
```

`ollama ps` cikisinda modelin GPU kullanimina dair `PROCESSOR` bilgisi kontrol edilir.
