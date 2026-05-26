from src.agents.student.graduation_utils import (
    is_graduation_personal_query,
    resolve_program_level,
)


def test_grade_viewing_location_is_not_personal_data_query():
    assert is_graduation_personal_query("Sinav notlarimi nereden gorebilirim?") is False


def test_grade_average_value_is_personal_data_query():
    assert is_graduation_personal_query("Not ortalamam kac?") is True


def test_program_level_resolver_handles_bachelor_program_names():
    assert resolve_program_level("Bilgisayar Muhendisligi icin kac?")["education_level"] == "bachelor"
    assert resolve_program_level("Elektrik-Elektronik Muhendisligi icin kac?")["education_level"] == "bachelor"
    assert resolve_program_level("Fizik ogretmenligi icin kac?")["education_level"] == "bachelor"


def test_program_level_resolver_does_not_force_240_for_long_programs():
    assert resolve_program_level("Tip icin kac?")["education_level"] == "special_long"
