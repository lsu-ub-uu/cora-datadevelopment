import xml.etree.ElementTree as ET


def create_related_item_type_proceeding(
    source_record: ET.Element,
) -> ET.Element | None:
    conference = source_record.findtext("./conference")
    if conference:
        related_item = ET.Element("relatedItem", type="proceeding")
        conference_element = ET.SubElement(related_item, "proceeding")
        conference_element.text = conference
        return related_item
    return None
