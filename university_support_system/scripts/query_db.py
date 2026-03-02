"""
ChromaDB Hızlı Sorgu Scripti — v2

Sadece arama yapar, yeniden indeksleme yapmaz.
Hız testi ve RAG sonuçlarının kalitesini ölçmek için kullanılır.

E5 modeli kullanıldığında sorguya otomatik "query:" prefix'i eklenir.

Kullanım:
    python scripts/query_db.py "Ders kaydı nasıl yapılır?"
    python scripts/query_db.py "Kayıt yenileme işlemleri" --top-k 5
"""

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.embedder import Embedder
from src.rag.indexer import ChromaIndexer


def main():
    parser = argparse.ArgumentParser(description="ChromaDB'de hızlı semantik arama yapar.")
    parser.add_argument("query", type=str, help="Aranacak soru veya metin")
    parser.add_argument("--top-k", type=int, default=5, help="Döndürülecek sonuç sayısı (varsayılan: 5)")
    parser.add_argument("--collection", type=str, default="student_affairs_docs", help="Koleksiyon adı")

    args = parser.parse_args()

    print(f"\n🔍 Aranıyor: '{args.query}'")
    print(f"   Model: E5 (sorgu prefix'i otomatik eklenir)")
    print("-" * 50)

    try:
        # Sadece embedder ve indexer'ı başlat
        embedder = Embedder()
        indexer = ChromaIndexer(collection_name=args.collection)

        # Sorguyu vektöre çevir — is_query=True (E5 prefix eklenir)
        query_vector = embedder.embed_single(args.query, is_query=True)

        # Veritabanında ara
        results = indexer.query(query_embedding=query_vector, n_results=args.top_k)

        if results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            distances = results["distances"][0] if results.get("distances") else []
            metadatas = results["metadatas"][0] if results.get("metadatas") else []

            for i, (doc, dist) in enumerate(zip(docs, distances)):
                source = metadatas[i].get("source", "?") if i < len(metadatas) else "?"
                category = metadatas[i].get("category", "?") if i < len(metadatas) else "?"
                similarity = 1 - dist

                print(f"[{i+1}] Dosya: {source} | Kategori: {category} | Benzerlik: {similarity:.3f}")

                # Metni biraz temiz gösterelim
                clean_doc = doc.replace("\n", " ").strip()
                if len(clean_doc) > 300:
                    clean_doc = clean_doc[:300] + "..."
                print(f"    METİN: {clean_doc}\n")
        else:
            print("Sonuç bulunamadı.")

    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        import traceback
        traceback.print_exc()
    finally:
        indexer.close()


if __name__ == "__main__":
    main()
