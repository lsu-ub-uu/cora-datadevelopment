import xml.etree.ElementTree as ET

from common.xml_utils import create_text


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
        identifiers.append(
            create_text(
                "identifier",
                source_text.text,
                type=type,
                repeatId=str(i) if type == "localId" or len(source_texts) > 1 else None,
            )
        )

    return identifiers
