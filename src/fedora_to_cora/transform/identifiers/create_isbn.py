import xml.etree.ElementTree as ET

from common.xml_utils import create_text


def create_identifier_type_isbn(source_record: ET.Element) -> list[ET.Element]:
    isbn_elements = source_record.findall("./isbnNumbers/isbn")
    identifiers = []
    for i, isbn in enumerate(isbn_elements):
        identifiers.append(
            create_text(
                "identifier",
                isbn.findtext("number"),
                type="isbn",
                displayLabel=_get_display_label(isbn.find("type")),
                repeatId=str(i),
            )
        )

    return identifiers


isbn_type_map = {
    "print": "print",
    "electronic": "online",
    None: "undefined",
}


def _get_display_label(isbn_element):
    """
    Get the display label for the ISBN element.

    Args:
        isbn_element (ET.Element): The XML element containing ISBN information.

    Returns:
        str: The display label.
    """

    key = (
        isbn_element.text
        if isbn_element is not None and isbn_element.text is not None
        else None
    )
    return isbn_type_map[key]
