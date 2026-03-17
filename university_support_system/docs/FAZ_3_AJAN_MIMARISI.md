# FAZ 3 — Çok Ajanlı Sistem Mimarisi: Teknik Dokümantasyon

**Proje:** Üniversite Kurumsal Destek Sistemi  
**Doküman Tarihi:** 17 Mart 2026  
**Hazırlayan:** Geliştirme Ekibi  
**Durum:** 🔄 Tasarım Tamamlandı — Kodlama Aşamasına Hazır  

---

## 1. Amaç ve Kapsam

Bu doküman, projenin Üçüncü Fazında (FAZ 3) tasarlanan **çok ajanlı sistemin (multi-agent system)** tüm mimari kararlarını, ajan tanımlarını ve bileşen ilişkilerini kapsamaktadır.

FAZ 3'ün temel hedefi: FAZ 0–2'de inşa edilen RAG altyapısı, LLM servisi ve veritabanı katmanını birbirine bağlayan, **A2A (Agent-to-Agent) protokolü** üzerinde çalışan, 3 katmanlı hiyerarşik bir ajan sistemi oluşturmaktır.

### 1.1 Önceki Fazlarla İlişki

| Faz | Kapsam | FAZ 3 ile İlişki |
|-----|--------|------------------|
| FAZ 0 | Veritabanı, konfigürasyon, enum sabitleri | AgentRegistry, AgentTask tabloları bu fazda kullanılır |
| FAZ 1 | RAG pipeline (belge yükleme, embedding, hybrid search, reranker) | Uzman ajanlar RAG pipeline'ı doğrudan çağırır |
| FAZ 2 | LLM servisi (Ollama + OpenAI fallback) | Her uzman ajan LLMService üzerinden cevap üretir |
| **FAZ 3** | **Ajan mimarisi, orkestrasyon, A2A iletişimi** | Bu doküman |

---

## 2. Departman Yapısı

### 2.1 Aktif Departmanlar (FAZ 3 Kapsamı)

| Departman | Enum Değeri | Açıklama |
|-----------|-------------|----------|
| Öğrenci İşleri | `student_affairs` | Kayıt, not, diploma, staj, öğrenci hayatı |
| Akademik Programlar | `academic_programs` | Müfredat, yönetmelikler, uluslararası programlar |
| Finans | `finance` | Harç, ödeme, burs işlemleri |

### 2.2 Kapsam Dışı Departman

`it_support` (Bilgi İşlem) bu fazda kapsam dışıdır. İlgili kod temizliği tamamlanmıştır:
- `Department.IT_SUPPORT` enum'dan kaldırıldı
- `DEPARTMENT_CONFIGS` ve IT görev tipleri silindi
- `src/agents/it/` klasörü silindi
- `data/raw/it_support/` klasörü silindi
- Etkilenen unit testler güncellendi

> **Not:** `it_support` ileride ek departman olarak eklenebilir. Mevcut departman kayıt yapısı (`DEPARTMENT_CONFIGS`) yeni departman eklemeyi desteklemektedir.

### 2.3 Veri Kaynağı Düzenlemeleri

Finans departmanının oluşturulmasıyla birlikte aşağıdaki dosyalar taşınmıştır:

| Kaynak | Hedef | Dosya |
|--------|-------|-------|
| `student_affairs/yönergeler/` | `finance/yönergeler/` | Türk öğrenci katkı payı ve öğrenim ücretleri PDF |
| `student_affairs/yönergeler/` | `finance/yönergeler/` | Uluslararası öğrenci öğrenim ücretleri PDF |
| `student_affairs/yönergeler/` | `finance/yönergeler/` | Öğrenci yemek bursu yönergesi PDF |
| `student_affairs/yönergeler/` | `finance/yönergeler/` | Kısmi zamanlı öğrenci çalıştırma yönergesi PDF |
| `student_affairs/birimler/` | `finance/birimler/` | İdari ve mali işler birimi TXT |

---

## 3. Mimari Genel Bakış

### 3.1 3 Katmanlı Hiyerarşi

```
┌─────────────────────────────────────────────────────────────────┐
│                    KATMAN 1: ANA ORKESTRATÖR                    │
│   Giriş: Slack Bot / REST API                                   │
│   Kimlik: OTP e-posta doğrulama                                 │
│   Yönlendirme: Kural tabanlı (hızlı) + LLM tabanlı (belirsizse)│
│   + announcement_agent (doğrudan erişim, tüm sorgulara ortak)  │
└────────────────────────┬────────────────────────────────────────┘
                         │ A2A Task
        ┌────────────────┼──────────────────┐
        │                │                  │
┌───────▼────────┐ ┌─────▼──────────┐ ┌────▼───────────┐
│   KATMAN 2:    │ │   KATMAN 2:    │ │   KATMAN 2:    │
│student_affairs │ │academic_programs│ │   finance      │
│  orchestrator  │ │  orchestrator  │ │  orchestrator  │
└──┬──┬──┬──┬───┘ └──┬──┬──┬───────┘ └──┬──┬──────────┘
   │  │  │  │        │  │  │             │  │
   │  │  │  │        │  │  │             │  │
  [1][2][3][4]      [5][6][7]           [8][9]

KATMAN 3 — UZMAN AJANLAR:
[1] registration_agent     [5] curriculum_agent      [8] tuition_agent
[2] graduation_agent       [6] regulation_agent      [9] scholarship_agent
[3] internship_agent       [7] international_agent
[4] student_life_agent
```

### 3.2 Ajan Rolleri (AgentRole Enum — Mevcut)

| Rol | Enum Değeri | Kimler |
|-----|-------------|--------|
| Ana Orkestratör | `main_orchestrator` | 1 adet |
| Departman Orkestratörü | `department_orchestrator` | 3 adet |
| Uzman Ajan | `specialist_agent` | 9 adet + 1 duyuru ajanı |

### 3.3 Genel Veri Akışı

```
Kullanıcı (Slack/API)
    ↓
Ana Orkestratör
  → Kimlik kontrolü (slack_student_mapping)
  → Sorgu ön işleme (QueryPreprocessor)
  → Yönlendirme kararı (kural + LLM)
    ↓
Departman Orkestratörü
  → Görev tipi tespiti
  → Veri tipi tespiti (RAG / DB / Hibrit)
    ↓
Uzman Ajan
  → RAG araması (HybridRetriever)   [prosedürel sorgu]
  → DB sorgusu (async SQLAlchemy)   [kişisel veri sorgusu]
  → LLMService ile yanıt üretimi
  → İletişim bilgisi ekleme (opsiyonel, kullanıcı isteğine bağlı)
  → İlgili duyuru ekleme (announcement_agent üzerinden)
    ↓
Ana Orkestratör
  → Yanıtları birleştir (PARALLEL durumunda)
  → query_logs tablosuna yaz
    ↓
Kullanıcı (Slack/API)
```

---

## 4. Katman 1 — Ana Orkestratör

```
Agent ID  : main_orchestrator
Rol       : Tüm kullanıcı sorgularının tek giriş noktası
Strateji  : Yönlendirme yapar, cevap üretmez
```

### 4.1 Kimlik Doğrulama Akışı

```
Mesaj geldi
    ↓
slack_student_mapping'de kayıtlı mı?
  ↓ Evet                        ↓ Hayır
  is_authenticated = True        "Öğrenci numaranızı girin"
  student_id bilinir                  ↓
  Sorguya devam                  students tablosunda ara
                                      ↓
                               Bulunamadı → "Kayıtlı değilsiniz"
                               Bulundu → üniversite e-postasına OTP gönder
                                          (otp_codes tablosuna hash'li kod)
                                      ↓
                               OTP doğrulandı
                                      ↓
                               verification_sessions + slack_student_mapping oluştur
                                      ↓
                               is_authenticated = True, student_id bilinir
```

> **Kural:** Kimlik doğrulanmamış kullanıcılar sistemi kullanmaya devam edebilir. Sadece kişisel veri gerektiren sorgular (harç borcu, not bilgisi, burs durumu) kısıtlanır. Genel sorular (harç ücreti nedir, yatay geçiş nasıl yapılır) herkese açıktır.

### 4.2 Yönlendirme Mantığı

**Aşama A — Kural Tabanlı (hızlı, ~0ms):**

`DEPARTMENT_CONFIGS.keywords` ile anahtar kelime eşleştirmesi yapılır. Her departman için 0.0–1.0 arası skor hesaplanır.

- En yüksek skor ≥ 0.6 ve diğerlerinden farkı > 0.2 → **DIRECT** yönlendirme, LLM çağrısı yok
- Koşul sağlanmıyorsa → Aşama B'ye geç

**Aşama B — LLM Tabanlı (~500ms):**

`DEPARTMENT_ROUTING_SYSTEM_PROMPT` ile Qwen2.5:7b'ye sorgu gönderilir. Dönen JSON:

```json
{
    "departments": ["student_affairs"],
    "confidence": 0.85,
    "reasoning": "Yatay geçiş kayıt işlemi..."
}
```

| Güven Seviyesi | Eşik | Aksiyon |
|----------------|------|---------|
| HIGH | > 0.7 | DIRECT yönlendirme |
| MEDIUM | 0.4–0.7 | Yönlendir, log'a düşür |
| LOW | < 0.4 | CLARIFICATION: Kullanıcıya seçenek sun |

### 4.3 Yönlendirme Stratejileri

| Durum | Strateji | Örnek |
|-------|----------|-------|
| Tek departman, yüksek güven | `DIRECT` | "Harç borcum var mı?" → finance |
| İki departman benzer skor | `PARALLEL` | "Yatay geçiş harç durumu?" → student_affairs + finance |
| Birbirini gerektiren | `SEQUENTIAL` | "Stajın bağıl nota etkisi?" → student_affairs sonra academic_programs |
| Çok düşük güven | `CLARIFICATION` | "Ofis nerede?" → kullanıcıya departman seçtir |

### 4.4 Departman İçi Paralel Routing

Aynı departman içinde birden fazla uzman ajan tetiklenirse (ör. öğrenci aynı anda staj ve not sorusu sordu) → departman orkestratörü iki uzman ajana **aynı anda** gönderir, yanıtları birleştirir.

### 4.5 Ana Orkestratörün Yapmadıkları

- ❌ RAG araması yapmaz
- ❌ Veritabanından veri çekmez
- ❌ LLM ile cevap üretmez
- ❌ Prompt oluşturmaz
- ✅ Sadece yönlendirir, toplar ve iletir

---

## 5. Katman 2 — Departman Orkestratörleri

Her departman orkestratörü için ortak işlem sırası:

```
1. Ana Orkestratörden A2A Task alır
2. Görev tipi tespiti → Hangi uzman ajan?
3. Veri tipi tespiti → RAG / DB / Hibrit?
4. Uzman ajana A2A Task gönderir (gerekirse paralel)
5. Uzman ajan yanıtını biçimlendirir
6. Ana Orkestratöre döndürür
```

### 5.1 student_affairs_orchestrator

**Görev Tipi Yönlendirme:**

| Sorgu İçeriği | Hedef Ajan |
|---------------|------------|
| Kesin kayıt, ders kaydı, yatay geçiş, muafiyet | `registration_agent` |
| Not, GNO, bağıl not, diploma, yaz okulu, mezuniyet | `graduation_agent` |
| Staj, bitirme projesi, MUP/sanayi uygulaması | `internship_agent` |
| Kimlik kartı, konukevi, öğrenci konseyi/toplulukları, engelli | `student_life_agent` |

### 5.2 academic_programs_orchestrator

**Görev Tipi Yönlendirme:**

| Sorgu İçeriği | Hedef Ajan |
|---------------|------------|
| Müfredat, ders programları, AKTS, ÇAP/YAP, önkoşullar | `curriculum_agent` |
| Yönetmelik, yönerge, politika, prosedür, genelge | `regulation_agent` |
| Erasmus, uluslararası öğrenci, ikamet izni, denklik | `international_agent` |

> **Not:** `calendar_agent` kaldırılmıştır. "Kayıt dönemi ne zaman?" → `registration_agent` (DB: course_registration_periods). "Bu dönem hangi dersler açık?" → `curriculum_agent` (DB: courses). Kontenjanlar → `international_agent` (prosedürler RAG).

### 5.3 finance_orchestrator

**Görev Tipi Yönlendirme:**

| Sorgu İçeriği | Hedef Ajan |
|---------------|------------|
| Harç ücreti, borç durumu, taksit, ödeme geçmişi | `tuition_agent` |
| Burs başvurusu, burs durumu, yemek bursu, kısmi zamanlı | `scholarship_agent` |

**Finance'a Özgü Kural:** Kimlik doğrulanmamış kullanıcı kişisel finansal sorgu sorarsa:
> "Bu bilgiye erişmek için öğrenci kimliğinizi doğrulamanız gerekmektedir. Öğrenci numaranızı girerek devam edebilirsiniz."

---

## 6. Katman 3 — Uzman Ajanlar

Her uzman ajan aşağıdaki genel adımları izler:
1. Departman orkestratöründen A2A Task alır
2. Kişisel veri sorgusu ise → DB erişimi (kimlik doğrulama kontrolü ile)
3. Belge sorgusu ise → HybridRetriever ile RAG araması
4. LLMService ile yanıt üretir
5. İletişim bilgisi seçeneği sunar (bölüm 8)
6. İlgili duyuruları ekler (bölüm 7, varsa)

---

### 6.1 registration_agent

```
Agent ID  : registration_agent
Bağlı     : student_affairs_orchestrator
```

**Tetikleyen Sorgular:**  
Kesin kayıt belgeleri / Yatay geçiş başvurusu / Ders kaydı tarihleri / Dönem dondurma / Ders muafiyeti ve intibak / Kayıt silme / Akademik takvim

**Veri Kaynakları:**

| Kaynak | İçerik |
|--------|--------|
| RAG — student_affairs_docs | listeler/(yatay geçiş kontenjanları, takvimi, YKS puanları), yönergeler/(yatay geçiş, kayıt belgeleri, muafiyet-intibak), yönetmelikler/(ön lisans-lisans), takvimler/(akademik takvim, ders programı) |
| DB — course_registration_periods | semester, start_date, end_date, is_active |

**İşlem Adımları:**
1. "Ne zaman?" sorgusu → `course_registration_periods` kontrol et
   - `is_active = True` → "Şu anda kayıt açık: [dönem] [tarih aralığı]" yanıtın başına ekle
2. RAG araması yap
3. DB + RAG birleştir → LLM ile yanıt üret

**Özel Kurallar:**
- Yatay geçiş sorgularında her zaman güncel kontenjan listesine yönlendir
- Ders yeterlik/muafiyet/intibak: başvuru süreci bu ajanda; ilgili yönerge `regulation_agent`'ta da mevcut

---

### 6.2 graduation_agent

```
Agent ID  : graduation_agent
Bağlı     : student_affairs_orchestrator
```

**Tetikleyen Sorgular:**  
Mezuniyet GNO şartı / Bağıl değerlendirme hesabı / Diploma alma / Transkript / Yaz okulu / **[KİŞİSEL]** GNO'mu öğrenme / Bu dönem notlarım / %10 başarı değerlendirme

**Veri Kaynakları:**

| Kaynak | İçerik |
|--------|--------|
| RAG — student_affairs_docs | yönergeler/(bağıl değerlendirme ×3, yaz okulu ×3, %10 başarı ×2, diploma-mezuniyet), yönetmelikler/(yaz dönemi) |
| DB — students | gpa, completed_credits, total_credits, registration_status, class_year |
| DB — student_courses | grade, status (semester bazlı) |
| DB — course_registration_periods | yaz okulu dönem bilgisi |

**İşlem Adımları:**
1. Kişisel veri mi?
   - Kimlik doğrulandı → DB'den students + student_courses çek
   - Kimlik yok → "Kimlik doğrulama gerekli"
2. Hibrit sorgu (ör. "GNO'm mezuniyet için yeterli mi?"):
   - DB'den GNO al + RAG'dan mezuniyet şartı + LLM karşılaştırma yapsın
3. Genel sorgu → Sadece RAG

**Özel Kurallar:**
- Transkript: DB'den not tablosu + RAG'dan transkript alma prosedürü birlikte verilir
- Yaz okulu: tarih/dönem DB'den, GNO şartı RAG'dan

---

### 6.3 internship_agent

```
Agent ID      : internship_agent
Bağlı         : student_affairs_orchestrator
Gerçek Kapsam : Uygulamalı Eğitim — Staj + Bitirme Projesi + MUP/Sanayi Uygulaması
```

**Tetikleyen Sorgular:**  
Zorunlu/gönüllü staj başvurusu / Staj formu indirme / Staj değerlendirme kriterleri / Bitirme projesi teslim / Bitirme projesi şablon / MUP nedir / Sanayi uygulaması dersi / Staj ücreti geri ödemesi

**Veri Kaynakları:**

| Kaynak | İçerik |
|--------|--------|
| RAG — student_affairs_docs | formlar/(~15 staj + bitirme projesi + sanayi uygulaması formu), uygulama/(staj adımları, sık sorulanlar, bilgilendirme), uygulama esasları/(staj ilkeleri bölüm bazlı ×7, bitirme projesi ×6, MUP ×4, iş yeri değerlendirme ×2), yönergeler/(staj ×3, uygulamalı dersler) |
| DB — students | department (bölüme özgü staj ilkesi seçimi için) |
| DB — student_courses | staj dersinin durumu |

**İşlem Adımları:**
1. Alt konu tespiti: staj / bitirme projesi / MUP
2. Bölüm bazlı mı?
   - Kimlik doğrulandı → `students.department` oku → bölüme özgü belgeyi önceliklendir
   - Kimlik yok → genel staj yönergesi
3. RAG araması yap
4. Form istendi → ilgili form dosya adını listele
5. LLM ile yanıt üret

**Özel Kurallar:**
- "Staj ücreti geri ödemesi" → prosedür bu ajanda, ödeme işlemi için `scholarship_agent`'a çapraz yönlendirme ekle
- Bitirme projesi danışmanı → DB'de kayıtlı değil → "Bölüm sekreterliğinizle iletişime geçin" yönlendirmesi

---

### 6.4 student_life_agent

```
Agent ID  : student_life_agent
Bağlı     : student_affairs_orchestrator
```

**Tetikleyen Sorgular:**  
Öğrenci kimlik kartı / Öğrenci konseyi / Öğrenci toplulukları / Konukevi başvurusu / Engelli öğrenci desteği / Akademik danışmanlık sistemi / Kalite komisyonu / Kurullar

**Veri Kaynakları:**

| Kaynak | İçerik |
|--------|--------|
| RAG — student_affairs_docs | yönergeler/(kimlik kartı, konseyi, topluluklar, konukevi, kalite komisyonu, akademik danışmanlık), birimler/(daire_başkanlığı, Kurullar), uygulama esasları/(engelli öğrenciler) |
| DB | Yok — tamamen RAG tabanlı |

**Özel Kurallar:**
- Kişisel danışman sorusu → "Bölüm sekreterliğinizle iletişime geçin"
- Kimlik doğrulaması gerektiren sorgu yok, içerik genel bilgi
- Engelli öğrenci sorusu: hem burada (student_affairs) hem `regulation_agent`'ta (academic_programs/yonergeler_kurumsal) belge var → main orchestrator `PARALLEL` routing ile her ikisine yönlendirebilir

---

### 6.5 curriculum_agent

```
Agent ID      : curriculum_agent
Bağlı         : academic_programs_orchestrator
Devralınan    : Eski calendar_agent'ın "hangi dersler açık?" görevi
```

**Tetikleyen Sorgular:**  
Bölüm müfredatı / Bu dönem açık dersler / ÇAP başvuru GNO şartı / YAP (yan dal) kredi şartı / Ders önkoşulları / Pedagojik formasyon dersleri / Ders içerikleri / AKTS kredisi

**Veri Kaynakları:**

| Kaynak | İçerik |
|--------|--------|
| RAG — academic_programs_docs | ders_programlari/(27 PDF), mufredatlar/(15 müfredat + ÇAP/YAP), uygulama/(ders içerikleri), uygulama esasları/(pedagojik formasyon), yonergeler_egitim/(ÇAP-YAP, pedagojik formasyon yönergeleri) |
| DB — courses | course_code, course_name, credits, department, semester, instructor |
| DB — course_prerequisites | önkoşul haritası |

**İşlem Adımları:**
1. DB sorgusu gerekiyor mu?
   - "Bu dönem hangi dersler açık?" → `courses WHERE semester = aktif_dönem`
   - "X dersinin önkoşulu?" → `course_prerequisites JOIN courses`
2. RAG araması yap
3. ÇAP/YAP sorusu → kuralları burada ver + "başvuru için öğrenci işleriyle görüşün" notu ekle
4. LLM ile yanıt üret

---

### 6.6 regulation_agent

```
Agent ID  : regulation_agent
Bağlı     : academic_programs_orchestrator
Kapsam    : 161 dosya — yönetmelik, yönerge, politika, prosedür, genelge
```

**Tetikleyen Sorgular:**  
Lisansüstü eğitim yönetmeliği / Uzaktan eğitim yönergesi / Kütüphane kuralları / Kariyer merkezi başvurusu / Etik ihlal bildirimi / Araştırma politikası / Özel öğrenci statüsü / Diş hekimliği/tıp eğitim yönergeleri / Bilgi güvenliği politikası

**Veri Kaynakları:**

| Kaynak | İçerik |
|--------|--------|
| RAG — academic_programs_docs | politikalar/(26 politika), yonergeler_egitim/(43 eğitim yönergesi), yonergeler_kurumsal/(48 kurumsal yönerge), yönetmelikler/(36 yönetmelik), genelgeler/(6 genelge), birimler/(eğitim_planlama, kalite_ofisi) |
| DB | Yok — tamamen RAG tabanlı |

**Özel Kurallar:**
- Bu ajanın performansı doğrudan RAG kalitesine bağlıdır — HybridRetriever + CrossEncoderReranker kritik
- Birden fazla ilgili belge → en yüksek puanlı 3 belgeyi sun, belge adı ve madde numarasını cevaba ekle
- Tıp/diş hekimliği/veteriner fakültesine özgü sorular da bu ajana gelir

---

### 6.7 international_agent

```
Agent ID  : international_agent
Bağlı     : academic_programs_orchestrator
```

**Tetikleyen Sorgular:**  
Erasmus başvurusu / Yabancı öğrenci kaydı / İkamet izni adımları / YÖS / Denklik belgesi / TÖMER kayıt şartları / Özel yetenek sınavı / Uluslararası yatay geçiş / Kontenjanlar

**Veri Kaynakları:**

| Kaynak | İçerik |
|--------|--------|
| RAG — academic_programs_docs | yonergeler_uluslararasi/(11 dosya — Erasmus, uluslararası öğrenci, yabancı dil), prosedürler/(16 dosya — ikamet, denklik, kesin kayıt, YÖS, ön kayıt kılavuzu — tamamı uluslararası), formlar/(4 dosya — tamamı uluslararası öğrenci formu), uygulama esasları/(yurt dışından öğrenci kabulü), mufredatlar/(uluslararası başvuru) |
| DB | Yok |

**Özel Kurallar:**
- "Uluslararası öğrenci harç ücreti?" → `finance/tuition_agent`'a çapraz yönlendirme (RAG'da uluslararası harç tablosu finance klasöründe)
- Adım adım prosedür sorularında (ikamet izni vb.) belgeleri doğrudan ve sıralı sun

---

### 6.8 tuition_agent

```
Agent ID  : tuition_agent
Bağlı     : finance_orchestrator
```

**Tetikleyen Sorgular:**  
Bu dönem harç borcu / Ödeme geçmişim / Taksit planım / Son ödeme tarihi / **[GENEL]** 2025-2026 harç ücreti / Uluslararası öğrenci harç tablosu / Taksitlendirme var mı

**Veri Kaynakları:**

| Kaynak | İçerik |
|--------|--------|
| RAG — finance_docs | türk öğrenci katkı payı ve öğrenim ücretleri PDF, uluslararası öğrenci öğrenim ücretleri PDF |
| DB — tuition | total_amount, paid_amount, has_debt, debt_amount, due_date, last_payment_date |
| DB — payments | amount, payment_date, payment_method, receipt_no |
| DB — installments | installment_number, amount, due_date, status, paid_at |

**İşlem Adımları:**
1. Kişisel sorgu mu?
   - Kimlik doğrulandı → ilgili DB tablolarını sorgula
   - Kimlik yok → "Kişisel harç bilgileri için kimlik doğrulama gereklidir"
2. Genel sorgu (ücret tablosu) → RAG
3. LLM ile yanıt üret

**Örnek Çıktı (kişisel):**
> "2025-2026 Bahar dönemine ait **3.850 TL** harç borcunuz bulunmaktadır. Son ödeme tarihi: **28 Şubat 2026**. 2. taksit henüz ödenmemiş."

---

### 6.9 scholarship_agent

```
Agent ID  : scholarship_agent
Bağlı     : finance_orchestrator
```

**Tetikleyen Sorgular:**  
Burs alıyor muyum / Burs miktarım / Burs başvurabilir miyim / GNO şartı / Yemek bursu başvurusu / Burs başvuru tarihleri / Kısmi zamanlı çalışma imkânı / Başvurumun durumu

**Veri Kaynakları:**

| Kaynak | İçerik |
|--------|--------|
| RAG — finance_docs | yemek bursu yönergesi PDF, kısmi zamanlı öğrenci çalıştırma yönergesi PDF |
| DB — scholarships | monthly_amount, status (active/inactive), start_date, end_date |
| DB — available_scholarships | name, description, min_gpa, monthly_amount, deadline, is_active |
| DB — scholarship_applications | application_date, status (pending/approved/rejected) |
| DB — students | gpa (başvuru uygunluk kontrolü için) |

**Özel Kurallar:**
- GNO uygunluğu: `students.gpa` ≥ `available_scholarships.min_gpa` ve `deadline` geçmemişse proaktif bildir: "X Bursu'na başvurabilirsiniz. Son başvuru: [tarih]"
- Başvuru durumu: `scholarship_applications.status` (pending/approved/rejected) Türkçe çeviriyle döndür

---

## 7. Yardımcı Ajan — announcement_agent

```
Agent ID  : announcement_agent
Bağlı     : main_orchestrator (doğrudan erişim, tüm departmanlar için ortak)
Tetiklenme: Hem direkt sorgu ("duyurular var mı?") hem de diğer sorguların sonunda
```

### 7.1 Duyuru Sistemi Akışı

**Arka Plan Servisi (Periyodik):**
```
Periyodik servis (günde 1 kez önerilir — gece yarısı)
    ↓
OMÜ web sitesinden duyuruları scrape eder
    ↓
Yeni duyuru → announcements.original_text'e yaz
    ↓
LLMService.generate() → 2-3 cümlelik özet üret → announcements.summary'e yaz
    ↓
faculty, department, source_url, published_at bilgilerini kaydet
    ↓
is_active = True olarak işaretle
```

> **Not:** `announcements` tablosu FAZ 0'da tasarlanmış ve `summary` + `source_url` alanları bu akışı destekleyecek şekilde hazır beklemektedir. Ayrı bir implementasyon gerekmez.

**Scraping Sıklığı Önerisi:** Günde bir kez (gece yarısı cron job). Saatlik scraping OMÜ sunucusuna gereksiz yük bindirir ve duyurular nadiren saatlik değişir.

**Sorgu Sırasında:**
```
Kullanıcı sorgusu geldi
    ↓
Uzman ajan cevabını üretiyor (paralel)
announcement_agent çalışıyor:
    WHERE is_active = True
    AND (faculty = öğrencinin fakültesi VEYA department eşleşmesi)
    AND published_at > son 7 gün
    AND ilgili anahtar kelimeler eşleşiyor
    ORDER BY published_at DESC LIMIT 3
    ↓
İlgili duyuru varsa cevabın sonuna ekle:
```

**Çıktı Formatı:**
```
📌 İlgili Duyuru:
[Özet metin — 2-3 cümle]
🔗 Detay için: [source_url]
```

### 7.2 Tetiklenme Senaryoları

| Senaryo | Tetiklenme |
|---------|------------|
| "Son duyurular neler?" | main_orchestrator → doğrudan announcement_agent |
| "Staj başvurusu nasıl yapılır?" | internship_agent cevap üretirken, announcement_agent paralel çalışır → staj duyurusu varsa ekler |
| Herhangi bir sorgu | Eşleşen aktif duyuru varsa otomatik eklenir; yoksa cevaba ekleme yapılmaz |

---

## 8. İletişim Bilgisi Sistemi

### 8.1 UX Akışı

Her uzman ajan cevabını ürettikten sonra aşağıdaki standart mesajı ekler:

```
─────────────────────────────────────────────────────
💬 Daha iyi yardımcı olabilmem için sorunuzu daha
   detaylı açıklayabilirsiniz ya da ilgili sekreterin
   iletişim bilgilerini paylaşabilirim.
─────────────────────────────────────────────────────
```

Kullanıcı "iletişim bilgisi" seçeneğini seçerse:
→ `office_contacts` tablosundan ajanın `related_agents` alanıyla eşleşen kayıtlar çekilir ve sunulur.

**Örnek Çıktı (iletişim bilgisi istenirse):**
```
📞 Ders Kayıt ve Not İşlemleri Ofisi
   [Personel Adı] — [Ünvan]
   Dahili: [7XXX]
   E-Posta: [kullanici@omu.edu.tr]
```

### 8.2 Önerilen office_contacts Tablo Tasarımı

```sql
office_contacts:
  - id              INTEGER PRIMARY KEY
  - unit_name       VARCHAR(150)   -- "Ders Kayıt ve Not İşlemleri Ofisi"
  - department      VARCHAR(50)    -- Department enum değeri
  - person_name     VARCHAR(120)   -- "Ahmet Yılmaz"
  - title           VARCHAR(80)    -- "Şef / Memur / Uzman"
  - phone_ext       VARCHAR(20)    -- "7304" (dahili numara)
  - email           VARCHAR(120)
  - related_agents  JSON           -- ["registration_agent", "graduation_agent"]
  - is_active       BOOLEAN        -- Default True
  - created_at      TIMESTAMPTZ
  - updated_at      TIMESTAMPTZ
```

### 8.3 Ajan — Ofis Eşleşme Önerileri

Aşağıdaki eşleşmeler OMÜ organizasyon şemasına dayanmaktadır. Personel bilgileri `data/raw/*/birimler/` klasörlerindeki TXT dosyalarından ve OMÜ web sitesinden toplanmalıdır.

| Ajan | İlgili OMÜ Ofisi | Açıklama |
|------|------------------|----------|
| `registration_agent` | Kesin Kayıt ve Özlük İşlemleri Ofisi | Kayıt, öğrenci kimliği |
| `registration_agent` | Ders Kayıt ve Not İşlemleri Ofisi | Ders seçimi, notlar |
| `graduation_agent` | Diploma ve Mezun Öğrenci İşlemleri Ofisi | Mezuniyet, diploma |
| `internship_agent` | Bölüm staj koordinatörlüğü | Bölüm bazlı yönlendirme |
| `student_life_agent` | Daire Başkanlığı genel hattı | Genel bilgi |
| `curriculum_agent` | Program İşlemleri Ofisi | Müfredat sorguları |
| `curriculum_agent` | Müfredat Düzenleme Ofisi | ÇAP/YAP, müfredat güncelleme |
| `regulation_agent` | Mevzuat Ofisi | Yönetmelik sorguları |
| `international_agent` | Uluslararası Öğrenci Ofisi | Yabancı öğrenci işlemleri |
| `tuition_agent` | Mali İşler ve Taşınır Kontrol Ofisi | Harç, ödeme |
| `scholarship_agent` | Yatay Geçiş ve Burs İşlemleri Ofisi | Burs başvurusu |
| `announcement_agent` | İletişim Ofisi | Genel duyurular |

> **Önemli Not:** Şu an sistemde yalnızca `kalite_ofisi.txt` dosyasından elde edilmiş personel bilgisi mevcuttur (Engin GÜNGÖR — Bilgisayar Teknikeri — Dahili: 7304). Diğer ofislerin personel bilgileri OMÜ web sitesinden veya birim sekreterliklerinden toplanarak `office_contacts` tablosuna eklenmesi gerekmektedir. Bu veriler değişkendir (personel rotasyonu), güncel tutmak için yönetim arayüzü önerilir.

---

## 9. Yeni Veritabanı Tablosu Gereksinimleri

FAZ 3 için mevcut şemaya eklenmesi gereken tablolar:

### 9.1 office_contacts (Yeni)

Bölüm 8.2'de tasarımı verilmiştir.

### 9.2 Mevcut Tablolar (Kullanılacak, Değişmeyecek)

| Tablo | Kullanan Ajanlar |
|-------|-----------------|
| `students` | graduation_agent, internship_agent, scholarship_agent, tuition_agent |
| `student_courses` | graduation_agent |
| `courses` | curriculum_agent |
| `course_prerequisites` | curriculum_agent |
| `course_registration_periods` | registration_agent, graduation_agent |
| `tuition` | tuition_agent |
| `payments` | tuition_agent |
| `installments` | tuition_agent |
| `scholarships` | scholarship_agent |
| `available_scholarships` | scholarship_agent |
| `scholarship_applications` | scholarship_agent |
| `announcements` | announcement_agent |
| `agent_registry` | Tüm ajanlar (kayıt ve heartbeat için) |
| `agent_tasks` | A2A iletişim takibi |
| `query_logs` | main_orchestrator |
| `otp_codes` | main_orchestrator (kimlik doğrulama) |
| `verification_sessions` | main_orchestrator |
| `slack_student_mapping` | main_orchestrator |

---

## 10. Cross-Cutting Konular

### 10.1 Cross-Agent Yönlendirme Durumları

| Durum | Kaynak Ajan | Hedef Ajan | Strateji |
|-------|------------|------------|----------|
| "Uluslararası öğrenci harç ücreti?" | international_agent | tuition_agent | Çapraz yönlendirme |
| "Staj ücreti geri ödemesi?" | internship_agent | scholarship_agent | Çapraz yönlendirme |
| "ÇAP başvurusu nasıl yapılır?" | curriculum_agent (kural) | registration_agent (başvuru süreci) | main_orchestrator → PARALLEL |
| "Engelli öğrenci desteği?" | student_life_agent + regulation_agent | her ikisi | PARALLEL |
| "Yatay geçiş harç durumu?" | registration_agent + tuition_agent | her ikisi | PARALLEL |

### 10.2 Kimlik Doğrulama Gerektiren Sorgular

Aşağıdaki sorgu tipleri kimlik doğrulama zorunludur:

| Ajan | Kişisel Veri |
|------|-------------|
| graduation_agent | GNO, notlar, transkript |
| tuition_agent | Harç borcu, ödeme geçmişi, taksit planı |
| scholarship_agent | Burs durumu, başvuru durumu |
| internship_agent | Bölüme özgü staj ilkesi (bölüm bilgisi için) |


Her ajan-arası iletişimde:
- `Task` nesnesi oluşturulur ve `agent_tasks` tablosuna yazılır
- `TaskState`: submitted → working → completed / failed
- `InternalTaskStatus` (routing, queued, retrying, timeout) A2A dışı iç süreçler için kullanılır

**A2A Task Payload Yapısı:**

```json
{
    "query_text": "Harç borcum var mı?",
    "original_query": "Harç borcum var mı?",
    "student_id": 1042,
    "is_authenticated": true,
    "query_type": "factual",
    "context_id": "conv_abc123",
    "routing_reason": "Harç anahtar kelimesi — finance DIRECT",
    "priority": "NORMAL"
}
```

## 11. Kodlama Sırası Önerisi

FAZ 3 implementasyonu için önerilen sıra:

1. `office_contacts` Alembic migration + model + seed verisi
2. `src/routing/` modülü — kural tabanlı + LLM tabanlı router implementasyonu
3. `src/agents/student/` — 4 uzman ajan (registration, graduation, internship, student_life)
4. `src/agents/academic/` — 3 uzman ajan (curriculum, regulation, international)
5. `src/agents/finance/` — 2 uzman ajan (tuition, scholarship)
6. `src/agents/announcement/` — duyuru ajanı
7. `src/orchestrators/` — 3 departman orkestratörü
8. `src/orchestrators/main.py` — ana orkestratör
9. `src/a2a/` — A2A protokol katmanı
10. `src/api/` — FastAPI endpoint'leri
11. `src/slack/` — Slack bot entegrasyonu
12. E2E testler + entegrasyon testleri

---

*Bu doküman FAZ 3 tasarım sürecinde alınan tüm mimari kararları yansıtmaktadır.*  
*Son güncelleme: 17 Mart 2026*