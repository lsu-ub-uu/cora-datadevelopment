import xml.etree.ElementTree as ET
from fedora_to_cora.transform.create_subject_authority_diva import (
    create_subject_authority_diva,
)
from common.test_helper import (
    assert_equal_for_xml_and_xml_string,
)
from cora.context import MockContext


def test_create_subject_authority_diva(monkeypatch):
    subject_1_old_id = "985"
    subject_1_cora_id = "diva-subject:21861441014837120"

    subject_2_old_id = "1234"
    subject_2_cora_id = "diva-subject:30224"

    mock_context = MockContext()

    def mock_get_id(old_id, *args, **kwargs):
        if old_id == subject_1_old_id:
            return subject_1_cora_id
        elif old_id == subject_2_old_id:
            return subject_2_cora_id
        else:
            return None

    monkeypatch.setattr(
        "fedora_to_cora.transform.create_subject_authority_diva.get_cora_id_by_old_id",
        mock_get_id,
    )

    source_record = ET.fromstring(f"""
        <publication>
            <researchSubjects>
                <subject>
                    <subjectId>{subject_1_old_id}</subjectId>
                </subject>
                <subject>
                    <subjectId>{subject_2_old_id}</subjectId>
                </subject>
            </researchSubjects>
        </publication>
        """)

    subjects = create_subject_authority_diva(source_record, mock_context)
    assert subjects is not None
    assert len(subjects) == 2

    assert_equal_for_xml_and_xml_string(
        subjects[0],
        f"""
        <subject authority="diva" repeatId="0">
            <topic>
                <linkedRecordType>diva-subject</linkedRecordType>
                <linkedRecordId>{subject_1_cora_id}</linkedRecordId>
            </topic>
        </subject>
        """,
    )

    assert_equal_for_xml_and_xml_string(
        subjects[1],
        f"""
        <subject authority="diva" repeatId="1">
            <topic>
                <linkedRecordType>diva-subject</linkedRecordType>
                <linkedRecordId>{subject_2_cora_id}</linkedRecordId>
            </topic>
        </subject>
        """,
    )
