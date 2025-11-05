import xml.etree.ElementTree as ET
from fedora_to_cora.transform.get_validation_type import (
    get_validation_type,
)


def create_genre_type_output_type(source_record: ET.Element) -> ET.Element | None:
    publication_type_code = source_record.findtext(
        "./publicationType/publicationTypeCode"
    )
    subtype = source_record.findtext("./subtype/publicationSubtypeCode")
    validation_type = get_validation_type(publication_type_code, subtype)

    if validation_type is None:
        return None

    genre = ET.Element("genre", type="outputType")
    genre.text = validation_type

    return genre
