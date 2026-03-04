import xml.etree.ElementTree as ET

from common.xml_utils import create_group, create_text


def create_locations(source_record: ET.Element) -> list[ET.Element | None]:
    """
    Create location elements from the source record.
    """

    urls = source_record.findall("./urls/url")
    return [
        _create_location(url, str(i))
        for i, url in enumerate(urls)
        if url is not None and url.text
    ]


def create_location_display_label_order_link(
    source_record: ET.Element,
) -> ET.Element | None:
    """
    Create location elements with attribute display label from the source record.
    """

    order_url = source_record.findtext("./publicationOrder/orderURL")
    if order_url is None or order_url == "":
        return None

    location = _create_location_display_label(order_url)

    return location


def _create_location(url: ET.Element, repeat_id: str):
    """
    Create a single location element from a URL element.
    """
    return create_group(
        "location",
        [
            create_text("url", url.findtext("url")),
            create_text("displayLabel", url.findtext("label")),
        ],
        repeatId=repeat_id,
    )


def _create_location_display_label(url: str):
    """
    Create a single location element for order link.
    """
    return create_group(
        "location",
        [
            create_text("url", url),
            create_text("displayLabel", "Beställ/Order"),
        ],
        displayLabel="orderLink",
    )
