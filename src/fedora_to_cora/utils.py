import xml.etree.ElementTree as ET
from fedora_to_cora.transform.get_validation_type import (
    get_validation_type_from_fedora_record,
)


def is_part_of_book(source_record: ET.Element) -> bool:
    validation_type = get_validation_type_from_fedora_record(source_record)
    return validation_type == "publication_book-chapter"


def is_part_of_conference(source_record: ET.Element) -> bool:
    validation_type = get_validation_type_from_fedora_record(source_record)
    return validation_type == "conference_paper"
