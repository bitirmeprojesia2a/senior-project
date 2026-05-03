from src.agents.student.graduation_utils import is_graduation_personal_query


def test_grade_viewing_location_is_not_personal_data_query():
    assert is_graduation_personal_query("Sinav notlarimi nereden gorebilirim?") is False


def test_grade_average_value_is_personal_data_query():
    assert is_graduation_personal_query("Not ortalamam kac?") is True
