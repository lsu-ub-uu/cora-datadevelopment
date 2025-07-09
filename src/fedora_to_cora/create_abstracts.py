import xml.etree.ElementTree as ET


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

    abstract_element = ET.Element(
        "abstract", lang=source_language.text, repeatId=str(repeat_id)
    )

    source_text = source_abstract.find("./text")
    if source_text is None:
        return None

    abstract_element.text = source_text.text

    return abstract_element
