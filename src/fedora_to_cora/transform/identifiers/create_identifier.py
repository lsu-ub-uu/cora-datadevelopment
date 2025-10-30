import xml.etree.ElementTree as ET


def create_identifier(
    source_record: ET.Element,
    type: str,
    source_selector: str | None = None,
) -> list[ET.Element]:
    """
    Create identifier elements for a given type
    """
    if source_selector is None:
        source_selector = f"./{type}"

    source_texts = source_record.findall(source_selector)
    identifiers = []

    for i, source_text in enumerate(source_texts):
        if type == "localId":
            identifier = ET.Element("identifier", type=type, repeatId=str(i))
        else:
            if len(source_texts) > 1:
                identifier = ET.Element("identifier", type=type, repeatId=str(i))
            else:
                identifier = ET.Element("identifier", type=type)

        if source_text is not None and source_text.text:
            identifier.text = source_text.text

        identifiers.append(identifier)

    return identifiers
