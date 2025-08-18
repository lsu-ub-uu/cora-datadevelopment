import xml.etree.ElementTree as ET
from cora.context import MockContext
from fedora_to_cora.transform.degree_project.create_student_degree import (
    create_student_degrees,
)
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext


def test_create_student_degree_thesis_level():
    source_record = ET.fromstring(
        """
      <publication>
            <studentDegrees>
                <studentDegree>
                    <thesisLevel>
                        <thesisLevelCode>H2</thesisLevelCode>
                    </thesisLevel>
                </studentDegree>
            </studentDegrees>
        </publication>
    """
    )

    student_degrees = create_student_degrees(source_record, MockContext())

    assert len(student_degrees) == 1
    assert_equal_for_xml_and_xml_string(
        student_degrees[0],
        """
        <studentDegree repeatId="0">
            <degreeLevel>H2</degreeLevel>
        </studentDegree>""",
    )


def test_create_student_degree_hp():
    source_record = ET.fromstring(
        """
      <publication>
            <studentDegrees>
                <studentDegree>
                    <universityPoints>
                        <hp>20</hp>
                    </universityPoints>
                </studentDegree>
            </studentDegrees>
        </publication>
    """
    )

    student_degrees = create_student_degrees(source_record, MockContext())

    assert len(student_degrees) == 1
    assert_equal_for_xml_and_xml_string(
        student_degrees[0],
        """
        <studentDegree repeatId="0">
            <universityPoints>20</universityPoints>
        </studentDegree>""",
    )


def test_create_linked_course(monkeypatch):
    old_id = "123"
    cora_id = "cora-course:12345678901234567"

    def mock_get_cora_id_by_old_id(old_id, *args, **kwargs):
        if old_id == "123":
            return "cora-course:12345678901234567"
        return None

    monkeypatch.setattr(
        "fedora_to_cora.transform.degree_project.create_student_degree.get_cora_id_by_old_id",
        mock_get_cora_id_by_old_id,
    )

    source_record = ET.fromstring(
        f"""
        <publication>
            <studentDegrees>
                <studentDegree>
                    <undergraduateSubject>
                        <subjectId>{old_id}</subjectId>
                    </undergraduateSubject>
                </studentDegree>
            </studentDegrees>
        </publication>
    """
    )

    student_degrees = create_student_degrees(source_record, MockContext())
    assert len(student_degrees) == 1
    assert_equal_for_xml_and_xml_string(
        student_degrees[0],
        f"""
        <studentDegree repeatId="0">
            <course>
                <linkedRecordType>diva-course</linkedRecordType>
                <linkedRecordId>{cora_id}</linkedRecordId>
            </course>
        </studentDegree>""",
    )
