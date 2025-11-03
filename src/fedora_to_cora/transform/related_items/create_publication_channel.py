import xml.etree.ElementTree as ET


def create_publication_channel(source_record: ET.Element) -> ET.Element | None:
    publication_channel = source_record.findtext("publicationChannel")
    if publication_channel is None or len(publication_channel) == 0:
        return None

    related_item = ET.Element("relatedItem", type="publicationChannel")
    ET.SubElement(related_item, "publicationChannel").text = publication_channel
    return related_item
