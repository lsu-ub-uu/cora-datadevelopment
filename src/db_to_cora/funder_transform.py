import xml.etree.ElementTree as ET
from common.record_info_create import record_info_create
from common.create_authority_or_variant_lang import create_authority_or_variant_lang_using_name_type_corporate

nameInData = "funder"


def transform_funder(source_record: ET.Element) -> ET.Element:
    """
    Create a Cora funder element from a DB export funder.
    """

    funder = ET.Element(nameInData)

    funder.append(_create_record_info(source_record))
    funder.append(_create_authority_or_variant_lang(source_record, element_name="authority", language="swe"))
    variant_lang = _create_authority_or_variant_lang(source_record, element_name="variant", language="eng")
    if variant_lang is not None:
        funder.append(variant_lang)
        
    return funder


def _create_record_info(source_record: ET.Element) -> ET.Element:
    source_old_id = source_record.find(".//old_id")
    assert (
        source_old_id is not None and source_old_id.text is not None
    ), "old_id is missing in source record"

    return record_info_create(
        validation_type_id="diva-funder",
        old_id=source_old_id.text,
        permission_unit_id=None,
    )


def _create_authority_or_variant_lang(source_record: ET.Element, element_name: str, language: str) -> ET.Element | None:
    name_lang = source_record.find(f".//name_{language}")
    if name_lang is not None and name_lang.text:
#    if (name_eng is None):
#        return None
        return create_authority_or_variant_lang_using_name_type_corporate(name_lang.text, element_name, language)


def _create_identifiers(source_record: ET.Element, identifierType: str) -> ET.Element | None:
    identifier = source_record.find(f".//identifier_{identifierType}")
    print(identifier)
    



