import xml.etree.ElementTree as ET


def create_locations(source_record: ET.Element) -> list[ET.Element]:
    """
    Create location elements from the source record.
    """

    urls = source_record.findall(".//urls/url")
    return [
        _create_location(url, str(i))
        for i, url in enumerate(urls)
        if url is not None and url.text
    ]


def _create_location(url: ET.Element, repeat_id: str):
    """
    Create a single location element from a URL element.
    """
    location = ET.Element("location", repeatId=repeat_id)
    url_element = url.find("url")
    label_element = url.find("label")

    if url_element is not None:
        ET.SubElement(location, "url").text = url_element.text
    if label_element is not None:
        ET.SubElement(location, "displayLabel").text = label_element.text

    # TODO Handle openAccess

    return location
