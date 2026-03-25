import xml.etree.ElementTree as ET
from cora.context import Context
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link
from fedora_to_cora.transform.identifiers.create_identifier import create_identifier
from common.xml_utils import append_if_value, create_group, create_text


def create_related_item_type_series(
    source_record: ET.Element, context: Context
) -> list[ET.Element]:
    """
    Create relatedItem elements of type series from the source record.

    Creates links to series for seriesInfo elements with seriesId and fills data from uncontrolledSeriesInfo.
    """
    controlled_items = _create_related_items_from_controlled_series(
        source_record, context
    )
    uncontrolled_items = _create_related_items_from_uncontrolled_series(source_record)

    return [item for item in controlled_items + uncontrolled_items if item is not None]


def _create_related_items_from_controlled_series(
    source_record: ET.Element, context: Context
) -> list[ET.Element | None]:
    controlled_series_infos = source_record.findall("./seriesInfos/seriesInfo")
    return [
        _create_controlled_series(series_info, f"controlled{i}", context)
        for i, series_info in enumerate(controlled_series_infos)
        if series_info.findtext("series/seriesId") is not None
    ]


def _create_controlled_series(
    series_info: ET.Element, repeat_id: str, context: Context
) -> ET.Element | None:
    """
    Create a relatedItem element of type series with a controlled series link.
    """
    series_id = series_info.findtext("series/seriesId")
    assert series_id is not None

    series_cora_id = get_cora_id_by_old_id(
        series_id, record_type="diva-series", context=context
    )

    return create_group(
        "relatedItem",
        [
            create_record_link(
                name_in_data="topic",
                record_type="diva-series",
                record_id=series_cora_id,
            ),
            create_text("partNumber", series_info.findtext("numberInSeries")),
        ],
        type="series",
        otherType="link",
        repeatId=repeat_id,
    )


def _create_related_items_from_uncontrolled_series(
    source_record: ET.Element,
) -> list[ET.Element | None]:
    uncontrolled_series_infos = source_record.findall("./uncontrolledSeriesInfo")
    return [
        _create_uncontrolled_series(series_xml, f"uncontrolled{i}")
        for i, series_xml in enumerate(uncontrolled_series_infos)
    ]


def _create_uncontrolled_series(
    series_xml: ET.Element, repeat_id: str
) -> ET.Element | None:
    """
    Create a relatedItem element of type series with an uncontrolled series link.
    """
    return create_group(
        "relatedItem",
        [
            _create_title_info(series_xml.findtext("./series/seriesNameUncontrolled")),
            create_identifier(
                source_record=series_xml,
                type="issn",
                source_selector="./series/issn",
                displayLabel="pissn",
            ),
            create_identifier(
                source_record=series_xml,
                type="issn",
                source_selector="./series/eissn",
                displayLabel="eissn",
            ),
            create_text("partNumber", series_xml.findtext("numberInSeries")),
        ],
        type="series",
        otherType="text",
        repeatId=repeat_id,
    )


def _create_title_info(title: str | None) -> ET.Element | None:
    return create_group(
        "titleInfo",
        children=[
            create_text(
                "title",
                title,
            )
        ],
    )
