import xml.etree.ElementTree as ET


def create_related_item_type_conference(
    source_record: ET.Element,
) -> ET.Element | None:
    conference = source_record.findtext("./conference")
    if conference:
        related_item = ET.Element("relatedItem", type="conference")
        conference_element = ET.SubElement(related_item, "conference")
        conference_element.text = conference
        return related_item
    return None
