import xml.etree.ElementTree as ET
from cora.context import Context
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link
from common.xml_utils import append_if_value, create_group

DIVA_SUBJECT_RECORD_TYPE = "diva-subject"


def create_subject_authority_diva(
    source_record: ET.Element, context: Context
) -> list[ET.Element] | None:
    """
    Create subject elements with authority "diva" based on the source record.

    Each subject contains exactly one topic and has a unique repeatId.
    """
    subjects = [
        _create_subject(topic.text, i, context)
        for i, topic in enumerate(
            source_record.findall("./researchSubjects/subject/subjectId")
        )
        if topic.text
    ]

    return subjects if subjects else None


def _create_subject(subject_id: str, repeat_id: int, context: Context) -> ET.Element:
    cora_id = get_cora_id_by_old_id(
        subject_id, record_type=DIVA_SUBJECT_RECORD_TYPE, context=context
    )

    topic = create_record_link(
        name_in_data="topic", record_type=DIVA_SUBJECT_RECORD_TYPE, record_id=cora_id
    )
    assert topic is not None
    subject = create_group(
        "subject",
        authority="diva",
        repeatId=str(repeat_id),
        children=[topic],
    )
    assert subject is not None

    return subject
