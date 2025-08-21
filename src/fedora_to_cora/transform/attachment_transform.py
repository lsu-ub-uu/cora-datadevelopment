import xml.etree.ElementTree as ET
from common.common_data import create_record_link_using_name_type_id


def attachment_transform(
    source_attachment: ET.Element, binary_record_id: str
) -> ET.Element:
    attachment = ET.Element("attachment", repeatId=binary_record_id)
    attachment.append(
        create_record_link_using_name_type_id(
            name_in_data="attachmentFile",
            record_type="binary",
            record_id=binary_record_id,
        )
    )
    ET.SubElement(attachment, "type").text = "fullText"

    admin_info = ET.SubElement(attachment, "adminInfo")
    ET.SubElement(admin_info, "availability").text = "availableNow"

    return attachment
