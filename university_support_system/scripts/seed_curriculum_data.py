"""
OMU Bilgisayar Muhendisligi Lisans Mufredat Verisi Seed Scripti

Tum zorunlu dersler, teknik/sosyal/lab secmeliler, staj, MUP, sanayi uygulamasi
ve onkosul iliskileri (VE / VEYA gruplamasiyla) veritabanina eklenir.

Kullanim:
    python -m scripts.seed_curriculum_data
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.console import configure_utf8_stdio
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.models import Course, CoursePrerequisite

configure_utf8_stdio()

engine = create_engine(settings.postgres.sync_url, future=True)

DEPT = "Bilgisayar Muhendisligi"

# ── course_type degerleri ──
Z = "zorunlu"
TS = "teknik_secmeli"
SS = "sosyal_secmeli"
LS = "lab_secmeli"
STAJ = "staj"
MUP = "mup"
SANAYI = "sanayi"
GRUP = "secmeli_grup"
BITIRME = "bitirme"

# ────────────────────────────────────────────────
# Ders Tanimlari
# Format: (code, name, dept, T, U, L, K, AKTS, sem, type, group)
# ────────────────────────────────────────────────

COURSES: list[tuple] = [
    # ========== 1. YARIYIL ==========
    ("BIL101", "Bilgisayar Muhendisligine Giris", DEPT, 3, 0, 0, 3, 5, 1, Z, None),
    ("BIL103", "Programlamaya Giris I", DEPT, 2, 0, 2, 3, 5, 1, Z, None),
    ("TBMAT111", "Matematik 1", "Temel Bilimler - Matematik", 2, 2, 0, 3, 5, 1, Z, None),
    ("TBFIZ121", "Fizik 1", "Temel Bilimler - Fizik", 3, 0, 2, 4, 6, 1, Z, None),
    ("BIL123", "Ayrik Matematik", DEPT, 3, 1, 0, 4, 5, 1, Z, None),
    ("YD113", "Yabanci Dil I", "Yabanci Diller", 1, 2, 0, 2, 2, 1, Z, None),
    ("ATI101", "Ataturk Ilkeleri ve Inkilap Tarihi I", "Ataturk Ilkeleri", 2, 0, 0, 2, 2, 1, Z, None),

    # ========== 2. YARIYIL ==========
    ("BIL108", "Elektrik Devreleri ve Elektronik", DEPT, 3, 0, 2, 4, 5, 2, Z, None),
    ("BIL104", "Programlamaya Giris II", DEPT, 2, 0, 2, 3, 5, 2, Z, None),
    ("TBMAT112", "Matematik 2", "Temel Bilimler - Matematik", 2, 2, 0, 3, 5, 2, Z, None),
    ("TBFIZ122", "Fizik 2", "Temel Bilimler - Fizik", 3, 0, 2, 4, 6, 2, Z, None),
    ("BIL124", "Olasilik ve Istatistige Giris", DEPT, 3, 0, 0, 3, 5, 2, Z, None),
    ("YD114", "Yabanci Dil II", "Yabanci Diller", 1, 2, 0, 2, 2, 2, Z, None),
    ("ATI102", "Ataturk Ilkeleri ve Inkilap Tarihi II", "Ataturk Ilkeleri", 2, 0, 0, 2, 2, 2, Z, None),

    # ========== 3. YARIYIL ==========
    ("BIL203", "Veri Yapilari", DEPT, 3, 0, 0, 3, 5, 3, Z, None),
    ("BIL215", "Sayisal Devreler ve Mantiksal Tasarim", DEPT, 3, 0, 2, 4, 5, 3, Z, None),
    ("BIL225", "Dogrusal Cebir", DEPT, 3, 1, 0, 4, 4, 3, Z, None),
    ("BIL227", "Diferansiyel Denklemler", DEPT, 3, 1, 0, 4, 4, 3, Z, None),
    ("TDI101", "Turk Dili I", "Turk Dili", 2, 0, 0, 2, 2, 3, Z, None),
    ("ISG101", "Is Sagligi ve Guvenligi I", "Is Sagligi ve Guvenligi", 2, 0, 0, 2, 2, 3, Z, None),
    ("YDI213", "Ileri Ingilizce I", "Yabanci Diller", 2, 2, 0, 3, 4, 3, Z, None),

    # BİLSEÇ-1 grubu ve dersleri
    ("BILSEC-1", "Teknik Secmeli Ders 1 (Grup)", DEPT, 2, 1, 0, 3, 4, 3, GRUP, "BILSEC-1"),
    ("BIL235", "Java I", DEPT, 2, 1, 0, 3, 4, 3, TS, "BILSEC-1"),
    ("BIL237", "Ileri Programlama", DEPT, 2, 1, 0, 3, 4, 3, TS, "BILSEC-1"),

    # ========== 4. YARIYIL ==========
    ("BIL204", "Algoritmalar", DEPT, 3, 0, 0, 3, 6, 4, Z, None),
    ("BIL212", "Nesneye Yonelik Programlama", DEPT, 2, 2, 0, 3, 6, 4, Z, None),
    ("BIL214", "Sayisal Cozumleme", DEPT, 3, 1, 0, 4, 6, 4, Z, None),
    ("YDI214", "Ileri Ingilizce II", "Yabanci Diller", 2, 2, 0, 3, 4, 4, Z, None),
    ("TDI102", "Turk Dili II", "Turk Dili", 2, 0, 0, 2, 2, 4, Z, None),
    ("ISG102", "Is Sagligi ve Guvenligi II", "Is Sagligi ve Guvenligi", 2, 0, 0, 2, 2, 4, Z, None),

    # BİLSEÇ-2 grubu ve dersleri
    ("BILSEC-2", "Teknik Secmeli Ders 2 (Grup)", DEPT, 2, 1, 0, 3, 4, 4, GRUP, "BILSEC-2"),
    ("BIL242", "Java II", DEPT, 2, 1, 0, 3, 4, 4, TS, "BILSEC-2"),
    ("BIL244", "Cizge Kurami", DEPT, 2, 1, 0, 3, 4, 4, TS, "BILSEC-2"),

    # ========== 5. YARIYIL ==========
    ("BIL313", "Sistem Programlama", DEPT, 2, 1, 0, 3, 6, 5, Z, None),
    ("BIL305", "Bilgisayar Mimarisi", DEPT, 3, 0, 0, 3, 6, 5, Z, None),
    ("BIL309", "Veritabani Yonetim Sistemleri", DEPT, 3, 0, 0, 3, 6, 5, Z, None),
    ("MUH301", "Girisimcilik ve Yenilikcilik", "Muhendislik Fakultesi Ortak", 2, 0, 0, 2, 5, 5, Z, None),
    ("SSD1", "Sosyal Secmeli Ders I (Grup)", "Sosyal Secmeli", 2, 0, 0, 2, 2, 5, SS, None),
    ("BIL392", "Staj", DEPT, 0, 0, 0, 0, 10, 5, STAJ, None),

    # BİLSEÇ-4 grubu ve dersleri
    ("BILSEC-4", "Teknik Secmeli Ders 4 (Grup)", DEPT, 3, 0, 0, 3, 5, 5, GRUP, "BILSEC-4"),
    ("BIL321", "Web Teknolojileri", DEPT, 3, 0, 0, 3, 5, 5, TS, "BILSEC-4"),
    ("BIL323", "Bilgisayar Muhendisliginde Matematiksel Teknikler", DEPT, 3, 0, 0, 3, 5, 5, TS, "BILSEC-4"),
    ("BIL325", "Sayilar Teorisi ve Uygulamalari", DEPT, 3, 0, 0, 3, 5, 5, TS, "BILSEC-4"),
    ("BIL327", "Mobil Programlama", DEPT, 3, 0, 0, 3, 5, 5, TS, "BILSEC-4"),
    ("BIL329", "Karmasik Islevler ve Donusumler", DEPT, 3, 0, 0, 3, 5, 5, TS, "BILSEC-4"),
    ("BIL341", "Yoneylem Arastirmasi", DEPT, 3, 0, 0, 3, 5, 5, TS, "BILSEC-4"),
    ("BIL343", "Sayisal Denetim 1", DEPT, 3, 0, 0, 3, 5, 5, TS, "BILSEC-4"),
    ("BIL349", "Bilimsel Hesaplama", DEPT, 3, 0, 0, 3, 5, 5, TS, "BILSEC-4"),

    # ========== 6. YARIYIL ==========
    ("BIL304", "Isletim Sistemleri", DEPT, 3, 0, 0, 3, 6, 6, Z, None),
    ("BIL312", "Ozdevinirler Kurami", DEPT, 3, 0, 0, 3, 5, 6, Z, None),
    ("BIL314", "Sinyaller ve Sistemler", DEPT, 3, 0, 0, 3, 5, 6, Z, None),
    ("BIL318", "Mikroislemciler", DEPT, 3, 0, 0, 3, 5, 6, Z, None),
    ("BIL322", "Mesleki Ingilizce", DEPT, 3, 0, 0, 3, 4, 6, Z, None),

    # BİLSEÇ-5 grubu ve dersleri
    ("BILSEC-5", "Teknik Secmeli Ders 5 (Grup)", DEPT, 3, 0, 0, 3, 5, 6, GRUP, "BILSEC-5"),
    ("BIL342", "Unix Sistem Yonetimi", DEPT, 3, 0, 0, 3, 5, 6, TS, "BILSEC-5"),
    ("BIL344", "Ileri SQL", DEPT, 3, 0, 0, 3, 5, 6, TS, "BILSEC-5"),
    ("BIL346", "Web Programlama", DEPT, 3, 0, 0, 3, 5, 6, TS, "BILSEC-5"),
    ("BIL348", "Bilgisayar Aritmetigi", DEPT, 3, 0, 0, 3, 5, 6, TS, "BILSEC-5"),
    ("BIL362", "Veri Iletisimi", DEPT, 3, 0, 0, 3, 5, 6, TS, "BILSEC-5"),
    ("BIL364", "Sayisal Denetim 2", DEPT, 3, 0, 0, 3, 5, 6, TS, "BILSEC-5"),

    # ========== 7. YARIYIL ==========
    ("BIL401", "Bilgisayar Aglari", DEPT, 3, 0, 0, 3, 5, 7, Z, None),
    ("BIL407", "Yazilim Muhendisligi", DEPT, 3, 0, 0, 3, 6, 7, Z, None),
    ("BIL409", "Proje Tasarimi", DEPT, 2, 2, 0, 3, 4, 7, Z, None),
    ("SAN.SEC.BIL", "Sanayi Uygulamasi (Secmeli)", DEPT, 0, 14, 0, 7, 15, 7, SANAYI, None),

    # BİLSEÇ-6 grubu ve dersleri
    ("BILSEC-6", "Teknik Secmeli Ders 6 (Grup)", DEPT, 3, 0, 0, 3, 6, 7, GRUP, "BILSEC-6"),
    ("BIL423", "Programlama Dilleri", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-6"),
    ("BIL431", "Bilgi Guvenligi", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-6"),
    ("BIL433", "Bilgisayar Grafigi", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-6"),
    ("BIL435", "Hesap Edilebilirlik Kurami", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-6"),
    ("BIL437", "Kombinatorik", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-6"),
    ("BIL439", "Kriptografiye Giris", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-6"),
    ("BIL447", "Oyun Programlama", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-6"),
    ("BIL449", "Mobil Aglar", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-6"),
    ("BIL451", "Bilgisayar Aglarinda Ozel Konular", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-6"),
    ("BIL457", "Finansal Matematik", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-6"),
    ("BIL463", "Gomulu Sistemlere Giris", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-6"),
    ("BIL467", "Proje Yonetimi", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-6"),

    # BİLSEÇ-7 grubu ve dersleri
    ("BILSEC-7", "Teknik Secmeli Ders 7 (Grup)", DEPT, 3, 0, 0, 3, 6, 7, GRUP, "BILSEC-7"),
    ("BIL429", "Makine Ogrenimine Giris", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-7"),
    ("BIL441", "Yapay Zeka", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-7"),
    ("BIL443", "Robotik", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-7"),
    ("BIL445", "Bulanik Mantik", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-7"),
    ("BIL453", "Bilgisayar Muhendisligi Ozel Konular I", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-7"),
    ("BIL455", "Insan Bilgisayar Arayuzu", DEPT, 3, 0, 0, 3, 6, 7, TS, "BILSEC-7"),

    # LABSEÇ-I grubu ve dersleri
    ("LABSEC-I", "Secmeli Laboratuvar I (Grup)", DEPT, 0, 0, 2, 1, 3, 7, GRUP, "LABSEC-I"),
    ("BIL417", "Goruntu Isleme Laboratuvari", DEPT, 0, 0, 2, 1, 3, 7, LS, "LABSEC-I"),
    ("BIL465", "Bilgisayar Ag Yonetimi Laboratuvari", DEPT, 0, 0, 2, 1, 3, 7, LS, "LABSEC-I"),
    ("BIL479", "Veri Tabani Yonetimi Laboratuvari", DEPT, 0, 0, 2, 1, 3, 7, LS, "LABSEC-I"),
    ("BIL481", "Web Programlama Laboratuvari", DEPT, 0, 0, 2, 1, 3, 7, LS, "LABSEC-I"),
    ("BIL483", "Bilgisayar Muhendisliginde Ozel Konular Laboratuvari", DEPT, 0, 0, 2, 1, 3, 7, LS, "LABSEC-I"),

    # ========== 8. YARIYIL ==========
    ("BIL400", "Bitirme Projesi", DEPT, 1, 2, 0, 2, 13, 8, BITIRME, None),
    ("SSD2", "Sosyal Secmeli Ders II (Grup)", "Sosyal Secmeli", 2, 0, 0, 2, 2, 8, SS, None),
    ("BIL502", "Mesleki Uygulama Programi", DEPT, 6, 4, 2, 9, 30, 8, MUP, None),

    # BİLSEÇ-8 grubu ve dersleri
    ("BILSEC-8", "Teknik Secmeli Ders 8 (Grup)", DEPT, 2, 2, 0, 3, 6, 8, GRUP, "BILSEC-8"),
    ("BIL504", "Bilgisayarli Goruye Giris", DEPT, 2, 2, 0, 3, 6, 8, TS, "BILSEC-8"),
    ("BIL506", "Yazilim Test Surecleri", DEPT, 2, 2, 0, 3, 6, 8, TS, "BILSEC-8"),
    ("BIL508", "Cografi Bilgi Sistemleri", DEPT, 2, 2, 0, 3, 6, 8, TS, "BILSEC-8"),
    ("BIL510", "Programlamada Ozel Konular", DEPT, 2, 2, 0, 3, 6, 8, TS, "BILSEC-8"),
    ("BIL512", "Prolog", DEPT, 2, 2, 0, 3, 6, 8, TS, "BILSEC-8"),
    ("BIL514", "Yapay Sinir Aglari", DEPT, 2, 2, 0, 3, 6, 8, TS, "BILSEC-8"),
    ("BIL516", "Alan Programlanabilir Kapi Dizileri", DEPT, 2, 2, 0, 3, 6, 8, TS, "BILSEC-8"),
    ("BIL518", "Derleyici Tasarimi", DEPT, 2, 2, 0, 3, 6, 8, TS, "BILSEC-8"),

    # BİLSEÇ-9 grubu ve dersleri
    ("BILSEC-9", "Teknik Secmeli Ders 9 (Grup)", DEPT, 2, 2, 0, 3, 6, 8, GRUP, "BILSEC-9"),
    ("BIL520", "Bilgi Teorisi", DEPT, 2, 2, 0, 3, 6, 8, TS, "BILSEC-9"),
    ("BIL522", "Kodlama Teorisi", DEPT, 2, 2, 0, 3, 6, 8, TS, "BILSEC-9"),
    ("BIL524", "Kritik Altyapilar ve Guvenligi", DEPT, 2, 2, 0, 3, 6, 8, TS, "BILSEC-9"),
    ("BIL526", "Bilgisayar Muhendisligi Ozel Konular II", DEPT, 2, 2, 0, 3, 6, 8, TS, "BILSEC-9"),
    ("BIL528", "Tibbi Bilisime Giris", DEPT, 2, 2, 0, 3, 6, 8, TS, "BILSEC-9"),
    ("BIL530", "Muhendislik Ekonomisi", DEPT, 2, 2, 0, 3, 6, 8, TS, "BILSEC-9"),
    ("BIL532", "Adli Bilisim", DEPT, 2, 2, 0, 3, 6, 8, TS, "BILSEC-9"),

    # LABSEÇ-II grubu ve dersleri
    ("LABSEC-II", "Secmeli Laboratuvar II (Grup)", DEPT, 0, 0, 2, 1, 3, 8, GRUP, "LABSEC-II"),
    ("BIL416", "Bilgisayarli Goru Laboratuvari", DEPT, 0, 0, 2, 1, 3, 8, LS, "LABSEC-II"),
    ("BIL418", "Yazilim Test Surecleri Laboratuvari", DEPT, 0, 0, 2, 1, 3, 8, LS, "LABSEC-II"),
    ("BIL434", "Cografi Bilgi Sistemleri Laboratuvari", DEPT, 0, 0, 2, 1, 3, 8, LS, "LABSEC-II"),
    ("BIL478", "Programlamada Ozel Konular Lab.", DEPT, 0, 0, 0, 1, 3, 8, LS, "LABSEC-II"),
    ("BIL482", "Mikrodenetleyici Lab.", DEPT, 0, 0, 2, 1, 3, 8, LS, "LABSEC-II"),
    ("BIL488", "Veri Tabani Laboratuvari", DEPT, 0, 0, 2, 1, 3, 8, LS, "LABSEC-II"),
    ("BIL490", "Yazilim Muhendisligi Laboratuvari", DEPT, 0, 0, 2, 1, 3, 8, LS, "LABSEC-II"),
    ("BIL494", "Web Teknolojileri Laboratuvari", DEPT, 0, 0, 2, 1, 3, 8, LS, "LABSEC-II"),
    ("BIL496", "Bilgisayar Aglari Laboratuvari", DEPT, 0, 0, 2, 1, 3, 8, LS, "LABSEC-II"),

]

# ────────────────────────────────────────────────
# Onkosul Tanimlari
# Format: (ders_kodu, [(onkosul_kodu, grup), ...])
#   Ayni grup icindeki onkosullar = VEYA (OR)
#   Farkli gruplar = VE (AND)
# ────────────────────────────────────────────────

PREREQUISITES: list[tuple[str, list[tuple[str, int]]]] = [
    # 2. yariyil
    ("BIL104", [("BIL103", 1)]),
    ("TBMAT112", [("TBMAT111", 1)]),
    ("TBFIZ122", [("TBFIZ121", 1)]),

    # 3. yariyil
    ("BIL203", [("BIL104", 1)]),
    ("BIL225", [("TBMAT112", 1)]),
    ("BIL227", [("TBMAT112", 1)]),

    # 3. yariyil secmeliler
    ("BIL235", [("BIL104", 1)]),
    ("BIL237", [("BIL104", 1)]),

    # 4. yariyil
    ("BIL204", [("BIL203", 1)]),
    ("BIL212", [("BIL104", 1)]),
    ("BIL214", [("TBMAT112", 1)]),

    # 4. yariyil secmeliler
    ("BIL242", [("BIL104", 1)]),
    ("BIL244", [("BIL104", 1)]),

    # 5. yariyil
    ("BIL313", [("BIL104", 1)]),
    ("BIL305", [("BIL215", 1)]),
    ("BIL309", [("BIL104", 1)]),

    # 5. yariyil secmeliler (BILSEC-4 → onkosul BILSEC-1)
    ("BIL321", [("BILSEC-1", 1)]),
    ("BIL323", [("BILSEC-1", 1)]),
    ("BIL325", [("BILSEC-1", 1)]),
    ("BIL327", [("BILSEC-1", 1)]),
    ("BIL329", [("BILSEC-1", 1)]),
    ("BIL341", [("BILSEC-1", 1)]),
    ("BIL343", [("BILSEC-1", 1)]),
    ("BIL349", [("BILSEC-1", 1)]),

    # 6. yariyil
    ("BIL304", [("BIL313", 1)]),
    ("BIL318", [("BIL215", 1)]),

    # 6. yariyil secmeliler (BILSEC-5 → onkosul BILSEC-2)
    ("BIL342", [("BILSEC-2", 1)]),
    ("BIL344", [("BILSEC-2", 1)]),
    ("BIL346", [("BILSEC-2", 1)]),
    ("BIL348", [("BILSEC-2", 1)]),
    ("BIL362", [("BILSEC-2", 1)]),
    ("BIL364", [("BILSEC-2", 1)]),

    # 7. yariyil secmeliler (LABSEC-I → onkosul BILSEC-5)
    ("BIL417", [("BILSEC-5", 1)]),
    ("BIL465", [("BILSEC-5", 1)]),
    ("BIL479", [("BILSEC-5", 1)]),
    ("BIL481", [("BILSEC-5", 1)]),
    ("BIL483", [("BILSEC-5", 1)]),

    # 8. yariyil
    ("BIL400", [("BIL409", 1)]),

    # 8. yariyil secmeliler (LABSEC-II → onkosul BIL407)
    ("BIL416", [("BIL407", 1)]),
    ("BIL418", [("BIL407", 1)]),
    ("BIL434", [("BIL407", 1)]),
    ("BIL478", [("BIL407", 1)]),
    ("BIL482", [("BIL407", 1)]),
    ("BIL488", [("BIL407", 1)]),
    ("BIL490", [("BIL407", 1)]),
    ("BIL494", [("BIL407", 1)]),
    ("BIL496", [("BIL407", 1)]),
]


def _get_or_create_course(session: Session, **kwargs) -> Course:
    code = kwargs["course_code"]
    existing = session.scalar(select(Course).where(Course.course_code == code))
    if existing:
        for k, v in kwargs.items():
            if v is not None:
                setattr(existing, k, v)
        return existing
    course = Course(**kwargs)
    session.add(course)
    session.flush()
    return course


def _clean_old_prerequisites(session: Session) -> int:
    """Mevcut tum onkosul kayitlarini siler (temiz baslangic icin)."""
    result = session.execute(delete(CoursePrerequisite))
    session.flush()
    return result.rowcount  # type: ignore[union-attr]


def seed_curriculum(session: Session) -> None:
    """Insert/update the full Computer Engineering curriculum."""

    deleted = _clean_old_prerequisites(session)
    print(f"  {deleted} eski onkosul kaydi silindi.")

    code_to_obj: dict[str, Course] = {}

    # ── 1) Dersleri ekle / guncelle ──
    for row in COURSES:
        code, name, dept, t, u, l, k, akts, sem, ctype, group = row
        course = _get_or_create_course(
            session,
            course_code=code,
            course_name=name,
            department=dept,
            theory_hours=t,
            practice_hours=u,
            lab_hours=l,
            credits=k,
            akts=akts,
            curriculum_semester=sem,
            course_type=ctype,
            elective_group=group,
        )
        code_to_obj[code] = course

    session.flush()
    print(f"  {len(code_to_obj)} ders islendi (insert/update).")

    # ── 2) Onkosullari ekle ──
    prereq_count = 0
    for course_code, prereqs in PREREQUISITES:
        course = code_to_obj.get(course_code)
        if course is None:
            print(f"  UYARI: Ders bulunamadi: {course_code}")
            continue

        for prereq_code, group in prereqs:
            prereq_course = code_to_obj.get(prereq_code)
            if prereq_course is None:
                print(f"  UYARI: Onkosul dersi bulunamadi: {prereq_code}")
                continue

            exists = session.scalar(
                select(CoursePrerequisite).where(
                    CoursePrerequisite.course_id == course.id,
                    CoursePrerequisite.prerequisite_id == prereq_course.id,
                )
            )
            if exists:
                exists.prerequisite_group = group
            else:
                session.add(
                    CoursePrerequisite(
                        course_id=course.id,
                        prerequisite_id=prereq_course.id,
                        prerequisite_group=group,
                    )
                )
                prereq_count += 1

    session.flush()
    print(f"  {prereq_count} yeni onkosul iliskisi eklendi.")


def main() -> None:
    print("Bilgisayar Muhendisligi mufredat verisi yukleniyor...")
    with Session(engine) as session:
        seed_curriculum(session)
        session.commit()
    print("Mufredat verisi basariyla yuklendi.")


if __name__ == "__main__":
    main()
