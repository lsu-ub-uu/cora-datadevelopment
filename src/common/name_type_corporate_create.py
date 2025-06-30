import xml.etree.ElementTree as ET


def name_type_corporate_create(name: str) -> ET.Element:
    """
    Create a Cora name element from a source record.
    """
    name_type_corporate = ET.Element("name", type="corporate")

    name_part = ET.SubElement(name_type_corporate, "namePart")
    name_part.text = name

    return name_type_corporate
