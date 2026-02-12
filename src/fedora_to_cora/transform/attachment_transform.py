from typing import Optional
import xml.etree.ElementTree as ET
from common.common_data import create_record_link_using_name_type_id
from common.xml_utils import append_if_value, transform_text_element
from fedora_to_cora.transform.binary.get_attachment_type import get_attachment_type
from fedora_to_cora.transform.binary.get_binary_requested_visibility import (
    get_binary_requested_visibility,
)
from fedora_to_cora.transform.create_date import create_date
from datetime import datetime, timezone


def attachment_transform(
    source_attachment: ET.Element,
    validation_type: str,
    binary_record_id: str,
    file_upload_message: Optional[str] = None,
) -> ET.Element:
    attachment = ET.Element("attachment", repeatId=binary_record_id)
    attachment.append(
        create_record_link_using_name_type_id(
            name_in_data="file",
            record_type="binary",
            record_id=binary_record_id,
        )
    )

    ET.SubElement(attachment, "label").text = get_attachment_type(source_attachment)

    if should_have_attachment_version(validation_type):
        append_if_value(
            attachment,
            _create_attachment_version(source_attachment),
        )

    append_if_value(
        attachment, _create_admin_info(source_attachment, file_upload_message)
    )
    append_if_value(
        attachment,
        transform_text_element(
            source_attachment.find("./selectedFileName"), "displayLabel"
        ),
    )
    append_if_value(
        attachment,
        _create_requested_visibility(source_attachment),
    )
    append_if_value(
        attachment,
        transform_text_element(source_attachment.find("./digitized"), "digitized"),
    )
    append_if_value(
        attachment,
        transform_text_element(
            source_attachment.find("./printOnDemand"), "printReadyFile"
        ),
    )

    available_from = source_attachment.findtext("./availableFrom")
    if available_from is not None and available_from > _get_now():
        append_if_value(
            attachment,
            create_date(available_from, "dateToBePublished"),
        )

    append_if_value(
        attachment,
        create_date(
            source_attachment.findtext("./availableUntil"), "dateToBeUnpublished"
        ),
    )

    return attachment


def should_have_attachment_version(validation_type: str) -> bool:
    validation_types_with_attachment_version = {
        "publication_encyclopedia-entry",
        "conference_poster",
        "publication_newspaper-article",
        "conference_paper",
        "publication_book-review",
        "conference_other",
        "conference_poster",
        "conference_proceeding",
    }
    return validation_type in validation_types_with_attachment_version


def _create_requested_visibility(source_attachment: ET.Element) -> ET.Element:
    requested_visibility = ET.Element("requestedVisibility")
    requested_visibility.text = get_binary_requested_visibility(source_attachment)
    return requested_visibility


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


def _create_display_label(source_attachment: ET.Element) -> Optional[ET.Element]:
    selected_file_name = source_attachment.findtext("./selectedFileName")
    if selected_file_name is not None and selected_file_name.strip() != "":
        display_label = ET.Element("displayLabel")
        display_label.text = selected_file_name
        return display_label


def _get_now() -> str:
    return datetime.now(timezone.utc).isoformat()
