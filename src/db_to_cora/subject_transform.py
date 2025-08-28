import xml.etree.ElementTree as ET
from common.xml_utils import append_if_value
from common.record_info_create import record_info_create
from common.common_data import create_authority_or_variant_lang_with_child_topic
from common.common_data import create_end_date


nameInData = "subject"
permissionUnit = "varldskulturmuseerna"


def transform_subject(source_record: ET.Element) -> ET.Element:
    """
    Create a Cora subject element from a DB export subject.
    """

    subject = ET.Element(nameInData)
    
    subject.append(_create_record_info(source_record))
    subject.append(_create_authority_or_variant_lang(source_record, element_name="authority", language="swe"))
    append_if_value(subject, _create_authority_or_variant_lang(source_record, element_name="variant", language="eng"))
    append_if_value(subject, _create_end_date(source_record))
    
    return subject


def _create_record_info(source_record: ET.Element) -> ET.Element:
    source_old_id = source_record.find(".//old_id")
    assert (
        source_old_id is not None and source_old_id.text is not None
    ), "old_id is missing in source record"

    return record_info_create(
        validation_type_id="diva-subject",
        old_id=source_old_id.text,
        permission_unit_id=permissionUnit,
    )
    
def _create_authority_or_variant_lang(source_record: ET.Element, element_name: str, language: str) -> ET.Element | None:
    name_lang = source_record.find(f".//name_{language}")
    if name_lang is not None and name_lang.text:
        return create_authority_or_variant_lang_with_child_topic(
            name_lang.text, element_name, language
            )
        
def _create_end_date(source_record: ET.Element)-> ET.Element | None:
    end_date = source_record.find(".//end_date")
    if end_date is not None and end_date.text:
        return create_end_date(
            end_date.text
            )
