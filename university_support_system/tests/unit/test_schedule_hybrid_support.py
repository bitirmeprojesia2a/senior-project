from pathlib import Path

from scripts.index_documents import _resolve_collection_name
from src.core.constants import (
    Department,
    academic_schedule_collection_name,
    collection_name_for_department,
)
from src.rag.document_loader import Document, DocumentLoader
from src.rag.retriever import _resolve_collection_plan
from src.rag.search_planner import _looks_like_schedule_query


def test_index_documents_resolves_schedule_collection_for_schedule_source(tmp_path):
    source_path = tmp_path / "data" / "raw" / "academic_programs" / "ders_programlari"
    source_path.mkdir(parents=True)

    assert _resolve_collection_name(source_path, None) == academic_schedule_collection_name()


def test_document_loader_excludes_schedule_subdirectory_from_main_academic_scan(tmp_path, monkeypatch):
    academic_root = tmp_path / "academic_programs"
    academic_root.mkdir()
    (academic_root / "yonergeler").mkdir()
    (academic_root / "yonergeler" / "cap.txt").write_text("Cap metni " * 8, encoding="utf-8")
    (academic_root / "ders_programlari").mkdir()
    (academic_root / "ders_programlari" / "bilgisayar_programi.txt").write_text("Program metni " * 8, encoding="utf-8")

    loader = DocumentLoader(min_content_length=1)

    def _fake_load_file(file_path: Path, category: str = "genel") -> Document:
        return Document(
            content="Icerik",
            metadata={"source": file_path.name, "category": category},
        )

    monkeypatch.setattr(loader, "load_file", _fake_load_file)

    docs = loader.load_directory(
        academic_root,
        exclude_subdirectories=("ders_programlari",),
    )

    assert {doc.metadata["source"] for doc in docs} == {"cap.txt"}


def test_schedule_query_detection_requires_real_schedule_signal():
    assert _looks_like_schedule_query("Bilgisayar Muhendisligi ders programi nerede?")
    assert _looks_like_schedule_query("BIL309 dersi hangi saatte?")
    assert not _looks_like_schedule_query("BIL309 dersinin on kosulu nedir?")


def test_collection_plan_prefers_schedule_collection_for_schedule_queries():
    primary, fallback = _resolve_collection_plan(
        [Department.ACADEMIC_PROGRAMS],
        [Department.STUDENT_AFFAIRS],
        "Bilgisayar Muhendisligi ders programi nerede?",
    )

    assert primary == [academic_schedule_collection_name()]
    assert fallback == [
        collection_name_for_department(Department.ACADEMIC_PROGRAMS),
        collection_name_for_department(Department.STUDENT_AFFAIRS),
    ]
