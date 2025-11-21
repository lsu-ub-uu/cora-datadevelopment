import xml.etree.ElementTree as ET


def create_extent(source_record: ET.Element) -> ET.Element | None:
    """
    Create an extent element from source record pages element.
    """
    physical_description = ET.Element("physicalDescription")

    pages = source_record.find("./pages")
    if pages is not None and pages.text:
        ET.SubElement(physical_description, "extent", unit="pages").text = pages.text

    return physical_description
