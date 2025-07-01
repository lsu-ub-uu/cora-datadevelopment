import xml.etree.ElementTree as ET
from common.name_type_corporate_create import name_type_corporate_create


def create_authority_or_variant_lang_using_name_type_corporate(name_lang: str, element_name: str, language: str) -> ET.Element:
    """
    Create a Cora authority or variant element from a source record.
    """
    element_name = ET.Element(element_name, lang=language)
    element_name.append(
        name_type_corporate_create(
            name = name_lang
        )
    )
    return element_name