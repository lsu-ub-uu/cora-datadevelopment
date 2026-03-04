import xml.etree.ElementTree as ET

from common.xml_utils import create_text
from fedora_to_cora.clean_rich_text import clean_rich_text


def create_abstracts(source_record: ET.Element) -> list[ET.Element]:
    """
    Create a list of abstract elements from the source record.

    Args:
        source_record (ET.Element): The source XML element containing publication data.

    Returns:
        list[ET.Element]: A list of abstract elements.
    """
    abstracts = []
    for i, source_abstract in enumerate(source_record.findall("./abstracts/abstract")):
        abstract = create_abstract(source_abstract, i)
        if abstract is not None:
            abstracts.append(abstract)
    return abstracts


def create_abstract(source_abstract: ET.Element, repeat_id: int) -> ET.Element | None:
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

    return create_text(
        "abstract",
        lang=source_language.text,
        repeatId=str(repeat_id),
        value=clean_rich_text(source_abstract.findtext("./text")),
        preserve_newlines=True,
    )
