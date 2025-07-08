import xml.etree.ElementTree as ET
from cora.context import Context
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link_using_name_type_id
from fedora_to_cora.identifiers.create_identifier import create_identifier
from common.xml_utils import append_if_value


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

    return controlled_items + uncontrolled_items


def _create_related_items_from_controlled_series(
    source_record: ET.Element, context: Context
) -> list[ET.Element]:
    controlled_series_ids = source_record.findall(
        "./seriesInfos/seriesInfo/series/seriesId"
    )
    return [
        _create_controlled_series_link(series_id.text, f"controlled{i}", context)
        for i, series_id in enumerate(controlled_series_ids)
        if series_id.text
    ]


def _create_controlled_series_link(
    series_id: str, repeat_id: str, context: Context
) -> ET.Element:
    """
    Create a relatedItem element of type series with a controlled series link.
    """
    series_cora_id = get_cora_id_by_old_id(
        series_id, record_type="diva-series", context=context
    )

    related_item = ET.Element("relatedItem", type="series", repeatId=repeat_id)
    related_item.append(
        create_record_link_using_name_type_id(
            name_in_data="series",
            record_type="diva-series",
            record_id=series_cora_id,
        )
    )
    return related_item


def _create_related_items_from_uncontrolled_series(
    source_record: ET.Element,
) -> list[ET.Element]:
    uncontrolled_series_ids = source_record.findall("./uncontrolledSeriesInfo")
    return [
        _create_uncontrolled_series(series_xml, f"uncontrolled{i}")
        for i, series_xml in enumerate(uncontrolled_series_ids)
    ]


def _create_uncontrolled_series(series_xml: ET.Element, repeat_id: str) -> ET.Element:
    """
    Create a relatedItem element of type series with an uncontrolled series link.
    """
    related_item = ET.Element("relatedItem", type="series", repeatId=repeat_id)

    append_if_value(
        related_item,
        _create_title_info(series_xml.findtext("./series/seriesNameUncontrolled")),
    )

    pissn = create_identifier(
        source_record=series_xml, type="issn", source_selector="./series/issn"
    )
    pissn.set("displayLabel", "pissn")
    append_if_value(related_item, pissn)

    eissn = create_identifier(
        source_record=series_xml, type="issn", source_selector="./series/eissn"
    )
    eissn.set("displayLabel", "eissn")
    append_if_value(related_item, eissn)

    number_in_series = series_xml.findtext("numberInSeries")
    if number_in_series is not None:
        ET.SubElement(related_item, "partNumber").text = number_in_series

    return related_item


def _create_title_info(title: str | None) -> ET.Element:
    """
    Create a titleInfo element with the given title.
    """
    title_info = ET.Element("titleInfo")
    title_element = ET.SubElement(title_info, "title")
    title_element.text = title

    return title_info
