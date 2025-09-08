import xml.etree.ElementTree as ET
from common.xml_utils import append_if_value
from common.record_info_create import record_info_create
from common.common_data import create_title_info
from common.common_data import create_origin_info
from common.common_data import create_identifiers_from_source_with_type_issn
from common.common_data import create_location
from db_to_cora.series_transform import _create_title_info
from common.xml_validate import XMLSpec, validate_xml

nameInData = "journal"
allowed_children: XMLSpec = {
    "old_id": "text",
    "title": "text",
    "subtitle": "text",
    "end_date": "text",
    "identifier_eissn": "text",
    "identifier_pissn": "text",
    "url": "text",
}


def transform_journal(source_record: ET.Element) -> ET.Element:
    """
    Create a Cora journal element from a DB export journal.
    """
    validate_xml(source_record, allowed_children)

    journal = ET.Element(nameInData)

    journal.append(_create_record_info(source_record))
    append_if_value(journal, _create_title_info(source_record))
    append_if_value(
        journal, _create_origin_info(source_record, origin_type="originInfo")
    )
    append_if_value(
        journal,
        _create_identifiers_from_source_with_type_issn(
            source_record, identifier_type="pissn"
        ),
    )
    append_if_value(
        journal,
        _create_identifiers_from_source_with_type_issn(
            source_record, identifier_type="eissn"
        ),
    )
    append_if_value(journal, _create_location(source_record))

    return journal


def _create_record_info(source_record: ET.Element) -> ET.Element:
    source_old_id = source_record.find(f".//old_id")
    assert (
        source_old_id is not None and source_old_id.text is not None
    ), "old_id is missing in source record"

    return record_info_create(
        validation_type_id="diva-journal",
        old_id=source_old_id.text,
        permission_unit_id=None,
    )


def _create_title_info(source_record: ET.Element) -> ET.Element | None:
    title = source_record.findtext(f".//title")
    subtitle = source_record.findtext(f".//subtitle")
    if title:
        return create_title_info(title, subtitle)


def _create_origin_info(
    source_record: ET.Element, origin_type: str
) -> ET.Element | None:
    end_date = source_record.find(f".//end_date")
    if end_date is not None and end_date.text:
        return create_origin_info(end_date.text, origin_type)


def _create_identifiers_from_source_with_type_issn(
    source_record: ET.Element, identifier_type: str
) -> ET.Element | None:
    identifier = source_record.find(f".//identifier_{identifier_type}")
    if identifier is not None and identifier.text:
        return create_identifiers_from_source_with_type_issn(
            identifier.text, identifier_type
        )


def _create_location(source_record: ET.Element) -> ET.Element | None:
    url = source_record.find(f".//url")
    if url is not None and url.text:
        return create_location(url.text)
