from common.date_utils import is_after_now
import xml.etree.ElementTree as ET
from fedora_to_cora.transform.binary.get_binary_visibility import get_binary_visibility


def get_binary_requested_visibility(source_attachment: ET.Element) -> str:
    to_be_published = source_attachment.findtext("./toBePublished") == "true"
    to_be_archived = source_attachment.findtext("./toBeArchived") == "true"
    secrecy = source_attachment.findtext("./secrecyInfo/secrecy") == "true"
    archive_only = source_attachment.findtext("./archiveOnly") == "true"
    temp_available_from = source_attachment.findtext("./tempAvailableFrom")
    available_from = source_attachment.findtext("./availableFrom")

    if archive_only:
        return "unpublished"

    if secrecy:
        return "confidential"

    if to_be_archived:
        return "unpublished"

    if to_be_published:
        return "published"

    if temp_available_from is not None:
        return "published"

    if available_from is not None and is_after_now(available_from):
        return "published"

    return "published"
