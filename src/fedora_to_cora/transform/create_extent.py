import xml.etree.ElementTree as ET


def create_extent(source_record: ET.Element) -> ET.Element | None:
    """
    Create an extent element from source record pages element.
    """
    extent = ET.Element("extent")

    pages = source_record.find("./pages")
    if pages is not None and pages.text:
        extent.text = pages.text

    return extent
