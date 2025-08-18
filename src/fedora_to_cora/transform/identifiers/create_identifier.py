import xml.etree.ElementTree as ET


def create_identifier(
    source_record: ET.Element,
    type: str,
    source_selector: str | None = None,
) -> ET.Element:
    """
    Create an identifier element for a given type
    """
    if source_selector is None:
        source_selector = f"./{type}"

    identifier = ET.Element("identifier", type=type)
    source_text = source_record.find(source_selector)

    if source_text is not None and source_text.text:
        identifier.text = source_text.text

    return identifier
