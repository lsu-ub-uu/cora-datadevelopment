import xml.etree.ElementTree as ET


def create_admin(source_record: ET.Element) -> ET.Element:
    """
    Create an admin element with internal notes and reviewed status.
    """
    admin = ET.Element("admin")

    internal_note = source_record.find("./internalNote")
    if internal_note is not None and internal_note.text:
        note = ET.SubElement(admin, "note", type="internal")
        note.text = internal_note.text

    reviewed = source_record.find("./reviewed")
    if reviewed is not None and reviewed.text:
        ET.SubElement(admin, "reviewed").text = reviewed.text

    return admin
