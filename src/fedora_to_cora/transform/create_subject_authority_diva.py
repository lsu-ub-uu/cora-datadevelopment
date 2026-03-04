import xml.etree.ElementTree as ET
from cora.context import Context
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link
from common.xml_utils import append_if_value, create_group

DIVA_SUBJECT_RECORD_TYPE = "diva-subject"


def create_subject_authority_diva(
    source_record: ET.Element, context: Context
) -> ET.Element | None:
    """
    Create a subject element with authority "diva" based on the source record.
    """
    return create_group(
        "subject",
        authority="diva",
        children=[
            _create_topic(topic.text, i, context)
            for i, topic in enumerate(
                source_record.findall("./researchSubjects/subject/subjectId")
            )
            if topic.text
        ],
    )


def _create_topic(subject_id: str, repeat_id: int, context: Context) -> ET.Element:
    cora_id = get_cora_id_by_old_id(
        subject_id, record_type=DIVA_SUBJECT_RECORD_TYPE, context=context
    )

    topic = create_record_link(
        name_in_data="topic", record_type=DIVA_SUBJECT_RECORD_TYPE, record_id=cora_id
    )
    topic.set("repeatId", str(repeat_id))

    return topic
