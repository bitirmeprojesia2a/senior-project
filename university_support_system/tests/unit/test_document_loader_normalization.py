import shutil
import tempfile
import unicodedata
from pathlib import Path

import pytest

from src.rag.document_loader import DocumentLoader


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
