# Faz 9 - Branch Dispatch Contract Gate

## Karar

Claude golden trace kosusunda selector katmani dogru calisti; sorun selector'dan
cok upstream branch sisirmesiydi. Bu nedenle Faz 9'da specialist selector'a
dokunmadan, department branch dispatch seviyesine dar kapsamli bir contract gate
eklendi.

## Amaç

- Capability/source owner net oldugunda gereksiz department branch'lerini
  calistirmamak.
- Student affairs policy process sorularinda academic curriculum branch'inin
  gereksiz acilmasini engellemek.
- CAP/GNO/kosul/kural gibi akademik policy sinyallerinde academic branch'i
  korumak ve `regulation_agent` yoluna dusurmek.
- International policy sorularinda student affairs branch'ini gereksizse
  kesmek.
- Karari trace ve metadata icinde gorunur tutmak.

## Gate Kurallari

### Tek Branch Sahipleri

- `calendar.academic_date` veya `source_owner=academic_calendar`
  -> sadece `student_affairs`
- `international.policy_lookup` veya `source_owner=international_policy`
  -> sadece `academic_programs`
- `finance.tuition_fee` veya `source_owner=tuition_fee_catalog`
  -> sadece `finance`, ama sorguda net student/academic compound sinyali varsa
  branch'ler korunur
- `course.*`, `curriculum.*`, `schedule.weekly_program`,
  `source_owner=curriculum_catalog|weekly_schedule`
  -> sadece `academic_programs`, ama sorguda net finance/student compound sinyali
  varsa branch'ler korunur

### Student Affairs Policy

`student_affairs.policy_lookup` veya `source_owner=student_affairs_policy`
varsayilan olarak `student_affairs` branch'ini korur.

Academic branch su sinyallerde korunur:

- `şart`, `koşul`, `uygunluk`
- `GNO/GANO`, `not ortalaması`, `yüzdelik`, `kontenjan`
- `AKTS`, `kredi`, `azami`
- `ÇAP`, `çift anadal`, `yandal`
- `yönetmelik`, `yönerge`, `kural`, `hak`

Academic branch korundugunda task type `procedure_query` olarak override edilir;
boylece curriculum yerine regulation uzmanina gitmesi hedeflenir.

Finance branch yalnizca harc/ucret/odeme/borc/burs gibi net finance sinyali
varsa korunur.

## Diagnostics

Her dispatch metadata'sina `branch_dispatch_gate` eklenir:

- `schema`
- `mode`
- `applied`
- `original_departments`
- `kept_departments`
- `pruned_departments`
- `reason`
- `capability`
- `source_owner`
- `task_type_overrides`

Aktif profiler'a da ayni payload `branch_dispatch_gate` attribute'u olarak
yazilir. Decision trace runtime payload'u bu attribute'u tasir. Golden trace
raporunda `Branch Gate` kolonu ve notlar bolumunde gate ozeti gorunur.

## Test Kapsami

Eklenen hedef testler:

- Student affairs policy process sorusunda academic branch prune edilir.
- CAP/GNO kosul sorusunda academic branch korunur ve task type
  `procedure_query` olur.
- International policy sorusunda student affairs branch prune edilir.
- Mevcut multi-department task type recompute davranisi korunur.

## Beklenen Etki

GT04 benzeri sorularda gereksiz academic branch kapanacagi icin latency ve LLM
call sayisi azalmalidir. GT11/GT12 gibi CAP/kosul takip sorularinda academic
branch korunur; selector tarafinda `regulation_agent` yolu devam eder.
