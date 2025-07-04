import xml.etree.ElementTree as ET
from cora.context import Context
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link_using_name_type_id


def create_related_item_type_series(
    source_record: ET.Element, context: Context
) -> list[ET.Element]:
    """
    Create relatedItem elements of type series from the source record.
    """
    related_items = []
    controlled_series_ids = source_record.findall(
        "./seriesInfos/seriesInfo/series/seriesId"
    )
    uncontrolled_series_ids = source_record.findall(
        "./seriesInfos/uncontrolledSeriesInfo"
    )

    controlled_related_items = [
        _create_controlled_series_link(series_id.text, f"controlled{i}", context)
        for i, series_id in enumerate(controlled_series_ids)
        if series_id.text
    ]

    related_items.extend(controlled_related_items)

    return related_items


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
