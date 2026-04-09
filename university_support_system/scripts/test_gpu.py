import os
import time
import logging

# Çevrimdışı korumasını KESİNLİKLE kaldır.
os.environ["RERANKER_LOCAL_FILES_ONLY"] = "false"
os.environ["RERANKER_MODEL"] = "cross-encoder/ms-marco-MiniLM-L-6-v2"
os.environ["EMBEDDING_DEVICE"] = "cuda"
os.environ["RERANKER_DEVICE"] = "cuda"

from src.core.config import settings
logging.getLogger("src").setLevel(logging.CRITICAL)

import torch
from src.rag.reranker import CrossEncoderReranker
from src.rag.embedder import Embedder

def test_hardware():
    print("="*60)
    print(" GPU PERFORMANS VE VRAM YÜKLEME TESTİ ")
    print("="*60)
    
    print(f"PyTorch Sürümü: {torch.__version__}")
    print(f"CUDA Algılandı: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"Kullanılan GPU: {torch.cuda.get_device_name(0)}")
        total_vram = torch.cuda.get_device_properties(0).total_memory / 1024**2
        print(f"Toplam VRAM: {total_vram:.0f} MB")

    print("\n--- [1] Embedder Yükleme ---")
    start = time.perf_counter()
    embedder = Embedder()
    _ = embedder.model
    elapsed = time.perf_counter() - start
    print(f" > Süre: {elapsed:.2f} saniye")
    print(f" > Cihaz: {embedder.resolved_device}")

    print("\n--- [2] Reranker Yükleme ---")
    start = time.perf_counter()
    reranker = CrossEncoderReranker()
    _ = reranker.model  # Şimdi HF model indirebilmeli
    elapsed = time.perf_counter() - start
    print(f" > Süre: {elapsed:.2f} saniye")
    print(f" > Cihaz: {reranker.resolved_device}")
    
    print("\n--- [3] Reranker Inference Testi (8 Aday x 1000 Harf) ---")
    dummy_query = "İkamet başvuruları ne zaman bitiyor?"
    dummy_candidates = [{"content": "Bu orta uzunlukta bir metindir. " * 30, "metadata": {"source": f"test_{i}.pdf"}} for i in range(8)]
    
    start = time.perf_counter()
    results = reranker.rerank(dummy_query, dummy_candidates, top_k=5)
    elapsed = time.perf_counter() - start
    print(f" > İşlem Süresi: {elapsed:.2f} saniye")
    
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / 1024**2
        reserved = torch.cuda.memory_reserved(0) / 1024**2
        print(f"\n[İŞLEM SONU VRAM DURUMU]\nTahsis Edilen: {allocated:.0f} MB\nAyrılan (Rezerve): {reserved:.0f} MB")

if __name__ == '__main__':
    test_hardware()
