"""Diagnostic: announcement short-circuit neden calismiyor?"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from src.core.text_normalization import normalize_text, contains_any_normalized
from src.core.query_markers import ANNOUNCEMENT_QUERY_MARKERS
from src.orchestrators.query_policy import looks_like_announcement_query

test_queries = [
    "Güncel duyurular nelerdir?",
    "Son duyurular neler?",
    "Son açıklanan haberler neler?",
    "Muhendislik fakultesindeki son duyurular neler?",
    "Bilgisayar muhendisligindeki son duyurular neler?",
    "Bilgisayar muhendisligi ara sinav programi duyurusu var mi?",
    "Bilgisayar muhendisligi ara sinav programi nereden takip edilir?",
    "Bilgisayar muhendisligi tek ders sinavi duyurusu var mi?",
    "Peki sinav programi ile ilgili olan var mi?",
    "Bir de ders programi linki olan var mi?",
]

print("=== ANNOUNCEMENT_QUERY_MARKERS ===")
print(ANNOUNCEMENT_QUERY_MARKERS)
print()

for q in test_queries:
    norm = normalize_text(q)
    matches = [normalize_text(m) for m in ANNOUNCEMENT_QUERY_MARKERS if normalize_text(m) in norm]
    result = looks_like_announcement_query(q)
    print(f"Q: {q}")
    print(f"  normalized: {norm}")
    print(f"  matched markers: {matches}")
    print(f"  looks_like_announcement: {result}")
    print()
