from typing import Optional
import xml.etree.ElementTree as ET
from common.common_data import create_record_link_using_name_type_id
from common.date_utils import is_after_now
from common.xml_utils import (
    create_group,
    create_text,
)
from fedora_to_cora.transform.binary.get_attachment_type import get_attachment_type
from fedora_to_cora.transform.binary.get_binary_requested_visibility import (
    get_binary_requested_visibility,
)
from fedora_to_cora.transform.binary.get_binary_visibility import get_binary_visibility
from fedora_to_cora.transform.create_date import create_date
from datetime import datetime


def attachment_transform(
    source_attachment: ET.Element,
    validation_type: str,
    binary_record_id: str,
) -> ET.Element:

    attachment = create_group(
        "attachment",
        repeatId=binary_record_id,
        label=get_attachment_type(source_attachment),
        children=[
            create_record_link_using_name_type_id(
                name_in_data="file",
                record_type="binary",
                record_id=binary_record_id,
            ),
            (
                _create_attachment_version(source_attachment)
                if _should_have_attachment_version(validation_type)
                else None
            ),
            _create_admin_info(source_attachment),
            create_text(
                "displayLabel", source_attachment.findtext("./selectedFileName")
            ),
            _create_requested_visibility(source_attachment),
            create_text("digitized", source_attachment.findtext("./digitized")),
            create_text(
                "printReadyFile", source_attachment.findtext("./printOnDemand")
            ),
            _create_date_to_be_published(source_attachment),
            create_date(
                source_attachment.findtext("./availableUntil"), "dateToBeUnpublished"
            ),
        ],
    )

    assert attachment is not None
    return attachment


def _create_date_to_be_published(source_attachment: ET.Element) -> Optional[ET.Element]:
    temp_available_from = source_attachment.findtext("./tempAvailableFrom")
    available_from = source_attachment.findtext("./availableFrom")

    if temp_available_from is not None:
        return create_date(temp_available_from, "dateToBePublished")

    if available_from is not None and is_after_now(available_from):
        return create_date(available_from, "dateToBePublished")

    return None


def _should_have_attachment_version(validation_type: str) -> bool:
    validation_types_with_attachment_version = {
        "publication_book-chapter",
        "conference_paper",
        "publication_newspaper-article",
        "conference_poster",
        "publication_encyclopedia-entry",
        "publication_foreword-afterword",
        "publication_review-article",
        "publication_journal-article",
        "publication_editorial-letter",
        "publication_report-chapter",
        "publication_book-review",
        "publication_magazine-article",
        "conference_other",
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
    if get_attachment_type(source_attachment) == "fullText":
        note = ET.Element("note", type="attachmentVersion")
        note.text = attachment_version
        return note

    return None


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


def _create_admin_info(source_attachment: ET.Element):
    return create_group(
        "adminInfo",
        children=[
            create_text(
                "secrecy",
                source_attachment.findtext("secrecyInfo/secrecy"),
                type="secrecy",
            ),
            create_text(
                "identifier",
                source_attachment.findtext("./registrationNumber"),
                type="registrationNumber",
            ),
        ],
    )
