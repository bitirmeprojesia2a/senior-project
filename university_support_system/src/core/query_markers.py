"""Sorgu sinyal ve marker sabitleri."""

ACADEMIC_DEPARTMENT_CONTEXT_MARKERS: tuple[str, ...] = (
    "mufredat",
    "yariyil",
    "donem",
    "secmeli",
    "ders listesi",
    "hangi dersler",
    "akts gerekli",
    "kredi gerekli",
    "toplam akts",
    "toplam kredi",
    "ders plani",
)

ANNOUNCEMENT_QUERY_MARKERS: tuple[str, ...] = (
    "duyuru",
    "duyurular",
    "haber",
    "haberler",
    "guncel duyuru",
    "son aciklanan",
)

GLOBAL_SYNTHESIS_QUERY_MARKERS: tuple[str, ...] = (
    "nasil",
    "basvuru",
    "sart",
    "kosul",
    "surec",
    "adim",
    "cap",
    "cift anadal",
    "cift ana dal",
    "yandal",
    "yan dal",
    "erasmus",
    "degisim programi",
)
