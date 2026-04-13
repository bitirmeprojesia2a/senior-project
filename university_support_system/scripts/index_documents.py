"""
Doküman İndeksleme CLI Script

Belgeleri ChromaDB'ye indeksler.

Kullanım:
    # Temel kullanım (varsayılan parametreler)
    python scripts/index_documents.py

    # Özel parametrelerle
    python scripts/index_documents.py --source "data/raw/student_affairs" --chunk-size 512 --reindex

    # Farklı kaynak klasör
    python scripts/index_documents.py --source "data/raw/academic_programs" --reindex

    # Test sorgusu ile
    python scripts/index_documents.py --test-query "Ders kaydı nasıl yapılır?"
"""

import argparse
import sys
from pathlib import Path

# Proje kök dizinini Python path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.console import configure_utf8_stdio
from src.core.constants import (
    Department,
    academic_schedule_collection_name,
    collection_name_for_department,
    normalize_department_value,
)
from src.core.text_normalization import normalize_text
from src.rag.pipeline import IndexingPipeline

configure_utf8_stdio()


def _resolve_collection_name(source_path: Path, explicit_collection: str | None) -> str:
    """Kaynak klasöre göre koleksiyon adını çözümler."""
    if explicit_collection:
        return explicit_collection

    normalized_parts = {normalize_text(part) for part in source_path.resolve().parts}
    if "ders_programlari" in normalized_parts or "ders programlari" in normalized_parts:
        return academic_schedule_collection_name()

    department_values = {department.value: department for department in Department}
    for part in source_path.resolve().parts:
        normalized = normalize_department_value(part)
        if normalized in department_values:
            return collection_name_for_department(department_values[normalized])

    return collection_name_for_department(Department.STUDENT_AFFAIRS)


def main():
    parser = argparse.ArgumentParser(
        description="Dokümanları ChromaDB'ye indeksler.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python scripts/index_documents.py
  python scripts/index_documents.py --chunk-size 768 --chunk-overlap 128
  python scripts/index_documents.py --reindex --test-query "Burs başvurusu"
        """,
    )
    parser.add_argument(
        "--source",
        type=str,
        default="data/raw/student_affairs",
        help="Kaynak dosya klasörü (varsayılan: data/raw/student_affairs)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1024,
        help="Chunk boyutu — karakter (varsayılan: 1024)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=128,
        help="Chunk örtüşme — karakter (varsayılan: 128)",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default=None,
        help="ChromaDB koleksiyon adı (boş bırakılırsa kaynak klasörden otomatik çözülür)",
    )
    parser.add_argument(
        "--reindex",
        action="store_true",
        help="Mevcut koleksiyonu silip yeniden oluştur",
    )
    parser.add_argument(
        "--test-query",
        type=str,
        default=None,
        help="İndeksleme sonrası test sorgusu çalıştır",
    )
    parser.add_argument(
        "--chroma-url",
        type=str,
        default=None,
        help="ChromaDB URL (varsayılan: config'den okunur)",
    )

    args = parser.parse_args()

    # Kaynak klasörü kontrol et
    source_path = project_root / args.source
    if not source_path.exists():
        print(f"❌ Klasör bulunamadı: {source_path}")
        sys.exit(1)

    resolved_collection = _resolve_collection_name(source_path, args.collection)

    print("=" * 50)
    print("🚀 RAG İndeksleme Pipeline")
    print("=" * 50)
    print(f"   Kaynak:        {source_path}")
    print(f"   Chunk boyutu:  {args.chunk_size}")
    print(f"   Chunk örtüşme: {args.chunk_overlap}")
    print(f"   Koleksiyon:    {resolved_collection}")
    print(f"   Yeniden oluş:  {'Evet' if args.reindex else 'Hayır'}")
    print("=" * 50)

    # Pipeline oluştur ve çalıştır
    pipeline = IndexingPipeline(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        collection_name=args.collection,
        chroma_url=args.chroma_url,
    )

    try:
        stats = pipeline.run(source_path, reindex=args.reindex)

        if "error" in stats:
            print(f"❌ Hata: {stats['error']}")
            sys.exit(1)

        # Test sorgusu
        if args.test_query:
            pipeline.test_query(args.test_query)

        print("✅ İndeksleme tamamlandı!")

    except Exception as e:
        print(f"❌ Pipeline hatası: {e}")
        raise
    finally:
        pipeline.close()


if __name__ == "__main__":
    main()
