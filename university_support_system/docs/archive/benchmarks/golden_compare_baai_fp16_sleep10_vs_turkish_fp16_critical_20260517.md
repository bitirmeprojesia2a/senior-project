# Golden Trace Comparison

- Baseline: `BAAI-FP16-sleep10` / `shadow_golden_baai_fp16_sleep10_20260517`
- Candidate: `Turkish-FP16-critical-sleep12` / `shadow_golden_turkish_fp16_critical_sleep12_20260517`
- Baseline statuses: `{'OK': 10, 'CHECK': 1, 'FAIL': 1}`
- Candidate statuses: `{'OK': 3, 'CHECK': 2, 'FAIL': 1}`
- Baseline validation: `{'total': 8, 'pass': 7, 'check': 0, 'fail': 1, 'requires_judge': 1, 'enforceable_by_contract': 4, 'by_reason': {'no_query_relevant_required_values': 3, 'no_evidence_claims': 2, 'required_values_preserved': 1, 'query_does_not_require_value_check': 1, 'answer_conflicts_with_evidence_values': 1}}`
- Candidate validation: `{'total': 6, 'pass': 5, 'check': 0, 'fail': 1, 'requires_judge': 1, 'enforceable_by_contract': 4, 'by_reason': {'no_evidence_claims': 1, 'required_values_preserved': 1, 'no_query_relevant_required_values': 2, 'query_does_not_require_value_check': 1, 'answer_conflicts_with_evidence_values': 1}}`
- Baseline provider errors: `{'total': 2, 'by_provider': {'groq': 2}, 'by_reason': {'rate_limit': 2}, 'retryable': 2}`
- Candidate provider errors: `{'total': 17, 'by_provider': {'groq': 11, 'google_ai': 6}, 'by_reason': {'rate_limit': 11, 'other': 6}, 'retryable': 15}`

## Case Diffs

### GT01 changed

- Query: Final sinavlari ne zaman basliyor?
- status: `OK` -> `None`
- owner: `academic_calendar` -> `None`
- capability: `calendar.academic_date` -> `None`
- final_owner: `main_orchestrator` -> `None`
- departments: `['student_affairs']` -> `None`
- validation: `pass` -> `None`
- quality: `pass` -> `None`
- value_conflict: `skipped` -> `None`
- source_count: `1` -> `None`
- llm_call_count: `3` -> `None`
- baseline validation summary: `shadow/pass:no_query_relevant_required_values`
- candidate validation summary: `None`
- baseline preview: Benchmark, Güz dönemi için 03-16 Ocak 2026, bahar dönemi için 01-14 Haziran 2026 tarihleri arasında final sınavları yapılacak. Bu tarihler genel akademik takvime göre belirlenmiştir. Yarıyıl sonu sınavlarına ilişkin cu the tarihler için ilgili akademik takv...
- candidate preview: -

### GT02 changed

- Query: BIL203 dersinin AKTS'si ve on kosulu nedir?
- status: `OK` -> `None`
- owner: `curriculum_catalog` -> `None`
- capability: `course.detail` -> `None`
- final_owner: `main_orchestrator` -> `None`
- departments: `['academic_programs']` -> `None`
- validation: `pass` -> `None`
- quality: `pass` -> `None`
- value_conflict: `skipped` -> `None`
- source_count: `0` -> `None`
- llm_call_count: `3` -> `None`
- baseline validation summary: `shadow/pass:no_evidence_claims`
- candidate validation summary: `None`
- baseline preview: Benchmark, BIL203 dersinin AKTS kredi değeri 5'dir. Ön koşulu BIL104 dersidir. Üretim Türü: - VT - Çalışma biçimi: Doğrudan - Ajan akışı: Müfredat
- candidate preview: -

### GT03 same

- Query: Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?

### GT04 changed

- Query: Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?
- llm_call_count: `4` -> `6`
- baseline preview: Benchmark, Yatay geçiş ile gelen öğrenciler, muafiyet başvurularını Genel akademik takvime göre yapmak zorundadır. • Merkezi yerleştirme puanı (Ek Madde-1) için başvurular 01.08.2025 – 06.08.2025 tarihleri arasında yapılmalıdır. • Kurumlar arası/kurum içi y...
- candidate preview: Benchmark, Yatay geçiş ile gelen öğrenciler, muafiyet başvurularını akademik takvimde belirtilen tarihlerde yapmalıdır. • Merkezi yerleştirme puanı (Ek Madde-1) için 01.08.2025 – 06.08.2025, • Kurumlar arası/kurum içi için 01.08.2025 – 15.08.2025, • Bahar y...

### GT05 changed

- Query: CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?
- departments: `['academic_programs', 'student_affairs']` -> `['student_affairs', 'academic_programs']`
- source_count: `8` -> `9`
- baseline preview: Benchmark, Çift Ana Dal Programı (ÇAP) başvuruları için ana dal not ortalamasının 4,00 üzerinden en az 2,75 olması gerekir. Başvuru koşulları ana dal not ortalaması ve tamamlanmış kredi sayısı esas alınarak belirlenir. Harc borcunuzu Banka ilgili ödeme kana...
- candidate preview: Benchmark, ÇAP başvuruları için ana dal programında mezuniyet hakkını elde eden ve ÇAP’ı başarıyla tamamlayan öğrenciye ayrıca ikinci ana dalı yaptığı bölümün lisans diploması verilir. Öğrencinin ÇAP’tan mezun olabilmesi için ana dal genel not ortalamasının...

### GT06 changed

- Query: Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?
- source_count: `1` -> `3`
- baseline preview: Benchmark, Yabancı öğrenci olarak kayıt ve ikamet izni alma süreci için gerekli evraklar arasında öğrenci bilgileri, beyan ve kabul taahhütnamesi bulunmaktadır. • Öğrenci beyanı ve kabul taahhütnamesinde, Türkiye'de geçireceğiniz öğrencilik sürecinde, Türki...
- candidate preview: Benchmark, Yabancı öğrenci olarak kayıt için Senato tarafından belirlenen kesin kayıt belgelerini teslim etmeniz ve ön kayıtlarınızı kesin kayda dönüştürmeniz zorunludur. İkamet izni başvuru süreci ile ilgili olarak, Türkiye'de geçireceğiniz öğrencilik süre...

### GT07 changed

- Query: Bilgisayar muhendisligindeki son duyurular neler?
- status: `OK` -> `None`
- owner: `announcement_search` -> `None`
- final_owner: `announcement_agent` -> `None`
- departments: `['announcement']` -> `None`
- quality: `pass` -> `None`
- source_count: `5` -> `None`
- llm_call_count: `1` -> `None`
- baseline validation summary: `-`
- candidate validation summary: `None`
- baseline preview: İlgili duyurular: 1. 2025-2026 Bahar Yarıyılı Ara Sınav Programı 2025-2026 Bahar Yarıyılı Ara Sınav Programı için tıklayınız.. Detay: https://bil-muhendislik.omu.edu.tr/tr/haberler/2025-2026-bahar-yariyili-ara-sinav-programi 2. Vefat Haberi - Öğrencimiz Mah...
- candidate preview: -

### GT08 changed

- Query: Bu hafta Muhendislik Fakultesinde seminer var mi?
- status: `OK` -> `None`
- owner: `event_search` -> `None`
- final_owner: `event_agent` -> `None`
- departments: `['event']` -> `None`
- quality: `pass` -> `None`
- source_count: `0` -> `None`
- llm_call_count: `1` -> `None`
- baseline validation summary: `-`
- candidate validation summary: `None`
- baseline preview: Bu sorguya uygun guncel veya yakin tarihli etkinlik bulamadim. Isterseniz fakulte, bolum ya da etkinlik turu belirterek tekrar sorabilirsiniz. Kaynak Özeti: - Veritabanı kaydı: etkinlik araması (uygun kayıt bulunamadı)
- candidate preview: -

### GT09 changed

- Query: Harc borcum var mi?
- status: `OK` -> `None`
- owner: `personal_student_data` -> `None`
- final_owner: `clarification` -> `None`
- departments: `['finance']` -> `None`
- quality: `pass` -> `None`
- source_count: `0` -> `None`
- llm_call_count: `1` -> `None`
- baseline validation summary: `-`
- candidate validation summary: `None`
- baseline preview: Benchmark, Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz.
- candidate preview: -

### GT10 changed

- Query: Sey basvuru ne zaman?
- status: `OK` -> `None`
- final_owner: `clarification` -> `None`
- departments: `[]` -> `None`
- quality: `pass` -> `None`
- source_count: `0` -> `None`
- llm_call_count: `1` -> `None`
- baseline validation summary: `-`
- candidate validation summary: `None`
- baseline preview: Benchmark, Hangi başvuru türü için tarih sorduğunuzu yazar mısınız? Örneğin yatay geçiş, ÇAP/YAP, Erasmus, staj, yaz okulu veya kayıt başvurusu gibi yazabilirsiniz.
- candidate preview: -

### GT11 changed

- Query: CAP basvurusu nasil yapilir?
- status: `OK` -> `CHECK`

### GT12 changed

- Query: Peki not ortalamasi kac olmali?
- source_count: `7` -> `9`
- llm_call_count: `6` -> `7`
- baseline preview: Benchmark, ÇAP başvurusu için genel koşullar: ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20 içinde bulunmak gerekir. Kontenjan ve başvuru takvimi ilgili...
- candidate preview: Benchmark, ÇAP başvurusu için genel koşullar: ana dal not ortalamasının 4,00 üzerinden en az 3,00 olması ve ana dal diploma programının ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20 içinde bulunmak gerekir. Kontenjan ve başvuru takvimi ilgili...

## Summary

- Changed cases: `11/12`
