import os
import logging
from src.core.config import settings

# Testlerin daha temiz görünmesi için uyarıları kapattık
logging.getLogger("src").setLevel(logging.CRITICAL)

import torch
from src.rag.reranker import CrossEncoderReranker

def run_quality_test():
    print("="*60)
    print(" YENİ RERANKER (MiniLM) TÜRKÇE KALİTE TESTİ ")
    print("="*60)
    
    reranker = CrossEncoderReranker()
    
    test_cases = [
        {
            "query": "Erasmus başvuruları için hangi dil seviyesi isteniyor?",
            "candidates": [
                {"content": "Yaz okulu başvuruları için gerekli belgeler 11 Temmuz'da açıklanacaktır.", "metadata": {"id": "yanlis_1"}},
                {"content": "Değişim programlarına ve Erasmus'a başvuru yapacak öğrencilerin en az B2 seviyesinde dil yeterlilik belgesi sunması zorunludur.", "metadata": {"id": "DOGRU_CEVAP"}},
                {"content": "Yabancı dil hazırlık sınıfını geçemeyen öğrenciler bir sonraki yıl tekrar sınava girerler.", "metadata": {"id": "yanlis_2"}},
                {"content": "Erasmus ofisi, hafta içi her gün saat 10:00 ile 16:00 arası öğrencilere hizmet vermektedir.", "metadata": {"id": "tuzak_kelime_var_1"}},
                {"content": "Öğrencilerin harç ödemelerini dil seviyelerine göre değil, okudukları bölüme göre yapmaları gerekir.", "metadata": {"id": "yanlis_3"}},
            ]
        },
        {
            "query": "Yatay geçiş yapmak istiyorum, not ortalaması sınırı kaç?",
            "candidates": [
                {"content": "Yandal programına başvurmak isteyen öğrencilerin not ortalamasının en az 2.50 olması talep edilmektedir.", "metadata": {"id": "tuzak_kelime_yandal"}},
                {"content": "Kurum içi yatay geçişlerde öğrencinin genel not ortalamasının (GANO) en az 3.00 ve üstü olması şartı aranır.", "metadata": {"id": "DOGRU_CEVAP"}},
                {"content": "Geçiş belgeleri her yıl güz dönemi başlamadan önce sisteme yüklenmelidir.", "metadata": {"id": "yanlis_1"}},
                {"content": "Vize ve final not ortalaması sınırı dersi geçmek için 60 puan olarak belirlenmiştir.", "metadata": {"id": "yanlis_2_tuzak"}},
                {"content": "DGS ile geçiş yapan öğrencilerin alacağı dersler intibak komisyonu tarafından belirlenir.", "metadata": {"id": "yanlis_3"}},
            ]
        }
    ]

    for index, test in enumerate(test_cases, 1):
        print(f"\n[Test {index}] Soru: '{test['query']}'")
        
        # Adayları Reranker'a gönderiyoruz
        ranked_results = reranker.rerank(test['query'], test['candidates'], top_k=5)
        
        # Sonuçları göster
        print("Sıralama Sonuçları:")
        for rank, result in enumerate(ranked_results, 1):
            doc_id = result['metadata']['id']
            score = result['score']
            
            # Doğruyu bulduysa yeşil ok gibi gösterelim
            if doc_id == "DOGRU_CEVAP":
                print(f"  {rank}. [-> DOĞRU!] Puan: {score:>7.4f} | Metin: {result['content'][:50]}...")
            else:
                print(f"  {rank}. [Yanlış]   Puan: {score:>7.4f} | Metin: {result['content'][:50]}...")

if __name__ == '__main__':
    run_quality_test()
