"""
Hibrit Arama (Hybrid Search) Test Betiği — v2

HybridRetriever kullanarak BM25 (kelime) + ChromaDB (vektör) +
Sorgu Ön İşleme (sinonim genişletme) ile aynı anda soru sorar.

Kullanım:
    python scripts/test_hybrid_search.py "kayıt dondurma nasıl yapılır"
    python scripts/test_hybrid_search.py "Çift anadal başvurusu nasıl yapılır"
    python scripts/test_hybrid_search.py "yaz okulu harç ücreti" --bm25-weight 0.6
    python scripts/test_hybrid_search.py "Müfredat nedir" --department academic_programs
"""

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.constants import department_values
from src.rag.retriever import HybridRetriever


def main():
    parser = argparse.ArgumentParser(description="Hibrit RAG Arama (BM25 + Semantic + Sorgu Genişletme)")
    parser.add_argument("query", type=str, help="Sorulacak soru / Kelimeler")
    parser.add_argument(
        "--collection",
        type=str,
        default=None,
        help="Belirli bir koleksiyon adı (verilmezse yönlendirme akışı kullanılır)",
    )
    parser.add_argument(
        "--department",
        type=str,
        choices=department_values(),
        default=None,
        help="Aramayı belirli bir departmanla sınırla",
    )
    parser.add_argument("--top-k", type=int, default=5, help="Getirilecek sonuç sayısı")
    parser.add_argument("--bm25-weight", type=float, default=0.5, help="BM25 (Kelime Eşleşmesi) Ağırlığı")
    parser.add_argument("--vector-weight", type=float, default=0.5, help="Vector (Semantik) Ağırlığı")
    parser.add_argument("--no-expansion", action="store_true", help="Sinonim genişletmeyi devre dışı bırak")
    parser.add_argument("--full", action="store_true", help="Metin kısaltma yapma, tamamını göster")

    args = parser.parse_args()

    print("=" * 70)
    print("🚀 HİBRİT ARAMA v3 (BM25 + Semantic + Cross-Encoder Reranking)")
    print("=" * 70)
    print(f"Soru/Kelime   : '{args.query}'")
    print(f"Ağırlıklar    : BM25: {args.bm25_weight} | Semantic: {args.vector_weight}")
    print(f"Genişletme    : {'Kapalı' if args.no_expansion else 'Açık'}")
    if args.collection:
        print(f"Koleksiyon    : {args.collection}")
    elif args.department:
        print(f"Departman     : {args.department}")
    else:
        print("Arama Modu    : Otomatik yönlendirme + kontrollü fallback")
    print("-" * 70)

    try:
        retriever_kwargs = {
            "k": args.top_k,
            "bm25_weight": args.bm25_weight,
            "chroma_weight": args.vector_weight,
            "enable_query_expansion": not args.no_expansion,
        }
        if args.collection:
            retriever_kwargs["collection_name"] = args.collection

        retriever = HybridRetriever(**retriever_kwargs)

        print("\nSonuçlar çekiliyor (Sorgu Genişletme + Ensemble Reranking)...\n")

        results = retriever.search(
            args.query,
            top_k=args.top_k,
            department=args.department,
        )

        if not results:
            print("❌ Hiçbir eşleşme bulunamadı.")
            return

        print("🎯 Hibrit Arama Sonuçları:\n")
        for i, result in enumerate(results):
            text = result["content"].replace("\n", " ").strip()
            source = result["source"]
            category = result["category"]
            score = result["score"]

            print(f"[{i+1}] Kaynak: {source} | Kategori: {category} | Skor: {score:.3f}")
            max_len = 0 if args.full else 500
            if max_len and len(text) > max_len:
                display_text = text[:max_len] + "..."
            else:
                display_text = text
            print(f"    METİN ({len(text)} kar.): {display_text}\n")

        retriever.close()

    except Exception as e:
        print(f"\n❌ Kritik Hata: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
