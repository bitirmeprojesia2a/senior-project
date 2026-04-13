"""Key-fact matching tests."""

from src.evaluation.key_fact_matching import check_key_facts, key_fact_present


def test_key_fact_matching_handles_number_word_variants():
    answer = "Muafiyet basvurusunu uc hafta icinde yapmali ve karar cikana kadar derslere devam etmelisiniz."
    assert key_fact_present(answer, "3. hafta") is True


def test_key_fact_matching_handles_diacritic_variants():
    answer = "Pedagojik formasyon dersleri transkripte dahil edilir."
    assert key_fact_present(answer, "dâhil") is True


def test_key_fact_matching_handles_decimal_separator_variants():
    answer = "Mezuniyet icin GANO en az 2.00 olmalidir."
    results = check_key_facts(answer, ["2,00"])
    assert results["2,00"] is True
