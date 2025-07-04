import xml.etree.ElementTree as ET
from fedora_to_cora.create_note import create_note
from common.xml_utils import append_if_value


def create_admin_info(source_record: ET.Element) -> ET.Element:
    """
    Create an admin element with internal notes and reviewed status.
    """
    admin_info = ET.Element("adminInfo")

    append_if_value(
        admin_info,
        create_note(source_record, type="internal", source_selector="./internalNote"),
    )

    reviewed = source_record.find("./reviewed")
    if reviewed is not None and reviewed.text:
        ET.SubElement(admin_info, "reviewed").text = reviewed.text

    failed = source_record.find("./failed")
    if failed is not None and failed.text == "true":
        ET.SubElement(admin_info, "failed").text = failed.text

    return admin_info
