import xml.etree.ElementTree as ET

from common.xml_utils import append_if_value
from fedora_to_cora.clean_rich_text import clean_rich_text


def create_physical_description(
    source_record: ET.Element,
) -> ET.Element:
    physical_description = ET.Element("physicalDescription")

    append_if_value(physical_description, _create_extent_pages(source_record))
    append_if_value(physical_description, _create_extent_other(source_record))

    return physical_description


def _create_extent_pages(
    source_record: ET.Element,
) -> ET.Element | None:
    """
    Create an extent element from source record pages element.
    """
    pages = source_record.findtext("./pages")
    if pages is None or len(pages) == 0:
        return None

    extent = ET.Element("extent", unit="pages")
    extent.text = pages
    return extent


def _create_extent_other(
    source_record: ET.Element,
) -> ET.Element | None:
    source_texts = source_record.findall(
        "./mediaInformation/physicalDescriptions/abstract/text"
    )

    if source_texts is None or len(source_texts) == 0:
        return None

    extent = ET.Element("extent", unit="other")
    extent.text = ", ".join(
        [clean_rich_text(elem.text) for elem in source_texts if elem.text is not None]
    )

    return extent
