from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import json
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.console import configure_utf8_stdio
from src.core.config import settings
from src.core.text_normalization import collapse_whitespace, normalize_text
from src.db.models import (
    Announcement,
    AvailableScholarship,
    Course,
    CourseRegistrationPeriod,
    Installment,
    OfficeContact,
    Payment,
    Scholarship,
    ScholarshipApplication,
    Student,
    StudentCourse,
    Tuition,
    TuitionFeeCatalog,
)

configure_utf8_stdio()


engine = create_engine(settings.postgres.sync_url, future=True)

_REGISTRATION_PERIODS_FILE = ROOT_DIR / "data" / "metadata" / "registration_periods.json"
_TUITION_FEE_CATALOG_FILE = ROOT_DIR / "data" / "metadata" / "tuition_fee_catalog.json"


_REGISTRATION_PERIOD_FIXTURES = (
    {
        "semester": "2025-Güz",
        "start_date": datetime(2025, 8, 26, tzinfo=timezone.utc),
        "end_date": datetime(2025, 9, 6, tzinfo=timezone.utc),
        "is_active": False,
    },
    {
        "semester": "2026-Bahar",
        "start_date": datetime(2026, 2, 10, tzinfo=timezone.utc),
        "end_date": datetime(2026, 2, 21, tzinfo=timezone.utc),
        "is_active": True,
    },
)


def _seed_demo_announcements(session: Session) -> None:
    """Sync a small set of demo announcements for end-to-end queries."""

    now = datetime.now(timezone.utc)
    fixtures = [
        {
            "title": "2026 Bahar Ders Kayit Takvimi Guncellendi",
            "summary": "Bahar donemi ders kayit ve mazeretli kayit tarihleri guncellenmistir. Ogrencilerin takvimi kontrol etmesi gerekir.",
            "original_text": "Bahar donemi ders kayit, ders ekle-birak ve mazeretli kayit tarihleri guncellenmistir.",
            "source_url": "https://omu.edu.tr/duyuru/2026-bahar-ders-kayit-takvimi",
            "faculty": None,
            "department": "student_affairs",
            "published_at": now - timedelta(days=2),
            "is_active": True,
        },
        {
            "title": "CAP Basvurulari Acildi",
            "summary": "Bilgisayar Muhendisligi dahil uygun programlar icin CAP basvurulari 15 Nisan 2026 tarihine kadar alinacaktir.",
            "original_text": "CAP basvurulari 15 Nisan 2026 tarihine kadar ogrenci bilgi sistemi uzerinden alinacaktir.",
            "source_url": "https://omu.edu.tr/duyuru/cap-basvurulari-2026",
            "faculty": "Muhendislik Fakultesi",
            "department": "academic_programs",
            "published_at": now - timedelta(days=1),
            "is_active": True,
        },
        {
            "title": "Yemek Bursu Basvurulari Basladi",
            "summary": "Yemek bursu ve kismi zamanli calisma basvurulari 20 Nisan 2026 tarihine kadar aciktir.",
            "original_text": "Yemek bursu ile kismi zamanli ogrenci calisma programi basvurulari baslamistir.",
            "source_url": "https://omu.edu.tr/duyuru/yemek-bursu-basvurulari-2026",
            "faculty": None,
            "department": "finance",
            "published_at": now - timedelta(days=3),
            "is_active": True,
        },
    ]

    existing = {
        item.source_url: item
        for item in session.scalars(select(Announcement).where(Announcement.source_url.is_not(None))).all()
    }

    for fixture in fixtures:
        row = existing.get(fixture["source_url"])
        if row is None:
            session.add(Announcement(**fixture))
            continue

        row.title = fixture["title"]
        row.summary = fixture["summary"]
        row.original_text = fixture["original_text"]
        row.faculty = fixture["faculty"]
        row.department = fixture["department"]
        row.published_at = fixture["published_at"]
        row.is_active = fixture["is_active"]


def _seed_demo_office_contacts(session: Session) -> None:
    """Sync a small set of office contacts for contact-request flows."""

    fixtures = [
        {
            "unit_name": "Program Isleri Ofisi",
            "department": "academic_programs",
            "person_name": "Ayse Kaya",
            "title": "Uzman",
            "phone_ext": "7304",
            "email": "program.isleri@omu.edu.tr",
            "related_agents": ["curriculum_agent"],
            "is_active": True,
        },
        {
            "unit_name": "Ogrenci Isleri Kayit Ofisi",
            "department": "student_affairs",
            "person_name": "Mehmet Demir",
            "title": "Memur",
            "phone_ext": "7401",
            "email": "kayit.ofisi@omu.edu.tr",
            "related_agents": ["registration_agent", "graduation_agent"],
            "is_active": True,
        },
        {
            "unit_name": "Mali Isler Ofisi",
            "department": "finance",
            "person_name": "Elif Yilmaz",
            "title": "Uzman",
            "phone_ext": "7412",
            "email": "mali.isler@omu.edu.tr",
            "related_agents": ["tuition_agent", "scholarship_agent"],
            "is_active": True,
        },
    ]

    existing = {
        (item.unit_name, item.department): item
        for item in session.scalars(select(OfficeContact)).all()
    }

    for fixture in fixtures:
        key = (fixture["unit_name"], fixture["department"])
        row = existing.get(key)
        if row is None:
            session.add(OfficeContact(**fixture))
            continue

        row.person_name = fixture["person_name"]
        row.title = fixture["title"]
        row.phone_ext = fixture["phone_ext"]
        row.email = fixture["email"]
        row.related_agents = fixture["related_agents"]
        row.is_active = fixture["is_active"]


def _sync_registration_periods(session: Session) -> None:
    """Kayit donemi verilerini her calistirmada guncel tutar."""

    if not _REGISTRATION_PERIODS_FILE.exists():
        return

    payload = json.loads(_REGISTRATION_PERIODS_FILE.read_text(encoding="utf-8"))
    fixtures = [
        {
            "semester": item["semester"],
            "start_date": datetime.fromisoformat(item["start_date"]),
            "end_date": datetime.fromisoformat(item["end_date"]),
            "is_active": bool(item.get("is_active", False)),
        }
        for item in payload
    ]

    existing = {
        period.semester: period
        for period in session.scalars(select(CourseRegistrationPeriod)).all()
    }
    expected_semesters = {fixture["semester"] for fixture in fixtures}

    for fixture in fixtures:
        period = existing.get(fixture["semester"])
        if period is None:
            session.add(CourseRegistrationPeriod(**fixture))
            continue

        period.start_date = fixture["start_date"]
        period.end_date = fixture["end_date"]
        period.is_active = fixture["is_active"]

    for semester, period in existing.items():
        if semester not in expected_semesters:
            session.delete(period)


def _normalize_unit_name(value: str | None) -> str:
    normalized = normalize_text(collapse_whitespace(value))
    replacements = {
        "fak.": "fakultesi",
        "fak ": "fakultesi ",
        "meslekyuksekokulu": "meslek yuksekokulu",
        "yuksek okulu": "yuksekokulu",
    }
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    return " ".join(normalized.split())


def _sync_tuition_fee_catalog(session: Session) -> None:
    """Ogrenim ucreti tablosunu JSON kaynaktan senkronize eder."""

    if not _TUITION_FEE_CATALOG_FILE.exists():
        return

    payload = json.loads(_TUITION_FEE_CATALOG_FILE.read_text(encoding="utf-8"))
    fixtures = []
    for item in payload:
        fixtures.append(
            {
                "academic_year": item["academic_year"],
                "student_type": normalize_text(item["student_type"]),
                "unit_name": item["unit_name"],
                "normalized_unit_name": _normalize_unit_name(item["unit_name"]),
                "annual_amount": float(item["annual_amount"]),
                "semester_amount": (
                    float(item["semester_amount"])
                    if item.get("semester_amount") is not None
                    else None
                ),
                "currency": item.get("currency", "TRY"),
                "source_document": item.get("source_document"),
                "notes": item.get("notes"),
                "is_active": bool(item.get("is_active", True)),
            }
        )

    existing = {
        (entry.academic_year, entry.student_type, entry.normalized_unit_name): entry
        for entry in session.scalars(select(TuitionFeeCatalog)).all()
    }
    expected_keys = {
        (fixture["academic_year"], fixture["student_type"], fixture["normalized_unit_name"])
        for fixture in fixtures
    }

    for fixture in fixtures:
        key = (fixture["academic_year"], fixture["student_type"], fixture["normalized_unit_name"])
        row = existing.get(key)
        if row is None:
            session.add(TuitionFeeCatalog(**fixture))
            continue

        row.unit_name = fixture["unit_name"]
        row.annual_amount = fixture["annual_amount"]
        row.semester_amount = fixture["semester_amount"]
        row.currency = fixture["currency"]
        row.source_document = fixture["source_document"]
        row.notes = fixture["notes"]
        row.is_active = fixture["is_active"]

    for key, row in existing.items():
        if key not in expected_keys:
            session.delete(row)


def seed_synthetic_data(session: Session) -> None:
    """Insert synthetic, student-focused test data when student tables are empty."""

    _sync_registration_periods(session)
    _sync_tuition_fee_catalog(session)
    _seed_demo_announcements(session)
    _seed_demo_office_contacts(session)

    has_any_student = session.scalar(select(Student.id).limit(1)) is not None

    if has_any_student:
        session.commit()
        print("Support data synced. Synthetic student seed skipped: students already contain data.")
        return

    # ---------- 1) STUDENTS ----------
    students = [
        # Eğitim Fakültesi
        Student(
            student_id="20210001",
            full_name="Ayşe Korkmaz",
            email="20210001@edu.univ.tr",
            department="Sınıf Öğretmenliği",
            faculty="Eğitim Fakültesi",
            class_year=3,
            enrollment_year=2021,
            registration_status="active",
            gpa=3.10,
            total_credits=150,
            completed_credits=90,
            current_semester="2026-Bahar",
        ),
        Student(
            student_id="20220015",
            full_name="Mehmet Çetin",
            email="20220015@edu.univ.tr",
            department="Rehberlik ve Psikolojik Danışmanlık",
            faculty="Eğitim Fakültesi",
            class_year=2,
            enrollment_year=2022,
            registration_status="active",
            gpa=2.45,
            total_credits=150,
            completed_credits=50,
            current_semester="2026-Bahar",
        ),
        Student(
            student_id="20190007",
            full_name="Elif Tanrıverdi",
            email="20190007@edu.univ.tr",
            department="Okul Öncesi Öğretmenliği",
            faculty="Eğitim Fakültesi",
            class_year=4,
            enrollment_year=2019,
            registration_status="graduated",
            gpa=3.45,
            total_credits=150,
            completed_credits=150,
            current_semester="2025-Güz",
        ),
        # Fen-Edebiyat Fakültesi
        Student(
            student_id="20210045",
            full_name="Can Yıldız",
            email="20210045@fen.univ.tr",
            department="Matematik",
            faculty="Fen-Edebiyat Fakültesi",
            class_year=3,
            enrollment_year=2021,
            registration_status="active",
            gpa=2.80,
            total_credits=180,
            completed_credits=110,
            current_semester="2026-Bahar",
        ),
        Student(
            student_id="20230011",
            full_name="Zeynep Aksoy",
            email="20230011@fen.univ.tr",
            department="İngiliz Dili ve Edebiyatı",
            faculty="Fen-Edebiyat Fakültesi",
            class_year=1,
            enrollment_year=2023,
            registration_status="active",
            gpa=None,
            total_credits=180,
            completed_credits=0,
            current_semester="2026-Bahar",
        ),
        Student(
            student_id="20200003",
            full_name="Burak Demir",
            email="20200003@fen.univ.tr",
            department="Tarih",
            faculty="Fen-Edebiyat Fakültesi",
            class_year=4,
            enrollment_year=2020,
            registration_status="frozen",
            gpa=1.95,
            total_credits=180,
            completed_credits=120,
            current_semester="2025-Güz",
        ),
        # Mühendislik Fakültesi
        Student(
            student_id="20210090",
            full_name="Tuba Sarıkaya",
            email="20210090@eng.univ.tr",
            department="Bilgisayar Mühendisliği",
            faculty="Mühendislik Fakültesi",
            class_year=4,
            enrollment_year=2021,
            registration_status="active",
            gpa=3.30,
            total_credits=240,
            completed_credits=190,
            current_semester="2026-Bahar",
        ),
        Student(
            student_id="20220032",
            full_name="Emre Koç",
            email="20220032@eng.univ.tr",
            department="Elektrik-Elektronik Mühendisliği",
            faculty="Mühendislik Fakültesi",
            class_year=3,
            enrollment_year=2022,
            registration_status="active",
            gpa=2.20,
            total_credits=240,
            completed_credits=80,
            current_semester="2026-Bahar",
        ),
        Student(
            student_id="20190022",
            full_name="Melis Şahin",
            email="20190022@eng.univ.tr",
            department="Endüstri Mühendisliği",
            faculty="Mühendislik Fakültesi",
            class_year=5,
            enrollment_year=2019,
            registration_status="leave_of_absence",
            gpa=2.90,
            total_credits=240,
            completed_credits=160,
            current_semester="2025-Güz",
        ),
    ]
    session.add_all(students)
    session.flush()

    students_by_code = {s.student_id: s for s in students}

    # ---------- 2) COURSES ----------
    courses = [
        # Eğitim
        Course(
            course_code="EGT101",
            course_name="Eğitime Giriş",
            credits=3,
            department="Sınıf Öğretmenliği",
            semester="1",
            instructor="Doç. Dr. Ayla Yılmaz",
        ),
        Course(
            course_code="EGT305",
            course_name="Sınıf Yönetimi",
            credits=4,
            department="Sınıf Öğretmenliği",
            semester="5",
            instructor="Dr. Öğr. Üyesi Ali Kaya",
        ),
        Course(
            course_code="RPD204",
            course_name="Psikolojik Danışma Kuramları",
            credits=4,
            department="Rehberlik ve Psikolojik Danışmanlık",
            semester="4",
            instructor="Prof. Dr. Sevim Er",
        ),
        # Fen-Edebiyat
        Course(
            course_code="MAT201",
            course_name="Lineer Cebir",
            credits=4,
            department="Matematik",
            semester="3",
            instructor="Doç. Dr. Selim Çetin",
        ),
        Course(
            course_code="MAT301",
            course_name="Olasılık ve İstatistik",
            credits=4,
            department="Matematik",
            semester="5",
            instructor="Dr. Öğr. Üyesi Funda Öz",
        ),
        Course(
            course_code="ING201",
            course_name="19. Yüzyıl İngiliz Edebiyatı",
            credits=3,
            department="İngiliz Dili ve Edebiyatı",
            semester="3",
            instructor="Dr. Öğr. Üyesi John Smith",
        ),
        # Muhendislik dersleri artik seed_curriculum_data.py ile yukleniyor.
        # Burada sadece diger fakultelerin sentetik dersleri kaliyor.
    ]
    session.add_all(courses)
    session.flush()
    courses_by_code = {c.course_code: c for c in courses}

    # ---------- 3) STUDENT–COURSE ENROLLMENTS ----------
    # Tuba icin gercek Bil. Muh. derslerini cek (seed_curriculum_data ile yuklenmis olmali)
    bil_courses: dict[str, Course] = {}
    for code in ("BIL101", "BIL103", "BIL104", "BIL108", "BIL123", "BIL203",
                 "BIL215", "BIL204", "BIL212", "BIL305", "BIL309", "BIL313",
                 "TBMAT111", "TBMAT112", "TBFIZ121", "TBFIZ122"):
        c = session.scalar(select(Course).where(Course.course_code == code))
        if c is not None:
            bil_courses[code] = c

    enrollments = [
        # Ayse – one completed, one current course
        StudentCourse(
            student_id=students_by_code["20210001"].id,
            course_id=courses_by_code["EGT101"].id,
            semester="2023-Guz",
            grade="AA",
            status="completed",
        ),
        StudentCourse(
            student_id=students_by_code["20210001"].id,
            course_id=courses_by_code["EGT305"].id,
            semester="2026-Bahar",
            grade=None,
            status="enrolled",
        ),
        # Can – one completed, one failed
        StudentCourse(
            student_id=students_by_code["20210045"].id,
            course_id=courses_by_code["MAT201"].id,
            semester="2024-Guz",
            grade="CB",
            status="completed",
        ),
        StudentCourse(
            student_id=students_by_code["20210045"].id,
            course_id=courses_by_code["MAT301"].id,
            semester="2025-Bahar",
            grade="FF",
            status="failed",
        ),
    ]

    # Tuba (Bil. Muh. 4. sinif) - gercek mufredat dersleri
    if bil_courses:
        tuba_id = students_by_code["20210090"].id
        tuba_completed = [
            ("BIL101", "2021-Guz",  "BA"), ("BIL103", "2021-Guz",  "AA"),
            ("TBMAT111","2021-Guz",  "BB"), ("TBFIZ121","2021-Guz",  "CB"),
            ("BIL123",  "2021-Guz",  "BA"), ("BIL108",  "2022-Bahar","BB"),
            ("BIL104",  "2022-Bahar","AA"), ("TBMAT112","2022-Bahar","CB"),
            ("TBFIZ122","2022-Bahar","BB"), ("BIL203",  "2022-Guz",  "BA"),
            ("BIL215",  "2022-Guz",  "BB"), ("BIL204",  "2023-Bahar","BA"),
            ("BIL212",  "2023-Bahar","AA"), ("BIL305",  "2023-Guz",  "BB"),
            ("BIL309",  "2023-Guz",  "BA"), ("BIL313",  "2023-Guz",  "CB"),
        ]
        for code, sem, grade in tuba_completed:
            if code in bil_courses:
                enrollments.append(StudentCourse(
                    student_id=tuba_id,
                    course_id=bil_courses[code].id,
                    semester=sem,
                    grade=grade,
                    status="completed",
                ))

    session.add_all(enrollments)

    # ---------- 4) TUITION, PAYMENTS, INSTALLMENTS ----------
    tuitions = [
        # Tuba – partial debt
        Tuition(
            student_id=students_by_code["20210090"].id,
            semester="2026-Bahar",
            total_amount=15000.00,
            paid_amount=9000.00,
            due_date=date(2026, 3, 31),
            last_payment_date=date(2026, 2, 20),
        ),
        # Ayşe – no debt
        Tuition(
            student_id=students_by_code["20210001"].id,
            semester="2026-Bahar",
            total_amount=12000.00,
            paid_amount=12000.00,
            due_date=date(2026, 3, 31),
            last_payment_date=date(2026, 2, 10),
        ),
        # Can – no payment yet
        Tuition(
            student_id=students_by_code["20210045"].id,
            semester="2026-Bahar",
            total_amount=13000.00,
            paid_amount=0.00,
            due_date=date(2026, 3, 31),
            last_payment_date=None,
        ),
    ]
    session.add_all(tuitions)
    session.flush()
    tuition_by_key = {(t.student_id, t.semester): t for t in tuitions}

    payments = [
        Payment(
            tuition_id=tuition_by_key[
                (students_by_code["20210090"].id, "2026-Bahar")
            ].id,
            amount=6000.00,
            payment_date=date(2026, 2, 1),
            payment_method="credit_card",
            receipt_no="CSE-2026-0001",
        ),
        Payment(
            tuition_id=tuition_by_key[
                (students_by_code["20210090"].id, "2026-Bahar")
            ].id,
            amount=3000.00,
            payment_date=date(2026, 2, 20),
            payment_method="bank_transfer",
            receipt_no="CSE-2026-0017",
        ),
        Payment(
            tuition_id=tuition_by_key[
                (students_by_code["20210001"].id, "2026-Bahar")
            ].id,
            amount=12000.00,
            payment_date=date(2026, 2, 10),
            payment_method="online",
            receipt_no="EDU-2026-0003",
        ),
    ]
    session.add_all(payments)

    installments = [
        # Can – 3-installment plan, first overdue
        Installment(
            tuition_id=tuition_by_key[
                (students_by_code["20210045"].id, "2026-Bahar")
            ].id,
            installment_number=1,
            amount=4333.33,
            due_date=date(2026, 2, 15),
            status="overdue",
        ),
        Installment(
            tuition_id=tuition_by_key[
                (students_by_code["20210045"].id, "2026-Bahar")
            ].id,
            installment_number=2,
            amount=4333.33,
            due_date=date(2026, 3, 15),
            status="pending",
        ),
        Installment(
            tuition_id=tuition_by_key[
                (students_by_code["20210045"].id, "2026-Bahar")
            ].id,
            installment_number=3,
            amount=4333.34,
            due_date=date(2026, 4, 15),
            status="pending",
        ),
    ]
    session.add_all(installments)

    # ---------- 6) SCHOLARSHIPS ----------
    available = [
        AvailableScholarship(
            name="Başarı Bursu",
            description="Yüksek not ortalamasına sahip öğrenciler için başarı bursu.",
            monthly_amount=1500.00,
            min_gpa=3.50,
            deadline=date(2026, 2, 28),
        ),
        AvailableScholarship(
            name="Yemek Desteği",
            description="Gelir durumu düşük öğrenciler için yemek desteği.",
            monthly_amount=800.00,
            min_gpa=None,
            deadline=None,
        ),
    ]
    session.add_all(available)
    session.flush()
    available_by_name = {a.name: a for a in available}

    scholarships = [
        Scholarship(
            student_id=students_by_code["20210001"].id,
            available_scholarship_id=available_by_name["Yemek Desteği"].id,
            monthly_amount=800.00,
            start_date=date(2025, 10, 1),
            end_date=None,
            status="active",
        ),
    ]
    session.add_all(scholarships)

    applications = [
        ScholarshipApplication(
            student_id=students_by_code["20210090"].id,
            available_scholarship_id=available_by_name["Başarı Bursu"].id,
            application_date=date(2026, 2, 5),
            status="pending",
            notes="Dönem sonunda GNO'nun 3.50'nin üzerine çıkması bekleniyor.",
        ),
        ScholarshipApplication(
            student_id=students_by_code["20210045"].id,
            available_scholarship_id=available_by_name["Yemek Desteği"].id,
            application_date=date(2026, 1, 20),
            status="rejected",
            notes="Gelir kriterlerini karşılamıyor.",
        ),
    ]
    session.add_all(applications)

    session.commit()
    print("Synthetic student-focused test data inserted successfully.")


def main() -> None:
    with Session(engine) as session:
        seed_synthetic_data(session)


if __name__ == "__main__":
    main()
