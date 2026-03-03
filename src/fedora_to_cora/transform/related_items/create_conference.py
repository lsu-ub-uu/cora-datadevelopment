import xml.etree.ElementTree as ET

from common.xml_utils import create_group, create_text


def create_related_item_type_conference(
    source_record: ET.Element,
) -> ET.Element | None:
    return create_group(
        "relatedItem",
        type="conference",
        children=[create_text("conference", source_record.findtext("./conference"))],
    )
