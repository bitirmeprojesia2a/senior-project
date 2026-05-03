"""Specialist answer evidence extraction tests."""

from src.agents.base import BaseSpecialistAgent


def test_evidence_extraction_keeps_query_relevant_specific_sentences():
    content = (
        "Genel tanitim metni ogrenci isleri hakkinda bilgi verir. "
        "MADDE 19 - Ogrenci basarisiz oldugu bir secmeli ders yerine sonraki donemde devam etmek kaydiyla baska bir secmeli ders alabilir. "
        "Araya giren bir baska aciklama cumlesi daha eklendi. "
        "Bu paragraf spor etkinlikleri ve topluluk duyurulari hakkindadir. "
        "Bu cumle yemekhane duyurulari hakkindadir. "
        "Bu cumle kutuphane calisma saatleri hakkindadir. "
        "Bu cumle kampus ulasim bilgileri hakkindadir. "
        "MADDE 17 - Devam kosulu teorik derslerde yuzde 70, uygulamalarda yuzde 80 olarak uygulanir. "
        "Son bolum ilgisiz web sayfasi aciklamasidir."
    )

    excerpt = BaseSpecialistAgent._extract_evidence_content(
        "Basarisiz oldugum secmeli ders yerine baska secmeli alirsam devam kosulu nasil degisir?",
        content,
    )

    assert "MADDE 19" in excerpt
    assert "MADDE 17" in excerpt
    assert "spor etkinlikleri" not in excerpt
