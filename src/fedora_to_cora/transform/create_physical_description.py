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
    abstracts = source_record.findall(
        "./mediaInformation/physicalDescriptions/abstract/text"
    )

    size = source_record.findtext("./mediaInformation/size")

    parts = []
    if size:
        parts.append(size)

    if abstracts:
        cleaned_texts = [clean_rich_text(elem.text) for elem in abstracts]
        parts.extend(text for text in cleaned_texts if text is not None)

    if not parts:
        return None

    extent_value = ", ".join(parts)

    return create_text(
        "extent",
        unit="other",
        value=extent_value,
    )
