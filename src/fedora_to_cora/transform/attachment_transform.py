from typing import Optional
import xml.etree.ElementTree as ET
from common.common_data import create_record_link_using_name_type_id
from common.xml_utils import append_if_value
from fedora_to_cora.transform.binary.get_attachment_type import get_attachment_type


def attachment_transform(
    source_attachment: ET.Element,
    validation_type: str,
    binary_record_id: str,
    file_upload_message: Optional[str] = None,
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

    if should_have_attachment_version(validation_type):
        append_if_value(
            attachment,
            _create_attachment_version(source_attachment),
        )

    append_if_value(
        attachment, _create_admin_info(source_attachment, file_upload_message)
    )

    return attachment


def should_have_attachment_version(validation_type: str) -> bool:
    validation_types_with_attachment_version = {
        "publication_newspaper-article",
        "publication_book-review",
        "publication_magazine-article",
        "publication_journal-article",
        "publication_review-article",
        "publication_editorial-letter",
    }
    return validation_type in validation_types_with_attachment_version


def _create_attachment_version(source_attachment: ET.Element) -> Optional[ET.Element]:
    attachment_version = _get_attachment_version(source_attachment)
    if attachment_version is None:
        return None

    note = ET.Element("note", type="attachmentVersion")
    note.text = attachment_version
    return note


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


def _create_admin_info(
    source_attachment: ET.Element, file_upload_message: Optional[str]
) -> ET.Element:
    admin_info = ET.Element("adminInfo")
    ET.SubElement(admin_info, "availability").text = "availableNow"

    if source_attachment.findtext("secrecyInfo/secrecy") == "true":
        ET.SubElement(admin_info, "secrecy").text = "true"

    registration_number = source_attachment.findtext("./registrationNumber")
    if registration_number is not None:
        ET.SubElement(admin_info, "identifier", type="registrationNumber").text = (
            registration_number
        )

    if file_upload_message is not None:
        ET.SubElement(admin_info, "note", type="attachment").text = (
            f"""**The following note was migrated from a DiVA Classic file upload message, and may not refer to this attachment**:\n\n{file_upload_message}"""
        )
    return admin_info
