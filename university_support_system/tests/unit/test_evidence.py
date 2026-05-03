"""Behavioral tests for the structured evidence extraction pipeline."""

from src.quality.evidence import (
    EvidenceItem,
    all_evidence_off_topic,
    build_evidence_context_chunks,
    build_evidence_diagnostics,
    compute_topic_coherence,
    extract_evidence_items,
    extract_factual_claims,
    select_evidence_sentences,
)
from src.orchestrators.response_utils import clean_final_answer


# ---------------------------------------------------------------------------
# extract_factual_claims
# ---------------------------------------------------------------------------


def test_extract_factual_claims_finds_dates_numbers_percentages():
    text = (
        "Ogrencinin GNO 2.50 uzerinde olmasi gerekir. "
        "Basvuru tarihi 15.09.2025 olarak belirlenmistir. "
        "Devamsizlik orani %30'u gecemez. "
        "Program suresi 4 yil olup toplam 240 AKTS kredi alinmalidir."
    )
    facts = extract_factual_claims(text)

    fact_text = " ".join(facts)
    assert any("2.50" in f or "gno" in f for f in facts), f"GNO not found in {facts}"
    assert any("15.09.2025" in f or "15/09/2025" in f for f in facts), f"Date not found in {facts}"
    assert any("30" in f for f in facts), f"Percentage not found in {facts}"
    assert any("240" in f and "akts" in f for f in facts), f"AKTS not found in {facts}"


def test_extract_factual_claims_finds_condition_phrases():
    text = (
        "Kayit dondurma suresi icinde harc ucreti odenmez. "
        "Ders ekleme birinci hafta sonunda yapilamaz. "
        "Staj defteri teslimi zorunludur."
    )
    facts = extract_factual_claims(text)

    fact_text = " ".join(facts)
    assert any("odenmez" in f for f in facts), f"odenmez not found in {facts}"
    assert any("yapilamaz" in f for f in facts), f"yapilamaz not found in {facts}"
    assert any("zorunludur" in f for f in facts), f"zorunludur not found in {facts}"


# ---------------------------------------------------------------------------
# compute_topic_coherence
# ---------------------------------------------------------------------------


def test_topic_coherence_low_for_unrelated_domains():
    query_terms = {"bagil", "degerlendirme", "sistemi", "nedir"}
    source_content = (
        "Bilgi guvenligi proseduru kapsaminda sunucu yedekleme islemi "
        "her hafta otomatik olarak gerceklestirilir."
    )
    coherence = compute_topic_coherence(query_terms, source_content)
    assert coherence < 0.20, f"Coherence too high for unrelated content: {coherence}"


def test_topic_coherence_high_for_matching_domain():
    query_terms = {"kayit", "dondurma", "suresi"}
    source_content = (
        "Kayit dondurma suresi iki donemi gecemez. "
        "Ogrenci bu surede ogrenim haklarini kullanamazlar."
    )
    coherence = compute_topic_coherence(query_terms, source_content)
    assert coherence >= 0.30, f"Coherence too low for matching content: {coherence}"


def test_topic_coherence_reranker_bonus():
    query_terms = {"yatay", "gecis", "kosullari"}
    source_content = "Yatay gecis basvurusu icin bazi kosullar aranir."
    low_score = compute_topic_coherence(
        query_terms, source_content, source_score=0.30, score_type="reranker",
    )
    high_score = compute_topic_coherence(
        query_terms, source_content, source_score=0.70, score_type="reranker",
    )
    assert high_score > low_score, "Reranker bonus should increase coherence"


# ---------------------------------------------------------------------------
# select_evidence_sentences
# ---------------------------------------------------------------------------


def test_critical_numbers_preserved_in_selected_sentences():
    content = (
        "Genel bilgi paragrafi burada yer alir. "
        "Ogrencinin GNO'su en az 2.50 olmalidir. "
        "Akademik takvim her yil ayri ilan edilir. "
        "Basvuru icin %70 devam zorunlulugu vardir. "
        "Universite hakkinda genel aciklama. "
        "Daha fazla bilgi icin birime basvurunuz. "
        "Fakulte kurulu karari gereklidir. "
        "Ek bilgi icin web sitesini ziyaret ediniz. "
        "Toplam 240 AKTS kredi alinmalidir. "
        "Ogrenci isleri mudurlugu bilgi verir."
    )
    selected = select_evidence_sentences(
        "GNO ve devam kosulu nedir?",
        content,
        max_sentences=4,
    )
    assert "2.50" in selected, f"GNO 2.50 not in selected: {selected}"
    assert "70" in selected, f"70% not in selected: {selected}"


def test_context_window_keeps_neighbor_sentence():
    content = (
        "Kayit dondurma suresi iki donemi gecemez. "
        "Bu sure zarfinda ogrenim haklari askiya alinir. "
        "Fakulte binasi merkez kampuste yer alir."
    )
    selected = select_evidence_sentences(
        "Kayit dondurma ne kadar surer?",
        content,
        max_sentences=3,
    )
    # "Bu sure zarfinda..." references the previous sentence and should be included
    assert "askiya" in selected or "gecemez" in selected, (
        f"Context window should preserve neighbor: {selected}"
    )


def test_heading_structure_preserved():
    content = (
        "Basvuru sartlari\n"
        "1. GNO en az 2.50 olmalidir.\n"
        "2. Disiplin cezasi almamis olmak gerekir.\n"
        "3. Ilgili donemin derslerini tamamlamis olmak.\n"
        "Genel bilgiler\n"
        "Universite hakkinda tanitim bilgisi."
    )
    selected = select_evidence_sentences(
        "Basvuru icin GNO siniri nedir?",
        content,
        max_sentences=4,
    )
    assert "2.50" in selected, f"GNO not in selected: {selected}"


def test_fallback_to_first_sentences_when_nothing_scores_high():
    content = (
        "Alfa beta gama delta epsilon. "
        "Zeta eta theta iota kappa. "
        "Lambda mu nu xi omicron."
    )
    selected = select_evidence_sentences(
        "Tamamen alakasiz bir soru?",
        content,
        max_sentences=3,
    )
    # Should not return empty; fallback returns first 2 sentences
    assert len(selected.strip()) > 0


# ---------------------------------------------------------------------------
# extract_evidence_items
# ---------------------------------------------------------------------------


def test_off_topic_source_marked_when_high_score_but_no_query_overlap():
    results = [
        {
            "content": (
                "Bilgi guvenligi proseduru kapsaminda sunucu yedekleme islemi "
                "her hafta otomatik olarak gerceklestirilir."
            ),
            "source": "bilgi_guvenligi.pdf",
            "score": 0.85,
            "metadata": {"score_type": "reranker"},
        },
    ]
    items = extract_evidence_items("Bagil degerlendirme nedir?", results, "academic_programs")
    assert items[0].is_potentially_off_topic is True, (
        f"Should be off-topic: relevance={items[0].relevance_score}, "
        f"matched={items[0].matched_query_terms}"
    )


def test_relevant_source_not_marked_off_topic():
    results = [
        {
            "content": (
                "Bagil degerlendirme sisteminde ogrencinin basarisi sinif "
                "ortalamasina gore belirlenir. Harf notu GNO hesabinda kullanilir."
            ),
            "source": "yonetmelik.pdf",
            "score": 0.80,
            "metadata": {"score_type": "reranker"},
        },
    ]
    items = extract_evidence_items("Bagil degerlendirme nedir?", results, "academic_programs")
    assert items[0].is_potentially_off_topic is False


def test_student_community_source_not_in_evidence_for_withdrawal_query():
    """Community sources should have lower relevance for withdrawal queries."""
    results = [
        {
            "content": (
                "Ogrenci topluluk uyeligi Yonetim Kurulu karari ile sonlandirilir. "
                "Uyeligi sona eren ogrenci SKSDB'ye itiraz edebilir."
            ),
            "source": "ogrenci_topluluklari_yonergesi.pdf",
            "score": 0.90,
            "metadata": {"score_type": "reranker"},
        },
        {
            "content": (
                "Kendi istegi ile kaydini sildiren ogrencilerin Universite ile ilisigi kesilir. "
                "Kayit sildirme islemi ilgili birime basvuru ile yurutulur."
            ),
            "source": "yonetmelik.pdf",
            "score": 0.65,
            "metadata": {"score_type": "reranker"},
        },
    ]
    items = extract_evidence_items(
        "Universiteyi birakip ayrilmak istiyorum",
        results,
        "student_affairs",
    )
    # The registration source should rank higher (more relevant)
    reg_item = next(i for i in items if "yonetmelik" in i.source_name)
    community_item = next(i for i in items if "topluluk" in i.source_name)
    assert reg_item.relevance_score >= community_item.relevance_score, (
        f"Regulation source should be more relevant: "
        f"reg={reg_item.relevance_score} vs community={community_item.relevance_score}"
    )


def test_student_community_source_kept_for_community_query():
    results = [
        {
            "content": (
                "Ogrenci topluluk uyeligi Yonetim Kurulu karari ile sonlandirilir. "
                "Uyeligi sona eren ogrenci SKSDB'ye itiraz edebilir."
            ),
            "source": "ogrenci_topluluklari_yonergesi.pdf",
            "score": 0.90,
            "metadata": {"score_type": "reranker"},
        },
    ]
    items = extract_evidence_items(
        "Ogrenci toplulugu uyeligi nasil sonlanir?",
        results,
        "student_affairs",
    )
    assert items[0].is_potentially_off_topic is False


def test_evidence_items_sorted_by_relevance():
    results = [
        {
            "content": "Genel tanitim bilgisi burada yer alir.",
            "source": "tanitim.pdf",
            "score": 0.90,
            "metadata": {"score_type": "reranker"},
        },
        {
            "content": "CAP basvurusu icin GNO en az 2.50 olmalidir ve kontenjan siniri vardir.",
            "source": "cap_yonergesi.pdf",
            "score": 0.70,
            "metadata": {"score_type": "reranker"},
        },
    ]
    items = extract_evidence_items("CAP basvuru kosullari nelerdir?", results, "student_affairs")
    assert items[0].source_name == "cap_yonergesi.pdf", (
        f"CAP source should rank first by relevance, got: {items[0].source_name}"
    )


def test_extract_evidence_items_can_use_expanded_analysis_query_for_admin_support_slots():
    results = [
        {
            "content": (
                "Danismanima ulasamazsam ne yapmam gerekir? "
                "Bolum baskanina ulasamazsaniz oidb@omu.edu.tr adresine "
                "sistemle ilgili sorununuzu iletebilirsiniz."
            ),
            "source": "sik_sorulan_sorular.txt",
            "score": 0.62,
            "metadata": {"score_type": "reranker"},
        },
        {
            "content": "Ders kaydi akademik takvimde belirtilen surede tamamlanir.",
            "source": "on_lisans_ve_lisans.pdf",
            "score": 0.70,
            "metadata": {"score_type": "reranker"},
        },
    ]

    items = extract_evidence_items(
        "Hocam benim ders notlarimi sisteme girmemis, ne yapabilirim?",
        results,
        "student_affairs",
        analysis_query=(
            "Hocam benim ders notlarimi sisteme girmemis, ne yapabilirim? "
            "oidb@omu.edu.tr bolum baskani danisman not duzeltme"
        ),
    )

    assert items[0].source_name == "sik_sorulan_sorular.txt"
    assert "oidb@omu.edu.tr" in items[0].selected_sentences.lower()


def test_extract_evidence_items_source_id_uses_relative_path_identity():
    results = [
        {
            "content": "Ayni icerik.",
            "source": "ortak.pdf",
            "score": 0.8,
            "metadata": {
                "relative_path": "a/ortak.pdf",
                "score_type": "reranker",
            },
        },
        {
            "content": "Ayni icerik.",
            "source": "ortak.pdf",
            "score": 0.8,
            "metadata": {
                "relative_path": "b/ortak.pdf",
                "score_type": "reranker",
            },
        },
    ]

    items = extract_evidence_items("Ayni icerik", results, "student_affairs")

    assert len({item.source_id for item in items}) == 2


# ---------------------------------------------------------------------------
# build_evidence_context_chunks
# ---------------------------------------------------------------------------


def test_build_evidence_context_chunks_excludes_off_topic_when_safe_exists():
    safe = EvidenceItem(
        source_name="yonetmelik.pdf", source_id="abc",
        department="academic_programs", score=0.80, score_type="reranker",
        content_snippet="Bagil degerlendirme...", selected_sentences="Bagil degerlendirme...",
        matched_query_terms=["bagil", "degerlendirme"], relevance_score=0.60,
        extracted_facts=[], is_potentially_off_topic=False,
    )
    safe2 = EvidenceItem(
        source_name="sinav_yonergesi.pdf", source_id="def",
        department="academic_programs", score=0.70, score_type="reranker",
        content_snippet="Sinav kurallari...", selected_sentences="Sinav kurallari...",
        matched_query_terms=["degerlendirme"], relevance_score=0.40,
        extracted_facts=[], is_potentially_off_topic=False,
    )
    off_topic = EvidenceItem(
        source_name="bilgi_guvenligi.pdf", source_id="ghi",
        department="academic_programs", score=0.85, score_type="reranker",
        content_snippet="Sunucu yedekleme...", selected_sentences="Sunucu yedekleme...",
        matched_query_terms=[], relevance_score=0.05,
        extracted_facts=[], is_potentially_off_topic=True,
    )
    chunks = build_evidence_context_chunks([safe, safe2, off_topic], "Bagil degerlendirme nedir?")
    chunk_text = "\n".join(chunks)
    assert "bilgi_guvenligi" not in chunk_text, "Off-topic should be excluded when safe sources exist"
    assert "yonetmelik" in chunk_text


def test_build_evidence_context_chunks_uses_off_topic_as_fallback():
    off_topic = EvidenceItem(
        source_name="bilgi_guvenligi.pdf", source_id="ghi",
        department="academic_programs", score=0.85, score_type="reranker",
        content_snippet="Sunucu yedekleme...", selected_sentences="Sunucu yedekleme...",
        matched_query_terms=[], relevance_score=0.05,
        extracted_facts=[], is_potentially_off_topic=True,
    )
    chunks = build_evidence_context_chunks([off_topic], "Test query")
    assert len(chunks) == 1, "Should use off-topic as fallback when no safe items"


# ---------------------------------------------------------------------------
# all_evidence_off_topic
# ---------------------------------------------------------------------------


def test_all_evidence_off_topic_with_one_safe():
    items = [
        EvidenceItem(
            source_name="a.pdf", source_id="1",
            department="x", score=0.8, score_type="reranker",
            content_snippet="", selected_sentences="",
            matched_query_terms=[], relevance_score=0.5,
            extracted_facts=[], is_potentially_off_topic=False,
        ),
    ]
    assert all_evidence_off_topic(items) is False


def test_all_evidence_off_topic_truly_all_off():
    items = [
        EvidenceItem(
            source_name="a.pdf", source_id="1",
            department="x", score=0.8, score_type="reranker",
            content_snippet="", selected_sentences="",
            matched_query_terms=[], relevance_score=0.05,
            extracted_facts=[], is_potentially_off_topic=True,
        ),
        EvidenceItem(
            source_name="b.pdf", source_id="2",
            department="x", score=0.2, score_type="retrieval",
            content_snippet="", selected_sentences="",
            matched_query_terms=[], relevance_score=0.02,
            extracted_facts=[], is_low_confidence=True,
        ),
    ]
    assert all_evidence_off_topic(items) is True


# ---------------------------------------------------------------------------
# diagnostics
# ---------------------------------------------------------------------------


def test_diagnostics_json_serializable():
    """Ensure diagnostics dict is JSON-serializable (no sets, no Python hash)."""
    import json

    item = EvidenceItem(
        source_name="test.pdf", source_id="abc123",
        department="student_affairs", score=0.75, score_type="reranker",
        content_snippet="Test content", selected_sentences="Test",
        matched_query_terms=["kayit", "dondurma"],
        relevance_score=0.60, extracted_facts=["2.50 gno"],
    )
    diag = build_evidence_diagnostics([item])

    # Should not raise
    serialized = json.dumps(diag, ensure_ascii=False)
    assert "kayit" in serialized
    assert "abc123" in serialized


def test_source_id_is_deterministic():
    """source_id should be deterministic across calls (not Python hash())."""
    from src.quality.evidence import _stable_source_id

    id1 = _stable_source_id("test.pdf", "content here")
    id2 = _stable_source_id("test.pdf", "content here")
    assert id1 == id2
    assert len(id1) == 12  # sha1 truncated


# ---------------------------------------------------------------------------
# clean_final_answer integration (sentence dedup, meta artifacts)
# ---------------------------------------------------------------------------


def test_sentence_deduplication_in_clean_final_answer():
    answer = (
        "Kayit dondurma suresi iki donemi gecemez.\n"
        "Ogrenci bu surede ogrenim haklarini kullanamazlar.\n"
        "Kayit dondurma suresi iki donemi gecemez.\n"
        "Ek bilgi icin birime basvurunuz."
    )
    cleaned = clean_final_answer(answer)
    # The duplicate should be removed
    count = cleaned.lower().count("iki donemi gecemez")
    assert count == 1, f"Duplicate sentence not removed, found {count} times"


def test_meta_artifact_still_cleaned():
    answer = (
        "Soru: Kayit dondurma nasil yapilir?\n"
        "Yanit: Akademik takvimde belirtilen tarihlerde basvuru yapilir.\n"
        "Benchmark, Test\n"
        "Kanitlar: yonetmelik.pdf"
    )
    cleaned = clean_final_answer(answer)
    assert "Soru:" not in cleaned
    assert "Benchmark" not in cleaned
    assert "Kanitlar:" not in cleaned
    assert "Akademik takvimde" in cleaned
