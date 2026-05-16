# Faz 7 - Contract-First Specialist Selector

## Karar

Faz 7'de specialist selector icin `Controlled Full Replace` uygulandi.
Keyword tabanli selector artik birincil karar mekanizmasi degil. Gercek agent
secimi once runtime decision contract / capability planner / source owner
sinyallerinden yapilir. Eski keyword selector sadece fallback ve shadow
comparison olarak kalir.

Bu karar, ana mimari hedefle uyumludur: nihai karar omurgasi LLM tarafindan
uretilen contract ve onun uzerine kurulan registry sinyalleri olsun; keyword
listeleri yalnizca kontrat sinyali yoksa emniyet agi olarak calissin.

## Yeni Secim Sirasi

1. `contract`
   - `capability_planner.action.capability`
   - `decision_contract.contract.capabilities.selected`
   - `source_owner.primary`
   - `decision_contract.contract.source_owner.primary`
   - Capability/topic/intent/evidence semantigi
2. `task_type`
   - Departman factory'sindeki mevcut task type -> agent map'i
3. `legacy_keyword_fallback`
   - Eski keyword routing sadece ust sinyaller agent secemediyse kullanilir
4. `fallback`
   - Departman fallback agent'i

## Kontrollu Replace Davranisi

Her secimde `specialist_selection` metadata'si uretilir:

- `selected_agent_id`
- `selected_by`
- contract'in sectigi agent
- task_type'in sececegi agent
- legacy keyword selector'in sececegi agent
- legacy kararinin runtime secimle eslesip eslesmedigi

Bu metadata:

- department response metadata'sina eklenir
- specialist task metadata'sina eklenir
- A2A specialist dispatch payload'unda tasinir
- telemetry payload'unda saklanir
- profiler attribute olarak `specialist_selection` listesine eklenir

Boylece full replace aktif olsa bile eski selector'un ne yapacagi gorunur kalir.

## Mevcut Contract Mapping

### Student Affairs

- `calendar.academic_date` -> `registration_agent`
- `student_affairs.policy_lookup` -> topic/intent semantigine gore:
  - staj / MUP / bitirme -> `internship_agent`
  - topluluk / konukevi / kimlik / engelli / konsey -> `student_life_agent`
  - mezuniyet / diploma / transkript -> `graduation_agent`
  - kayit / basvuru / itiraz / yaz okulu / tek ders vb. -> `registration_agent`
- `source_owner=academic_calendar` -> `registration_agent`
- `source_owner=student_affairs_policy` -> yalnizca semantik alt konu netse spesifik agent

### Academic Programs

- `international.policy_lookup` -> `international_agent`
- `course.*`, `curriculum.*`, `schedule.weekly_program` -> `curriculum_agent`
- `source_owner=curriculum_catalog` veya `weekly_schedule` -> `curriculum_agent`
- `source_owner=international_policy` -> `international_agent`

### Finance

- `finance.tuition_fee` -> `tuition_agent`
- `source_owner=tuition_fee_catalog` -> `tuition_agent`
- Burs tarafinda ayrik capability henuz yok; `SCHOLARSHIP_QUERY` task type halen `scholarship_agent` secer.

## Bilerek Korunan Sinirlar

- Selector henuz yeni bir LLM cagrisi yapmiyor; mevcut LLM/router/planner
  kararlarini tuketiyor. Bu response time'i artirmadan mimariyi ana karar
  omurgasina baglar.
- Keyword listeleri silinmedi. Fallback ve shadow comparison olarak tutuldu.
- Generic `student_affairs_policy` source owner tek basina butun sorulari
  `registration_agent`'a zorlamiyor; spesifik agent secmek icin capability
  topic/intent/evidence semantigi aranir.
- Burs icin yeni capability contract'i eklenmedi. Bu ayri karar ister.

## Sonraki Sertlestirme Adaylari

1. Specialist selector mapping'ini kod icinden ayirip registry/config haline getirmek.
2. `student_affairs.policy_lookup` topic taxonomy'sini capability planner prompt'u ile daha deterministik yapmak.
3. `finance.scholarship_policy` veya benzeri bir capability ekleyip burs secimini task_type'tan contract seviyesine tasimak.
4. Golden trace'e `specialist_selection` kolonlari eklemek.
5. Shadow mismatch oranlarini raporlayip legacy keyword listelerini kademeli temizlemek.
