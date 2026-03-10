"""
ChromaDB Koleksiyon Karşılaştırma Betiği

Aynı soruyu farklı chunk boyutlarıyla oluşturulmuş koleksiyonlarda arar.
Çıktıları yan yana görmemizi sağlar.

Kullanım:
    python scripts/compare_collections.py "Kayıt dondurma nasıl yapılır"
    python scripts/compare_collections.py "Müfredat nedir?" --department academic_programs
"""

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.constants import Department, collection_name_for_department, department_values
from src.rag.embedder import Embedder
from src.rag.indexer import ChromaIndexer


def _build_collection_family(base_collection: str) -> list[str]:
    """Aynı veri ailesine ait varyant koleksiyon adlarını üretir."""
    return [
        f"{base_collection}_256",
        base_collection,
        f"{base_collection}_1024",
    ]


def main():
    parser = argparse.ArgumentParser(description="Farklı koleksiyonlardaki arama sonuçlarını karşılaştırır.")
    parser.add_argument("query", type=str, help="Aranacak soru")
    parser.add_argument(
        "--department",
        type=str,
        choices=department_values(),
        default=None,
        help="Baz koleksiyonu departmandan üret (ör: student_affairs, academic_programs)",
    )
    parser.add_argument(
        "--collection-base",
        type=str,
        default=None,
        help="Karşılaştırılacak baz koleksiyon adı (ör: student_affairs_docs)",
    )

    args = parser.parse_args()

    base_collection = (
        args.collection_base
        or (
            collection_name_for_department(args.department)
            if args.department
            else collection_name_for_department(Department.STUDENT_AFFAIRS)
        )
    )
    collections = _build_collection_family(base_collection)

    print(f"\n🔍 Aranıyor: '{args.query}'")
    print(f"📚 Baz koleksiyon: {base_collection}")
    print("=" * 70)

    try:
        embedder = Embedder()
        query_vector = embedder.embed_single(args.query)

        for coll_name in collections:
            print(f"\n📁 KOLEKSİYON: {coll_name.upper()}")
            print("-" * 50)
            
            indexer = ChromaIndexer(collection_name=coll_name)
            
            # Koleksiyon veritabanında var mı kontrolü
            try:
                results = indexer.query(query_embedding=query_vector, n_results=2)
                
                if results.get("documents") and results["documents"][0]:
                    docs = results["documents"][0]
                    distances = results["distances"][0] if results.get("distances") else []
                    metadatas = results["metadatas"][0] if results.get("metadatas") else []

                    for i, (doc, dist) in enumerate(zip(docs, distances)):
                        src = metadatas[i].get("source", "?") if i < len(metadatas) else "?"
                        sim = 1 - dist
                        clean_doc = doc.replace("\n", " ").strip()
                        if len(clean_doc) > 200:
                            clean_doc = clean_doc[:200] + "..."
                            
                        print(f"[{i+1}] {src} (Benzerlik: {sim:.3f})")
                        print(f"    {clean_doc}\n")
                else:
                    print("Sonuç bulunamadı.\n")
                    
            except Exception as e:
                print(f"Bu koleksiyon henüz oluşturulmamış veya hata var: {e}\n")
            finally:
                indexer.close()

    except Exception as e:
        print(f"\n❌ Kritik Hata: {e}")

if __name__ == "__main__":
    main()
