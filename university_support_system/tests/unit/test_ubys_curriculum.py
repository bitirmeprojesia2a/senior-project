from __future__ import annotations

from src.db.ubys_curriculum import (
    build_curriculum_payload,
    dump_payload,
    find_program_record,
    infer_department_name,
    normalize_course_code_key,
    parse_prerequisites_from_course_detail,
)


def test_find_program_record_extracts_curriculum_identifiers() -> None:
    record = find_program_record(
        [
            {
                "EncryptedAcademicProgramId": "abc",
                "AcademicProgramId": 2723,
                "CurriculumId": 4186,
                "EncryptedCurriculumId": "cur-1",
                "FullAcademicProgramName": "Muhendislik Fakultesi - Elektrik-Elektronik Muhendisligi",
                "EducationQualificatinDegree": 10602,
            }
        ],
        "abc",
    )

    assert record.academic_program_id == 2723
    assert record.curriculum_id == 4186
    assert record.encrypted_curriculum_id == "cur-1"


def test_infer_department_name_uses_last_program_segment() -> None:
    assert (
        infer_department_name(
            "Muhendislik Fakultesi Dekanligi - Elektrik-Elektronik Muhendisligi Bolumu / Elektrik-Elektronik Muhendisligi"
        )
        == "Elektrik-Elektronik Muhendisligi"
    )


def test_build_curriculum_payload_includes_required_and_elective_courses() -> None:
    payload, lookup = build_curriculum_payload(
        {
            "CurriculumDetails": [
                {
                    "CurriculumCources": [
                        {
                            "SemesterNo": 1,
                            "Course": {
                                "Code": "EEM105",
                                "Name": "Elektrik Muhendisligine Giris",
                                "EncryptedId": "eem105",
                                "TheoreticalCredit": 3,
                                "PractiseCredit": 0,
                                "LaboratoryCredit": 2,
                                "Credit": 4,
                                "Ects": 5,
                                "CourseType": 12301,
                            },
                            "ElectivePool": None,
                        },
                        {
                            "SemesterNo": 5,
                            "Course": None,
                            "ElectivePool": {
                                "Code": "EEM-SEC-1",
                                "Name": "Sosyal Secmeli Ders I (Grup)",
                                "ElectivePoolType": 15902,
                                "Credit": 2,
                                "Ects": 2,
                                "ElectivePoolCourses": [
                                    {
                                        "Code": "EEM431",
                                        "Name": "Guc Elektronigi",
                                        "EncryptedId": "eem431",
                                        "TheoreticalCredit": 3,
                                        "PractiseCredit": 0,
                                        "LaboratoryCredit": 0,
                                        "Credit": 3,
                                        "Ects": 5,
                                    }
                                ],
                            },
                        },
                    ]
                }
            ]
        },
        department_name="Elektrik-Elektronik Muhendisligi",
    )

    assert len(payload["courses"]) == 2
    assert payload["courses"][0]["course_code"] == "EEM105"
    assert payload["courses"][1]["course_type"] == "sosyal_secmeli"
    assert payload["courses"][1]["elective_group"] == "EEM-SEC-1"
    assert payload["program_slots"] == [
        {
            "slot_code": "EEM-SS-5-EEMSEC",
            "slot_name": "Sosyal Secmeli Ders I (Grup)",
            "department": "Elektrik-Elektronik Muhendisligi",
            "credits": 2,
            "akts": 2,
            "curriculum_semester": 5,
            "course_type": "secmeli_grup",
            "elective_group": "EEM-SEC-1",
        }
    ]
    assert lookup["EEM431"]["is_elective"] is True


def test_parse_prerequisites_from_course_detail_reads_table_rows() -> None:
    html = """
    <div class="col-md-6">Ön / Yan Koşullar</div>
    <table>
      <tbody>
        <tr>
          <td>EEM217</td>
          <td>Devre Kurami</td>
          <td>Ön Koşul</td>
          <td>3</td>
        </tr>
        <tr>
          <td>MAT103</td>
          <td>Matematik</td>
          <td>Yan Koşul</td>
          <td>4</td>
        </tr>
      </tbody>
    </table>
    """

    prerequisites = parse_prerequisites_from_course_detail(html)

    assert prerequisites == [
        {"course_code": "EEM217", "course_name": "Devre Kurami", "group": 1}
    ]


def test_parse_prerequisites_from_course_detail_falls_back_to_summary() -> None:
    html = """
    <tr>
      <th class="td-baslik">Ön Koşullar</th>
      <td>:</td>
      <td>EEM217 ve MAT103</td>
    </tr>
    """

    prerequisites = parse_prerequisites_from_course_detail(html)

    assert prerequisites == [
        {"course_code": "EEM217", "course_name": None, "group": 1},
        {"course_code": "MAT103", "course_name": None, "group": 1},
    ]


def test_dump_payload_serializes_prerequisite_attempt_metadata() -> None:
    text = dump_payload(
        {
            "department": "Test",
            "courses": [],
            "program_slots": [],
            "prerequisites": [],
            "prerequisite_attempted_courses": ["AAA101"],
            "prerequisite_failed_courses": ["AAA201"],
        }
    )

    assert '"prerequisite_attempted_courses"' in text
    assert '"prerequisite_failed_courses"' in text


def test_normalize_course_code_key_handles_turkish_and_mojibake_variants() -> None:
    assert normalize_course_code_key("İST268") == "IST268"
    assert normalize_course_code_key("IST268") == "IST268"
    assert normalize_course_code_key("Ä°ST268") == "IST268"
