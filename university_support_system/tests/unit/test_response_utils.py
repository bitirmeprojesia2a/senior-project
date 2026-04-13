"""Response post-processing tests."""

from src.orchestrators.response_utils import clean_final_answer


def test_clean_final_answer_removes_foreign_headings_and_english_lines():
    answer = (
        "Sonuc: Kayit yenileme ucreti doneme gore degisebilir.\n"
        "If the registration is canceled after renewal, the semester fee will not be refunded.\n"
        "Kanitlar:\n"
        "Staj defterini teslim etme suresi关于 bu konuda net bilgi bulunamadi."
    )

    cleaned = clean_final_answer(answer)

    assert "Sonuc:" not in cleaned
    assert "Kanitlar:" not in cleaned
    assert "registration is canceled" not in cleaned
    assert "关于" not in cleaned
    assert "Staj defterini teslim etme suresi" in cleaned


def test_clean_final_answer_replaces_common_foreign_words_inline():
    answer = (
        "Kosullar following gibidir.\n"
        "Yaz okulu hakkinda informatie verir misin?\n"
        "Staj basvuru belgelerini several kaynaklardan alabilirsiniz."
    )

    cleaned = clean_final_answer(answer)

    assert "following" not in cleaned
    assert "informatie" not in cleaned
    assert "several" not in cleaned
    assert "su sekild" in cleaned
    assert "bilgi" in cleaned
    assert "birden fazla kaynaktan" in cleaned


def test_clean_final_answer_replaces_additional_foreign_leaks():
    answer = (
        "Ayrintili bilgi icin siguientes maddelere bakin.\n"
        "Erasmus basvurusu icin once_online form doldurulur.\n"
        "Por favor belgeleri zamaninda teslim edin."
    )

    cleaned = clean_final_answer(answer)

    assert "siguientes" not in cleaned
    assert "once_online" not in cleaned
    assert "por favor" not in cleaned.lower()
    assert "asagidaki" in cleaned
    assert "once online" in cleaned
    assert "lutfen" in cleaned.lower()


def test_clean_final_answer_normalizes_unicode_diacritic_leaks():
    answer = "Yatay geçiş için not ortalaması, üniversitenin kullandığı hệ thốnge göre değişmektedir."

    cleaned = clean_final_answer(answer)

    assert "hệ" not in cleaned
    assert "thốnge" not in cleaned
    assert "sistem" in cleaned.lower()
