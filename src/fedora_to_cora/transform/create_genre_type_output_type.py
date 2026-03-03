import xml.etree.ElementTree as ET
from fedora_to_cora.transform.get_validation_type import (
    get_validation_type_from_fedora_record,
)


def create_genre_type_output_type(source_record: ET.Element) -> ET.Element | None:
    validation_type = get_validation_type_from_fedora_record(source_record)

    if validation_type is None:
        return None

    genre = ET.Element("genre", type="outputType")
    genre.text = validation_type

    return genre
