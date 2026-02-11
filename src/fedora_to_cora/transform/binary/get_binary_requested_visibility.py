import xml.etree.ElementTree as ET
from fedora_to_cora.transform.binary.get_binary_visibility import get_binary_visibility


def get_binary_requested_visibility(source_attachment: ET.Element) -> str:
    published = get_binary_visibility(source_attachment) == "published"
    to_be_published = source_attachment.findtext("./toBePublished") == "true"
    to_be_archived = source_attachment.findtext("./toBeArchived") == "true"
    secrecy = source_attachment.findtext("./secrecyInfo/secrecy") == "true"
    archive_only = source_attachment.findtext("./archiveOnly") == "true"

    if archive_only:
        return "unpublished"

    if secrecy:
        return "confidential"

    if published:
        return "published"

    if to_be_archived:
        return "unpublished"

    if to_be_published:
        return "published"

    return "unpublished"
