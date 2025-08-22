import xml.etree.ElementTree as ET
from common.common_data import create_record_link_using_name_type_id
from common.xml_utils import append_if_value
from fedora_to_cora.transform.binary.get_attachment_type import get_attachment_type


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

    ET.SubElement(attachment, "type").text = get_attachment_type(source_attachment)

    attachment_version = _get_attachment_version(source_attachment)
    if attachment_version is not None:
        ET.SubElement(attachment, "note", type="attachmentVersion").text = (
            attachment_version
        )

    append_if_value(attachment, _create_admin_info(source_attachment))

    return attachment


def _get_attachment_version(source_attachment: ET.Element) -> str | None:
    prePrint = source_attachment.findtext("./prePrint")
    postPrint = source_attachment.findtext("./postPrint")
    print_ = source_attachment.findtext("./print")

    # Validate at most one tag is set to "true"
    true_count = sum(1 for value in [prePrint, postPrint, print_] if value == "true")
    if true_count > 1:
        raise ValueError("Multiple attachment versions found")

    if prePrint == "true":
        return "submitted"
    elif postPrint == "true":
        return "accepted"
    elif print_ == "true":
        return "published"
    return None


def _create_admin_info(source_attachment: ET.Element) -> ET.Element:
    admin_info = ET.Element("adminInfo")
    ET.SubElement(admin_info, "availability").text = "availableNow"

    if source_attachment.findtext("secrecyInfo/secrecy") == "true":
        ET.SubElement(admin_info, "secrecy").text = "true"

    registration_number = source_attachment.findtext("./registrationNumber")
    if registration_number is not None:
        ET.SubElement(admin_info, "identifier", type="registrationNumber").text = (
            registration_number
        )

    return admin_info
