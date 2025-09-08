import xml.etree.ElementTree as ET
from common.xml_utils import append_if_value, assert_no_unknown_elements
from common.record_info_create import record_info_create
from common.common_data import create_end_date


nameInData = "subject"
permissionUnit = "varldskulturmuseerna"
allowed_children = {
    "domain",
    "old_id",
    "end_date",
    "name_swe",
    "name_eng",
    "broader_id",
    "parent_subject_id",
    "earlier_id",
}


def transform_subject(source_record: ET.Element) -> ET.Element:
    """
    Create a Cora subject element from a DB export subject.
    """
    assert_no_unknown_elements(source_record, allowed_children)

    subject = ET.Element(nameInData)

    subject.append(_create_record_info(source_record))
    append_if_value(subject, _create_authority(source_record))
    append_if_value(subject, _create_variant(source_record))
    append_if_value(subject, _create_end_date(source_record))

    return subject


def _create_record_info(source_record: ET.Element) -> ET.Element:
    source_old_id = source_record.find(f"./old_id")
    assert (
        source_old_id is not None and source_old_id.text is not None
    ), "old_id is missing in source record"

    return record_info_create(
        validation_type_id="diva-subject",
        old_id=source_old_id.text,
        permission_unit_id=permissionUnit,
    )


def _create_end_date(source_record: ET.Element) -> ET.Element | None:
    end_date = source_record.find(f"./end_date")
    if end_date is not None and end_date.text:
        return create_end_date(end_date.text)


def _create_authority(source_record: ET.Element) -> ET.Element | None:
    name = source_record.findtext(f"./name_swe")
    if name:
        authority = ET.Element("authority", lang="swe")
        authority.append(_create_topic(name))
        return authority


def _create_variant(source_record: ET.Element) -> ET.Element | None:
    name = source_record.findtext(f"./name_eng")
    if name:
        variant = ET.Element("variant", lang="eng")
        variant.append(_create_topic(name))
        return variant


def _create_topic(name: str) -> ET.Element:
    topic = ET.Element("topic")
    topic.text = name
    return topic
