import xml.etree.ElementTree as ET
from typing import Optional, List
from common.xml_utils import create_text


def create_identifier(
    source_record: ET.Element,
    type: str,
    source_selector: Optional[str] = None,
    **attributes: Optional[str],
) -> List[ET.Element]:
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
                preserve_newlines=False,
                **attributes,
            )
        )

    return identifiers
