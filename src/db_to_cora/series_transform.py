import xml.etree.ElementTree as ET
from common.xml_utils import append_if_value
from common.record_info_create import record_info_create
from common.common_data import create_title_info
from common.common_data import create_title_info_type_alternative
from common.common_data import create_origin_info
from common.common_data import create_identifiers_from_source_with_type_issn
from common.common_data import create_location
from common.common_data import create_note
from common.common_data import create_genre
from common.xml_validate import XMLSpec, validate_xml

nameInData = "series"
allowed_children: XMLSpec = {
    "domain": "text",
    "old_id": "text",
    "title": "text",
    "subtitle": "text",
    "alternative_title": "text",
    "alternative_subtitle": "text",
    "end_date": "text",
    "identifier_pissn": "text",
    "identifier_eissn": "text",
    "format_id": "text",
    "format_code": "text",
    "url": "text",
    "internal_note": "text",
    "publication_type_id": "text",
    "publication_type_code": "text",
    "relation_type_id": "text",
    "relative_id_host": "text",
    "series_id": "text",
    "relation_type_id": "text",
    "relative_id_preceding": "text",
    "series_id": "text",
    "organisation_id": "text",
}


def transform_series(source_record: ET.Element) -> ET.Element:
    """
    Create a Cora series element from a DB export series.
    """
    validate_xml(source_record, allowed_children)

    series = ET.Element(nameInData)

    series.append(_create_record_info(source_record))
    append_if_value(series, _create_title_info(source_record))
    append_if_value(series, _create_title_info_type_alternative(source_record))
    append_if_value(
        series, _create_origin_info(source_record, origin_type="originInfo")
    )
    append_if_value(
        series,
        _create_identifiers_from_source_with_type_issn(
            source_record, identifier_type="pissn"
        ),
    )
    append_if_value(
        series,
        _create_identifiers_from_source_with_type_issn(
            source_record, identifier_type="eissn"
        ),
    )
    append_if_value(series, _create_location(source_record))
    append_if_value(series, _create_note(source_record, note_type="internal"))
    append_if_value(series, _create_genre(source_record))

    return series


def _create_record_info(source_record: ET.Element) -> ET.Element:
    source_old_id = source_record.find(f"./old_id")
    assert (
        source_old_id is not None and source_old_id.text is not None
    ), "old_id is missing in source record"

    return record_info_create(
        validation_type_id="diva-series",
        old_id=source_old_id.text,
        permission_unit_id=_create_permission_unit(source_record),
    )


def _create_permission_unit(source_record: ET.Element) -> str:
    domain = source_record.find("./domain")
    assert (
        domain is not None and domain.text is not None
    ), "domain is missing in source record"

    return domain.text


def _create_title_info(source_record: ET.Element) -> ET.Element | None:
    title = source_record.findtext(f"./title")
    subtitle = source_record.findtext(f"./subtitle")
    if title:
        return create_title_info(title, subtitle)


def _create_title_info_type_alternative(source_record: ET.Element) -> ET.Element | None:
    title = source_record.findtext(f"./alternative_title")
    subtitle = source_record.findtext(f"./alternative_subtitle")
    if title:
        return create_title_info_type_alternative(title, subtitle)


def _create_origin_info(
    source_record: ET.Element, origin_type: str
) -> ET.Element | None:
    end_date = source_record.find(f"./end_date")
    if end_date is not None and end_date.text:
        return create_origin_info(end_date.text, origin_type)


def _create_identifiers_from_source_with_type_issn(
    source_record: ET.Element, identifier_type: str
) -> ET.Element | None:
    identifier = source_record.find(f"./identifier_{identifier_type}")
    if identifier is not None and identifier.text:
        return create_identifiers_from_source_with_type_issn(
            identifier.text, identifier_type
        )


def _create_location(source_record: ET.Element) -> ET.Element | None:
    url = source_record.find(f"./url")
    if url is not None and url.text:
        return create_location(url.text)


def _create_note(source_record: ET.Element, note_type: str) -> ET.Element | None:
    note = source_record.find(f"./external_note")
    if note is not None and note.text:
        return create_note(note.text, note_type)


def _create_genre(source_record: ET.Element) -> ET.Element | None:
    publication_type = source_record.find(f"./publication_type_id")
    if publication_type is not None and publication_type.text:
        return create_genre(publication_type.text, "0")
