import xml.etree.ElementTree as ET

from common.xml_utils import create_group, create_text
from fedora_to_cora.clean_rich_text import clean_rich_text


def create_physical_description(
    source_record: ET.Element,
) -> ET.Element | None:
    return create_group(
        "physicalDescription",
        [_create_extent_pages(source_record), _create_extent_other(source_record)],
    )


def _create_extent_pages(
    source_record: ET.Element,
) -> ET.Element | None:
    """
    Create an extent element from source record pages element.
    """
    return create_text("extent", source_record.findtext("./pages"), unit="pages")


def _create_extent_other(
    source_record: ET.Element,
) -> ET.Element | None:
    source_texts = source_record.findall(
        "./mediaInformation/physicalDescriptions/abstract/text"
    )

    if source_texts is None or len(source_texts) == 0:
        return None

    cleaned_texts = [clean_rich_text(elem.text) for elem in source_texts]
    extent_value = ", ".join(text for text in cleaned_texts if text is not None)

    return create_text(
        "extent",
        unit="other",
        value=extent_value,
    )
