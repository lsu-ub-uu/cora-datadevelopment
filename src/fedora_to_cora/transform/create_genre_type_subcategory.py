import xml.etree.ElementTree as ET

from common.xml_utils import create_text

subtype_to_subcategory = {
    "policyDocument": "policyDocument",
    "exhibitionCatalogue": "exhibitionCatalog",
}


def create_genre_type_subcategory(
    source_record: ET.Element,
) -> ET.Element | None:
    publication_subtype_id = source_record.findtext("./subtype/publicationSubtypeCode")

    if publication_subtype_id in subtype_to_subcategory:
        return create_text(
            "genre",
            type="subcategory",
            value=subtype_to_subcategory[publication_subtype_id],
        )

    return None
