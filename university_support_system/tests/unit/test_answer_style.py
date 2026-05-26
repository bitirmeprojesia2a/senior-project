from src.core.profiling import QueryProfiler, activate_profiler
from src.quality.answer_style import (
    analyze_answer_length,
    build_answer_length_instruction,
    is_length_exempt_query,
    record_answer_length_telemetry,
)


def test_normal_question_gets_short_answer_instruction():
    instruction = build_answer_length_instruction("CAP basvuru sartlari nelerdir?")

    assert "en fazla 4 cumle" in instruction
    assert "en fazla 3 kisa madde" in instruction


def test_schedule_question_is_length_exempt():
    instruction = build_answer_length_instruction("Bilgisayar Muhendisligi ders programi ne?")

    assert is_length_exempt_query("Bilgisayar Muhendisligi ders programi ne?") is True
    assert "Gerekli satirlari kesme" in instruction


def test_transcript_question_is_length_exempt():
    assert is_length_exempt_query("Transkript belgesini incele, kaldigim dersleri soyle") is True


def test_answer_length_analysis_warns_only_for_non_exempt_long_answers():
    answer = "Bir. Iki. Uc. Dort. Bes. Alti. Yedi."

    telemetry = analyze_answer_length("CAP basvuru sartlari nelerdir?", answer)

    assert telemetry["policy"] == "normal"
    assert telemetry["sentence_count"] == 7
    assert telemetry["warning"] is True
    assert "normal_answer_sentence_count_high" in telemetry["warnings"]


def test_answer_length_analysis_does_not_warn_for_schedule_lists():
    answer = "\n".join(f"- Ders {index}" for index in range(10))

    telemetry = analyze_answer_length("Bilgisayar Muhendisligi ders programi ne?", answer)

    assert telemetry["policy"] == "exempt"
    assert telemetry["bullet_count"] == 10
    assert telemetry["warning"] is False


def test_record_answer_length_telemetry_uses_active_profiler_query():
    profiler = QueryProfiler(label="answer-length")
    profiler.set_attribute("query", "Guncel duyurular neler?")

    with activate_profiler(profiler):
        telemetry = record_answer_length_telemetry(answer="- Duyuru 1\n- Duyuru 2")

    assert telemetry["policy"] == "exempt"
    assert profiler.get_attribute("answer_length") == telemetry
