import xml.etree.ElementTree as ET

from common.xml_utils import create_text
from fedora_to_cora.clean_rich_text import clean_rich_text


def create_note(
    source_record: ET.Element, type: str, source_selector: str
) -> ET.Element | None:
    """
    Create a note element from the source record.
    """

    return create_text(
        "note",
        type=type,
        value=clean_rich_text(source_record.findtext(source_selector)),
    )
