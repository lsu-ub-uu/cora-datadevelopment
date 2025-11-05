import xml.etree.ElementTree as ET

subtype_to_subcategory = {
    "policyDocument": "policyDocument",
    "exhibitionCatalogue": "exhibitionCatalog",
}


def create_genre_type_subcategory(
    source_record: ET.Element,
) -> ET.Element | None:
    publication_subtype_id = source_record.findtext("./subtype/publicationSubtypeCode")

    if publication_subtype_id in subtype_to_subcategory:
        genre_type_subcategory = ET.Element("genre", type="subcategory")
        genre_type_subcategory.text = subtype_to_subcategory[publication_subtype_id]
        return genre_type_subcategory

    return None
