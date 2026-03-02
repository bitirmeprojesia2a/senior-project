"""
Doküman İndeksleme CLI Script

Belgeleri ChromaDB'ye indeksler.

Kullanım:
    # Temel kullanım (varsayılan parametreler)
    python scripts/index_documents.py

    # Özel parametrelerle
    python scripts/index_documents.py --source "data/raw/student_affairs" --chunk-size 512 --reindex

    # Farklı kaynak klasör
    python scripts/index_documents.py --source "bitirme veriler - öğrenci işleri" --reindex

    # Test sorgusu ile
    python scripts/index_documents.py --test-query "Ders kaydı nasıl yapılır?"
"""

import argparse
import sys
from pathlib import Path

# Proje kök dizinini Python path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.pipeline import IndexingPipeline


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
        default="bitirme veriler - öğrenci işleri",
        help="Kaynak dosya klasörü (varsayılan: bitirme veriler - öğrenci işleri)",
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
        default="student_affairs_docs",
        help="ChromaDB koleksiyon adı (varsayılan: student_affairs_docs)",
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

    print("=" * 50)
    print("🚀 RAG İndeksleme Pipeline")
    print("=" * 50)
    print(f"   Kaynak:        {source_path}")
    print(f"   Chunk boyutu:  {args.chunk_size}")
    print(f"   Chunk örtüşme: {args.chunk_overlap}")
    print(f"   Koleksiyon:    {args.collection}")
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
