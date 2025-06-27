import xml.etree.ElementTree as ET


def create_admin_info(source_record: ET.Element) -> ET.Element:
    """
    Create an admin element with internal notes and reviewed status.
    """
    admin_info = ET.Element("adminInfo")

    internal_note = source_record.find("./internalNote")
    if internal_note is not None and internal_note.text:
        note = ET.SubElement(admin_info, "note", type="internal")
        note.text = internal_note.text

    reviewed = source_record.find("./reviewed")
    if reviewed is not None and reviewed.text:
        ET.SubElement(admin_info, "reviewed").text = reviewed.text

    return admin_info
