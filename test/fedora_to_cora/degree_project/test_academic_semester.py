import xml.etree.ElementTree as ET
from fedora_to_cora.degree_project.create_academic_semester import (
    create_academic_semester,
)
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_academic_semester():
    source_record = ET.fromstring(
        """
        <publication>
            <academicTerm>
                <year>2022</year>
                <term>HT</term>
            </academicTerm>
        </publication>
        """
    )
    semester = create_academic_semester(source_record)

    assert_equal_for_xml_and_xml_string(
        semester,
        """
        <academicSemester>
            <year>2022</year>
            <academicSemester>ht</academicSemester>
        </academicSemester>
        """,
    )


def test_academic_semester_is_empty():
    source_record = ET.fromstring(
        """
        <publication>
            <academicTerm>
            </academicTerm>
        </publication>
        """
    )
    semester = create_academic_semester(source_record)

    assert_equal_for_xml_and_xml_string(
        semester,
        """
        <academicSemester>
        </academicSemester>
        """,
    )


def test_academic_semester_with_year_is_empty():
    source_record = ET.fromstring(
        """
        <publication>
            <academicTerm>
                <year></year>
            </academicTerm>
        </publication>
        """
    )
    semester = create_academic_semester(source_record)

    assert_equal_for_xml_and_xml_string(
        semester,
        """
        <academicSemester>
        </academicSemester>
        """,
    )
