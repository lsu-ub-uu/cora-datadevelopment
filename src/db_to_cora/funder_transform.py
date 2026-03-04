import xml.etree.ElementTree as ET
from common.xml_utils import append_if_value, create_group
from common.xml_validate import XMLSpec, validate_xml
from common.record_info_create import record_info_create
from common.common_data import (
    name_type_corporate_create,
)
from common.common_data import create_end_date
from common.common_data import create_identifiers_from_source


nameInData = "funder"

allowed_children: XMLSpec = {
    "old_id": "$ANY_TEXT$",
    "name_swe": "$ANY_TEXT$",
    "name_eng": "$ANY_TEXT$",
    "end_date": "$ANY_TEXT$",
    "identifier_organisationNumber": "$ANY_TEXT$",
    "identifier_doi": "$ANY_TEXT$",
    "locale_swe": "$ANY_TEXT$",
    "locale_eng": "$ANY_TEXT$",
    "funder_name_id": "$ANY_TEXT$",
}


def transform_funder(source_record: ET.Element) -> ET.Element:
    """
    Create a Cora funder element from a DB export funder.
    """
    validate_xml(source_record, allowed_children)

    funder = create_group(
        "funder",
        children=[
            _create_record_info(source_record),
            _create_authority_swe(source_record),
            _create_authority_eng(source_record),
            _create_end_date(source_record),
            _create_identifiers_from_source(source_record, identifier_type="doi"),
            _create_identifiers_from_source(
                source_record, identifier_type="organisationNumber"
            ),
        ],
    )
    assert funder is not None
    return funder


def _create_record_info(source_record: ET.Element) -> ET.Element:
    source_old_id = source_record.find(f".//old_id")
    assert (
        source_old_id is not None and source_old_id.text is not None
    ), "old_id is missing in source record"

    return record_info_create(
        validation_type_id="diva-funder",
        old_id=source_old_id.text,
        permission_unit_id=None,
    )


def _create_authority_swe(source_record: ET.Element) -> ET.Element | None:
    name = source_record.findtext(f".//name_swe")
    return (
        create_group(
            "authority",
            lang="swe",
            repeatId="swe",
            children=[name_type_corporate_create(name)],
        )
        if name
        else None
    )


def _create_authority_eng(source_record: ET.Element) -> ET.Element | None:
    name = source_record.findtext(f".//name_eng")
    return (
        create_group(
            "authority",
            lang="eng",
            repeatId="eng",
            children=[name_type_corporate_create(name)],
        )
        if name
        else None
    )


def _create_end_date(source_record: ET.Element) -> ET.Element | None:
    end_date = source_record.find(f".//end_date")
    if end_date is not None and end_date.text:
        return create_end_date(end_date.text)


def _create_identifiers_from_source(
    source_record: ET.Element, identifier_type: str
) -> ET.Element | None:
    identifier = source_record.find(f".//identifier_{identifier_type}")
    if identifier is not None and identifier.text:
        return create_identifiers_from_source(identifier.text, identifier_type)
