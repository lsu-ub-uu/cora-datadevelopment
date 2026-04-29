import xml.etree.ElementTree as ET

from common.xml_utils import create_group, create_text


def create_locations(source_record: ET.Element) -> list[ET.Element | None]:
    urls = source_record.findall("./urls/url")
    return [
        _create_location(url, str(i))
        for i, url in enumerate(urls)
        if url is not None and url.text
    ]


def create_location_display_label_order_link(
    source_record: ET.Element,
) -> ET.Element | None:
    order_url = source_record.findtext("./publicationOrder/orderURL")
    if order_url is None or order_url == "":
        return None

    return create_group(
        "location",
        [
            create_text("url", order_url),
            create_text("displayLabel", "Beställ/Order"),
        ],
        displayLabel="orderLink",
        repeatId="0",
    )


def _create_location(url: ET.Element, repeat_id: str):
    return create_group(
        "location",
        [
            create_text("url", url.findtext("url")),
            create_text("displayLabel", url.findtext("label")),
        ],
        repeatId=repeat_id,
    )
