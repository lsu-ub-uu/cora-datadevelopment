import xml.etree.ElementTree as ET
from common.xml_utils import get_inner_xml


def create_abstracts(source_record: ET.Element) -> list[ET.Element]:
    """
    Create a list of abstract elements from the source record.

    Args:
        source_record (ET.Element): The source XML element containing publication data.

    Returns:
        list[ET.Element]: A list of abstract elements.
    """

    return [
        create_abstract(abstract, i)
        for (i, abstract) in enumerate(source_record.findall("./abstracts/abstract"))
    ]


def create_abstract(source_abstract: ET.Element, repeat_id: int) -> ET.Element:
    """
    Create an abstract element with a repeatId attribute.

    Args:
        source_abstract (ET.Element): The source abstract element.
        repeat_id (int): The repeat ID for the abstract.

    Returns:
        ET.Element: The created abstract element with repeatId.
    """
    source_language = source_abstract.find("./language/languageCode3")

    assert (
        source_language is not None and source_language.text
    ), "Language code must be present in the abstract"

    abstract_element = ET.Element(
        "abstract", lang=source_language.text, repeatId=str(repeat_id)
    )

    source_text = source_abstract.find("./text")
    if source_text is not None:
        abstract_element.text = source_text.text

    return abstract_element
