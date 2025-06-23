import xml.etree.ElementTree as ET
from fedora_to_cora.get_validation_type_by_publication_type_id import (
    get_validation_type_by_publication_type_id,
)


def create_genre_type_output_type(source_record: ET.Element) -> ET.Element | None:
    publication_type_id = source_record.find(".//publicationTypeId")
    assert (
        publication_type_id is not None and publication_type_id.text is not None
    ), "publicationTypeId is missing in source record"

    validation_type = get_validation_type_by_publication_type_id(
        publication_type_id.text
    )

    genre = ET.Element("genre", type="outputType")
    genre.text = validation_type

    return genre
