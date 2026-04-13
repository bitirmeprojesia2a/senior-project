import shutil
import tempfile
import unicodedata
from pathlib import Path

import pytest

from src.rag.document_loader import Document, DocumentLoader


@pytest.fixture
def local_tmp_path():
    base_dir = Path(".codex_pytest_tmp")
    base_dir.mkdir(exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix="doc-loader-", dir=base_dir))
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_loader_normalizes_source_name_to_nfc(local_tmp_path):
    decomposed_name = unicodedata.normalize("NFD", "diş_hekimliği_yönergesi.txt")
    txt_file = local_tmp_path / decomposed_name
    txt_file.write_text("Bu bir test dokumanidir. " * 8, encoding="utf-8")

    loader = DocumentLoader(min_content_length=10)
    doc = loader.load_file(txt_file)

    expected_name = unicodedata.normalize("NFC", decomposed_name)
    assert doc is not None
    assert doc.metadata["source"] == expected_name
    assert doc.metadata["display_source"] == expected_name


def test_loader_supports_docx_files_via_docx_reader(local_tmp_path, monkeypatch):
    docx_file = local_tmp_path / "staj_formu.docx"
    docx_file.write_bytes(b"placeholder")

    loader = DocumentLoader(min_content_length=10)
    monkeypatch.setattr(loader, "_load_docx", lambda _path: "Staj formu icerigi. " * 8)

    doc = loader.load_file(docx_file, category="formlar")

    assert doc is not None
    assert doc.metadata["source"] == "staj_formu.docx"
    assert doc.metadata["file_type"] == "docx"
    assert doc.metadata["category"] == "formlar"
    assert "Staj formu icerigi" in doc.content


def test_loader_reports_missing_docx_dependency(local_tmp_path, monkeypatch):
    docx_file = local_tmp_path / "eksik_bagimlilik.docx"
    docx_file.write_bytes(b"placeholder")

    loader = DocumentLoader(min_content_length=10)

    def _raise_import_error(_name: str):
        raise ImportError("missing docx")

    monkeypatch.setattr("src.rag.document_loader.importlib.import_module", _raise_import_error)

    with pytest.raises(ValueError, match="python-docx"):
        loader._load_docx(docx_file)


def test_load_directory_includes_docx_and_skips_still_unsupported_files(local_tmp_path, monkeypatch):
    txt_file = local_tmp_path / "duyuru.txt"
    txt_file.write_text("Metin " * 8, encoding="utf-8")
    docx_file = local_tmp_path / "staj.docx"
    docx_file.write_bytes(b"placeholder")
    xlsx_file = local_tmp_path / "takvim.xlsx"
    xlsx_file.write_bytes(b"placeholder")

    loader = DocumentLoader(min_content_length=1)

    def _fake_load_file(file_path: Path, category: str = "genel") -> Document:
        return Document(
            content="Icerik",
            metadata={
                "source": file_path.name,
                "category": category,
                "file_type": file_path.suffix.lstrip("."),
            },
        )

    monkeypatch.setattr(loader, "load_file", _fake_load_file)

    docs = loader.load_directory(local_tmp_path)

    assert {doc.metadata["source"] for doc in docs} == {"duyuru.txt", "staj.docx"}
