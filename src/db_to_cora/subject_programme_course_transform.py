import xml.etree.ElementTree as ET
from common.xml_utils import create_group
from common.record_info_create import record_info_create
from common.common_data import create_end_date
from common.xml_validate import XMLSpec, validate_xml


allowed_children: XMLSpec = {
    "domain": "$ANY_TEXT$",
    "old_id": "$ANY_TEXT$",
    "end_date": "$ANY_TEXT$",
    "name_swe": "$ANY_TEXT$",
    "name_eng": "$ANY_TEXT$",
    "broader_id": "$ANY_TEXT$",
    "parent_subject_id": "$ANY_TEXT$",
    "earlier_id": "$ANY_TEXT$",
}


def transform_subject(source_record: ET.Element) -> ET.Element:
    """
    Create a Cora subject element from a DB export subject.
    """
    validate_xml(source_record, allowed_children)
    return _create_element_with_common_children(source_record, "subject")


def transform_programme(source_record: ET.Element) -> ET.Element:
    """
    Create a Cora programme element from a DB export subject.
    """
    validate_xml(source_record, allowed_children)
    return _create_element_with_common_children(source_record, "programme")


def transform_course(source_record: ET.Element) -> ET.Element:
    """
    Create a Cora course element from a DB export subject.
    """
    validate_xml(source_record, allowed_children)
    return _create_element_with_common_children(source_record, "course")


def _create_record_info(source_record: ET.Element, type: str) -> ET.Element:
    source_old_id = source_record.find(f"./old_id")
    assert (
        source_old_id is not None and source_old_id.text is not None
    ), "old_id is missing in source record"

    return record_info_create(
        validation_type_id=f"diva-{type}",
        old_id=source_old_id.text,
        permission_unit_id=source_record.findtext("./domain"),
    )


def _create_element_with_common_children(
    source_record: ET.Element, name_in_data: str
) -> ET.Element:
    """
    Create an XML element with common children (_create_record_info, _create_authority,
    _create_variant, _create_end_date).
    """
    element = create_group(
        name_in_data,
        children=[
            _create_record_info(source_record, name_in_data),
            _create_authority_swe(source_record),
            _create_authority_eng(source_record),
            _create_end_date(source_record),
        ],
    )
    assert element is not None
    return element


def _create_end_date(source_record: ET.Element) -> ET.Element | None:
    end_date = source_record.findtext(f"./end_date")
    if end_date:
        return create_end_date(end_date)


def _create_authority_swe(source_record: ET.Element) -> ET.Element | None:
    name = source_record.findtext(f"./name_swe")
    if name:
        authority = ET.Element("authority", lang="swe", repeatId="swe")
        authority.append(_create_topic(name))
        return authority


def _create_authority_eng(source_record: ET.Element) -> ET.Element | None:
    name = source_record.findtext(f"./name_eng")
    if name:
        variant = ET.Element("authority", lang="eng", repeatId="eng")
        variant.append(_create_topic(name))
        return variant


def _create_topic(name: str) -> ET.Element:
    topic = ET.Element("topic")
    topic.text = name
    return topic
