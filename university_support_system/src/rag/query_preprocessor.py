"""
Sorgu Ön İşleme (Query Preprocessing)

Kullanıcı sorgularını RAG aramasından önce normalize eder ve zenginleştirir.
LLM olmadan çalışır — kural tabanlı Türkçe normalizasyon ve sinonim genişletme.

Temel Sorunlar ve Çözümleri:
    1. "anadal" vs "ana dal" → Bileşik kelime ayırma/birleştirme
    2. "ÇAP" vs "Çift Ana Dal" → Kısaltma genişletme
    3. "nasıl yapılır" → Başvuru süreçleri gibi prosedürel soruların tespiti
    4. Türkçe karakter normalizasyonu (büyük/küçük harf)

Kullanım:
    from src.rag.query_preprocessor import QueryPreprocessor

    qp = QueryPreprocessor()
    expanded = qp.preprocess("Çift anadal başvurusu nasıl yapılır?")
    # → "Çift ana dal ÇAP ikinci lisans başvuru nasıl yapılır"
"""

import re
from typing import Dict, List, Set, Tuple

import structlog

from src.core.text_normalization import normalize_text

logger = structlog.get_logger()


# ── Türkçe Kısaltma / Sinonim Sözlüğü ──────────────────────────────
# Her anahtar: kullanıcının yazabileceği form
# Her değer: belgede geçebilecek alternatif formlar (genişletme)
SYNONYM_MAP: Dict[str, List[str]] = {
    # Çift Ana Dal / ÇAP
    "çap": ["çift ana dal", "ikinci lisans", "çift anadal", "ÇAP"],
    "çift anadal": ["çift ana dal", "ÇAP", "ikinci lisans"],
    "çift ana dal": ["ÇAP", "ikinci lisans", "çift anadal"],
    "ikinci lisans": ["çift ana dal", "ÇAP", "çift anadal"],
    "çift ana dal programı": ["ÇAP", "ikinci lisans programı"],

    # Yan Dal / YDP
    "ydp": ["yan dal programı", "yan dal sertifika"],
    "yandal": ["yan dal", "YDP", "yan dal sertifika"],
    "yan dal": ["YDP", "yandal", "yan dal sertifika"],

    # Öğrenci İşleri
    "öidb": ["öğrenci işleri daire başkanlığı", "öğrenci işleri"],
    "öğrenci işleri": ["ÖİDB", "öğrenci işleri daire başkanlığı"],

    # Kayıt İşlemleri
    "kayıt dondurma": ["kayıt dondurmak", "dönem izni", "kayıt dondurulması", "kayıt dondurmak istiyorum"],
    "dönem dondurma": ["kayıt dondurma", "dönem izni"],
    "kayıt yenileme": [
        "ders kaydı yenileme",
        "kayıt yenilemek",
        "ubys.omu.edu.tr",
        "danışman onayı",
        "sınıf yoklama listesi",
    ],
    "ders kaydı": [
        "kayıt yenileme",
        "ders seçimi",
        "ders kaydı yenileme",
        "ubys.omu.edu.tr",
        "danışman onayı",
        "sınıf yoklama listesi",
    ],
    "kayıt silme": ["kayıt sildirme", "kaydını silme"],
    "ilişik kesme": ["ilişik kesmek", "ayrılma", "kaydını silme", "kayıt sildirme"],
    "ayrılmak": ["ilişik kesme", "kayıt sildirme", "ayrılma"],
    "bırakmak": ["ilişik kesme", "kayıt sildirme", "ayrılma"],
    "muafiyet": [
        "ders muafiyeti",
        "intibak",
        "muafiyet dilekçesi",
        "muafiyet komisyonu",
        "derslere devam",
        "üç hafta",
        "transkript",
        "ders içerikleri",
    ],
    "intibak": [
        "muafiyet",
        "ders muafiyeti",
        "intibak komisyonu",
        "muafiyet dilekçesi",
        "üç hafta",
        "transkript",
    ],
    "itiraz": ["dilekçe", "beş iş günü", "bölüm başkanlığı", "maddi hata", "ilgili birim"],
    "notuma itiraz": [
        "beş iş günü",
        "dilekçe",
        "bölüm başkanlığı",
        "maddi hata",
        "ilgili birim",
        "öğrenci otomasyon sistemi",
    ],
    "not girmemiş": ["oidb@omu.edu.tr", "bölüm başkanı", "danışman", "not düzeltme"],
    "sisteme girmemiş": ["oidb@omu.edu.tr", "bölüm başkanı", "danışman", "not düzeltme"],
    "notlarımı nereden": ["öğrenci bilgi sistemi", "öğrenci otomasyon sistemi", "UBYS", "sınav sonucu"],
    "notlarimi nereden": ["ogrenci bilgi sistemi", "ogrenci otomasyon sistemi", "UBYS", "sinav sonucu"],
    "sınav notlarımı": ["öğrenci bilgi sistemi", "öğrenci otomasyon sistemi", "UBYS", "sınav sonucu"],
    "sinav notlarimi": ["ogrenci bilgi sistemi", "ogrenci otomasyon sistemi", "UBYS", "sinav sonucu"],
    "kopya": [
        "disiplin suçu",
        "kopya muamelesi",
        "sınav kuralları",
        "öğrenci disiplin yönetmeliği",
        "yükseköğretim kurumları öğrenci disiplin yönetmeliği",
    ],
    "disiplin": [
        "disiplin cezası",
        "disiplin soruşturması",
        "disiplin kurulu",
        "sınav kuralları",
        "öğrenci disiplin yönetmeliği",
        "yükseköğretim kurumları öğrenci disiplin yönetmeliği",
    ],

    # Akademik Terimler
    "gno": ["genel not ortalaması", "not ortalaması", "GNO", "akademik ortalama"],
    "not ortalaması": ["GNO", "genel not ortalaması"],
    "akts": ["kredi", "AKTS", "ects"],
    "transkript": ["not belgesi", "transkript belgesi", "not dökümü"],
    "mezuniyet": ["diploma", "mezun olma", "mezuniyet belgesi", "mezun olmak", "mezuniyet koşulları", "mezuniyet şartları"],
    "mezuniyet koşulları": ["mezuniyet şartları", "mezun olmak için", "mezuniyet gereksinimleri"],
    "mezuniyet şartları": ["mezuniyet koşulları", "mezun olmak için", "mezuniyet gereksinimleri"],
    "diploma": ["mezuniyet belgesi", "lisans diploması", "diploma eki"],
    "önkoşul": ["ön koşul", "ön şart", "önşart"],
    "müfredat": ["ders planı", "ders programı", "öğretim programı"],

    # Burs
    "burs": ["burs başvurusu", "burs programı", "başarı bursu"],
    "başarı bursu": ["burs", "akademik burs"],
    "yemek bursu": ["yemek kartı", "ücretsiz yemek"],
    "kısmi zamanlı": ["kısmi zamanlı çalışma", "yarı zamanlı çalışma"],

    # Sınav
    "bütünleme": ["bütünleme sınavı", "telafi sınavı"],
    "final": ["dönem sonu sınavı", "final sınavı"],
    "vize": ["ara sınav", "vize sınavı", "midterm"],
    "mazeret sınavı": ["mazeret", "mazeret dilekçesi"],

    # Staj
    "staj": ["staj uygulaması", "staj programı", "zorunlu staj"],
    "mesleki uygulama": ["MÜP", "sanayi uygulaması", "staj"],
    "bitirme projesi": ["bitirme tezi", "lisans projesi"],

    # Yaz Okulu
    "yaz okulu": ["yaz dönemi", "yaz okulu eğitimi"],
    "sinif kapasitesi": ["kontenjan", "ogrenci sayisi", "kisi", "sube"],
    "sınıf kapasitesi": ["kontenjan", "öğrenci sayısı", "kişi", "şube"],
    "kapasite": ["kontenjan", "ogrenci sayisi", "kisi", "sube"],
    "kontenjan": ["kapasite", "ogrenci sayisi", "kisi", "sube"],

    # Lisansüstü
    "lisansüstü": ["yüksek lisans", "master", "doktora", "lisansüstü eğitim"],
    "yüksek lisans": ["lisansüstü", "master", "lisansüstü eğitim"],

    # Geçiş Programları
    "yatay geçiş": ["kurum içi yatay geçiş", "kurumlar arası yatay geçiş"],
    "dikey geçiş": ["DGS", "dikey geçiş sınavı"],

    # Erasmus ve Değişim
    "erasmus": ["öğrenci değişimi", "erasmus programı", "değişim programı"],
    "mevlana": ["mevlana değişim programı"],
    "farabi": ["farabi değişim programı"],

    # Formasyon
    "formasyon": ["pedagojik formasyon", "öğretmenlik sertifikası"],
    "pedagojik formasyon": ["formasyon", "öğretmenlik sertifikası"],

    # Uluslararasi terimler
    "tömer": ["turkce ogretimi uygulama ve arastirma merkezi", "turkce ogretimi merkezi", "TÖMER", "tomer"],
    "tomer": ["turkce ogretimi uygulama ve arastirma merkezi", "turkce ogretimi merkezi", "TÖMER"],
    "yös": ["yabanci ogrenci sinavi", "uluslararasi ogrenci basvurusu", "YÖS", "yos"],
    "yos": ["yabanci ogrenci sinavi", "uluslararasi ogrenci basvurusu", "YÖS"],
    "denklik": ["denklik belgesi", "okul denkligi", "lise denklik", "diploma denklik"],
    "ikamet": ["ikamet izni", "oturma izni", "göç idaresi", "goc idaresi"],

    # Harç ve Ücret
    "harç": ["katkı payı", "öğrenim ücreti", "harç ücreti"],
    "katkı payı": ["harç", "öğrenim ücreti"],
    "ücret iadesi": ["harç iadesi", "para iadesi"],

    # Devamsızlık ve Kurallar
    "devamsızlık": ["devam zorunluluğu", "yoklama", "devam durumu"],
    "bağıl değerlendirme": [
        "bağıl değerlendirme yönergesi",
        "bağıl not sistemi",
        "mutlak değerlendirme",
        "öğrenci sayısı",
    ],
    "bagil degerlendirme": [
        "bağıl değerlendirme yönergesi",
        "bağıl not sistemi",
        "mutlak değerlendirme",
        "öğrenci sayısı",
    ],
    "mutlak degerlendirme": [
        "bağıl değerlendirme yönergesi",
        "bağıl değerlendirme",
        "mutlak not sistemi",
        "öğrenci sayısı",
    ],
    "ogrenci sayisi": ["bağıl değerlendirme yönergesi", "bağıl değerlendirme", "mutlak değerlendirme"],
    "azami süre": ["azami öğrenim süresi", "maksimum süre"],

    # Belgeler
    "öğrenci belgesi": ["öğrenci durum belgesi", "kayıt belgesi"],
    "askerlik belgesi": ["askerlik tecil belgesi", "tecil belgesi"],
    "disiplin": [
        "disiplin cezası",
        "disiplin soruşturması",
        "disiplin kurulu",
        "öğrenci disiplin yönetmeliği",
    ],

    # Üniversite
    "omü": ["ondokuz mayıs üniversitesi", "OMÜ"],
    "üniversite": ["ondokuz mayıs üniversitesi", "OMÜ"],

    # Sistem
    "ubys": ["üniversite bilgi yönetim sistemi", "UBYS"],
    "obs": ["öğrenci bilgi sistemi", "OBS"],
}


# ── Türkçe Bileşik Kelime Ayırma Kuralları ──────────────────────────
# "anadal" → "ana dal", "yandal" → "yan dal" vb.
COMPOUND_WORD_SPLITS: Dict[str, str] = {
    "anadal": "ana dal",
    "yandal": "yan dal",
    "çiftanadal": "çift ana dal",
    "önkosul": "ön koşul",
    "önkoşul": "ön koşul",
    "önsart": "ön şart",
    "önşart": "ön şart",
}


PROCEDURAL_KEYWORDS = {
    "nasıl", "ne zaman", "nereye", "nerede", "nereden",
    "başvuru", "başvurmak", "başvurulur", "yapılır",
    "süreç", "adım", "prosedür", "işlem",
    "gerekir", "gereklidir", "gerekiyor",
    "şart", "koşul", "zorunlu",
    "nereye başvurulur", "kimden alınır",
}

_TURKISH_SUFFIX_CHARS = "abcçdefgğhıijklmnoöprsştuüvyz"
_NEGATION_WORDS = (
    "sormuyorum",
    "sormuyodum",
    "sormadim",
    "sormadım",
    "degil",
    "değil",
    "istemiyorum",
    "bahsetmiyorum",
    "kastetmiyorum",
)


class QueryPreprocessor:
    """
    Kullanıcı sorgularını arama öncesi normalize eder ve zenginleştirir.

    İşlemler:
        1. Türkçe karakter normalizasyonu
        2. Bileşik kelime ayırma (anadal → ana dal)
        3. Kısaltma/sinonim genişletme (ÇAP → Çift Ana Dal)
        4. Prosedürel sorgu tespiti (nasıl, ne zaman...)

    Args:
        synonym_map: Özel sinonim sözlüğü. None ise varsayılan kullanılır.
        enable_expansion: Sinonim genişletme aktif mi?
    """

    def __init__(
        self,
        synonym_map: Dict[str, List[str]] | None = None,
        enable_expansion: bool = True,
    ):
        self.synonym_map = synonym_map or SYNONYM_MAP
        self.enable_expansion = enable_expansion

        # ASCII/Turkish-agnostic lookup tablosu oluştur.
        self._normalized_synonym_map: Dict[str, List[str]] = {
            normalize_text(k): v for k, v in self.synonym_map.items()
        }

    def preprocess(self, query: str) -> str:
        """
        Sorguyu normalize eder ve zenginleştirir.

        Orijinal sorguyu korur, sonuna genişletilmiş terimleri ekler.
        Bu sayede hem orijinal kelimeler hem de alternatifler aranır.

        Args:
            query: Kullanıcının ham sorusu.

        Returns:
            Zenginleştirilmiş sorgu metni.
        """
        if not query or not query.strip():
            return ""

        query = query.strip()

        # 1. Bileşik kelimeleri ayır
        normalized = self._split_compound_words(query)

        # 2. Sinonim genişletme
        if self.enable_expansion:
            expanded_terms = self._expand_synonyms(normalized)
        else:
            expanded_terms = set()

        # 3. Sonuç: orijinal (normalize edilmiş) + genişletilmiş terimler
        if expanded_terms:
            # Orijinal sorguda zaten geçenleri çıkar
            new_terms = self._dedupe_expanded_terms(
                normalized_query=normalized,
                terms=sorted(expanded_terms, key=lambda value: (normalize_text(value), value)),
            )
            if new_terms:
                result = f"{normalized} {' '.join(new_terms)}"
                # Genişletilmiş terimlere de bileşik kelime ayırma uygula
                # Örn: sinonim "çift anadal" → "çift ana dal" olur
                result = self._split_compound_words(result)
                logger.info(
                    "query_expanded",
                    original=query,
                    expanded=result,
                    added_terms=new_terms,
                )
                return result

        logger.info("query_preprocessed", original=query, result=normalized)
        return normalized

    def normalize_for_bm25(self, text: str) -> str:
        """
        BM25 indeksleme veya arama için metni normalize eder.
        Bileşik kelimeleri ayırır ama sinonim genişletme YAPMAZ.
        
        Bu fonksiyon hem belge indeksleme hem de sorgu zamanında
        BM25'in tutarlı tokenizasyon yapması için kullanılır.

        Args:
            text: Normalize edilecek metin.

        Returns:
            Normalize edilmiş metin.
        """
        if not text:
            return ""

        text = self._split_compound_words(text)
        return text

    def _split_compound_words(self, text: str) -> str:
        """Türkçe bileşik kelimeleri ayırır (büyük/küçük harf duyarsız)."""
        result = text
        for compound, split in sorted(
            COMPOUND_WORD_SPLITS.items(), key=lambda x: len(x[0]), reverse=True
        ):
            pattern = re.compile(re.escape(compound), re.IGNORECASE)
            result = pattern.sub(split, result)
        return result

    def _expand_synonyms(self, text: str) -> Set[str]:
        """
        Metindeki terimleri sinonim sözlüğünden genişletir.
        Uzun terim öncelikli ifade eşleşmesi yapar ve kelime/parça sınırlarını korur.
        """
        expanded: Set[str] = set()
        normalized_text_value = normalize_text(text)

        # Uzun terimlerden kısa terimlere doğru kontrol et
        # (Böylece "çift ana dal programı" önce "çift ana dal"den kontrol edilir)
        sorted_keys = sorted(self._normalized_synonym_map.keys(), key=len, reverse=True)

        matched_keys: Set[str] = set()
        for key in sorted_keys:
            if self._matches_synonym_key(normalized_text_value, key) and key not in matched_keys:
                if self._is_negated_topic(normalized_text_value, key):
                    continue
                synonyms = self._normalized_synonym_map[key]
                expanded.update(synonyms)
                matched_keys.add(key)
                # Alt terimleri de işaretleyerek çift genişletme önle
                for other_key in sorted_keys:
                    if other_key != key and other_key in key:
                        matched_keys.add(other_key)

        return expanded

    def _dedupe_expanded_terms(
        self,
        *,
        normalized_query: str,
        terms: List[str],
    ) -> List[str]:
        """Remove duplicate expansions after compound-word normalization."""
        normalized_query_value = normalize_text(normalized_query)
        seen: Set[str] = set()
        deduped: List[str] = []

        for term in terms:
            split_term = self._split_compound_words(term).strip()
            if not split_term:
                continue

            key = normalize_text(split_term)
            if key in seen or key in normalized_query_value:
                continue

            seen.add(key)
            deduped.append(split_term)

        return deduped

    def _matches_synonym_key(self, text_lower: str, key: str) -> bool:
        exact_pattern = re.compile(rf"(?<!\w){re.escape(key)}(?!\w)")
        if exact_pattern.search(text_lower):
            return True

        # Turkish process phrases are often inflected on the final word:
        # "ders kaydı" -> "ders kaydından", "kayıt yenileme" -> "kayıt yenilemede".
        suffix_pattern = re.compile(
            rf"(?<!\w){re.escape(key)}[{_TURKISH_SUFFIX_CHARS}]*(?!\w)"
        )
        return bool(suffix_pattern.search(text_lower))

    def _is_negated_topic(self, text_lower: str, key: str) -> bool:
        """Negated correction phrases should not expand the rejected topic."""
        match = re.search(
            rf"(?<!\w){re.escape(key)}[{_TURKISH_SUFFIX_CHARS}]*(?!\w)",
            text_lower,
        )
        if not match:
            return False
        following = text_lower[match.end() : match.end() + 48]
        return any(
            re.search(rf"(?<!\w){re.escape(word)}(?!\w)", following)
            for word in _NEGATION_WORDS
        )

    def detect_query_type(self, query: str) -> str:
        """
        Sorgunun tipini tespit eder.

        Returns:
            "procedural" — Nasıl yapılır, ne zaman gibi prosedürel sorular
            "factual" — Ne, kim, kaç gibi bilgi soruları
            "general" — Diğer
        """
        normalized_query = normalize_text(query)

        if any(normalize_text(keyword) in normalized_query for keyword in PROCEDURAL_KEYWORDS):
            return "procedural"

        factual_keywords = {"nedir", "kaçtır", "kaç", "kimdir", "hangi", "ne kadardır"}
        if any(normalize_text(keyword) in normalized_query for keyword in factual_keywords):
            return "factual"

        return "general"
