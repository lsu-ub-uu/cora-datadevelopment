import xml.etree.ElementTree as ET


def create_identifier_type_isrn(source_record: ET.Element) -> ET.Element:
    """
    Create an identifier of type ISRN from the source record.

    Args:
        source_record (ElementTree): The source XML record.
    """
    isrn_element = source_record.find(".//isrn")

    identifier = ET.Element(
        "identifier",
        type="isrn",
    )
    identifier.text = isrn_element.text if isrn_element is not None else None

    return identifier
