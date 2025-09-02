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
from common.common_data import create_record_link_test
from common.common_data import create_record_link_using_name_type_id


nameInData = "series"
permissionUnit = "varldskulturmuseerna"


def transform_series(source_record: ET.Element) -> ET.Element:
    """
    Create a Cora series element from a DB export series.
    """

    create_genre._counter = -1
    genre_repeat_id = dict(repeatId=0)
    create_record_link_test._counter = -1
    link_repeat_id = dict(repeatId=0)

    series = ET.Element(nameInData)

    series.append(_create_record_info(source_record))
    series.append(_create_title_info(source_record))
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
    append_if_value(series, _create_note(source_record, note_type="external"))
    append_if_value(series, _create_genre(source_record, genre_repeat_id))
    append_if_value(
        series,
        _create_record_link_using_name_type_id(
            source_record, name_in_data="organisation", record_type="diva-organisation"
        ),
    )
    append_if_value(
        series,
        _create_record_link_test(
            source_record,
            link_repeat_id,
            record_type="diva-series",
            name_in_data="related",
            related_type="host",
        ),
    )
    append_if_value(
        series,
        _create_record_link_test(
            source_record,
            link_repeat_id,
            record_type="diva-series",
            name_in_data="related",
            related_type="preceding",
        ),
    )

    return series


def _create_record_info(source_record: ET.Element) -> ET.Element:
    source_old_id = source_record.find(f".//old_id")
    assert (
        source_old_id is not None and source_old_id.text is not None
    ), "old_id is missing in source record"

    return record_info_create(
        validation_type_id="diva-series",
        old_id=source_old_id.text,
        permission_unit_id=permissionUnit,
    )


def _create_title_info(source_record: ET.Element) -> ET.Element:
    title = source_record.findtext(f".//title")
    subtitle = source_record.findtext(f".//subtitle")
    if title is not None:
        return create_title_info(title, subtitle)


def _create_title_info_type_alternative(source_record: ET.Element) -> ET.Element | None:
    title = source_record.findtext(f".//alternative_title")
    subtitle = source_record.findtext(f".//alternative_subtitle")
    if title is not None:
        return create_title_info_type_alternative(title, subtitle)


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


def _create_note(source_record: ET.Element, note_type: str) -> ET.Element | None:
    note = source_record.find(f".//external_note")
    if note is not None and note.text:
        return create_note(note.text, note_type)


def _create_genre(
    source_record: ET.Element, genre_repeat_id: dict
) -> ET.Element | None:
    publication_type = source_record.find(f".//publication_type_id")
    if publication_type is not None and publication_type.text:
        return create_genre(publication_type.text, genre_repeat_id)


def _create_record_link_test(
    source_record: ET.Element,
    link_repeat_id: dict,
    record_type: str,
    name_in_data: str,
    related_type: str,
) -> ET.Element | None:
    old_record_id = source_record.find(f".//{related_type}_id")
    if old_record_id is not None and old_record_id.text:
        return create_record_link_test(
            old_record_id.text,
            link_repeat_id,
            record_type,
            name_in_data,
            related_type,
        )


def _create_record_link_using_name_type_id(
    source_record: ET.Element, name_in_data: str, record_type: str
) -> ET.Element | None:
    record_id = source_record.find(f".//organisation_id")
    if record_id is not None and record_id.text:
        return create_record_link_using_name_type_id(
            name_in_data, record_type, record_id.text
        )
