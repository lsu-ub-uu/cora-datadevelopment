import xml.etree.ElementTree as ET
from common.date_utils import is_before_now


def get_binary_visibility(fedora_attachment: ET.Element) -> str:
    deleted = fedora_attachment.findtext("./deleted")
    on_hold = fedora_attachment.findtext("./onHold")
    archive_only = fedora_attachment.findtext("./archiveOnly")
    to_be_archived = fedora_attachment.findtext("./toBeArchived")
    to_be_published = fedora_attachment.findtext("./toBePublished")
    available_from = fedora_attachment.findtext("./availableFrom")
    available_until = fedora_attachment.findtext("./availableUntil")
    print_on_demand = fedora_attachment.findtext("./printOnDemand")

    if deleted == "true":
        return "unpublished"

    if on_hold == "true":
        return "unpublished"

    if archive_only == "true":
        return "unpublished"

    if to_be_archived == "true":
        return "unpublished"

    if to_be_published == "true":
        return "unpublished"

    if print_on_demand == "true":
        return "unpublished"

    if available_from is not None and is_before_now(available_from):
        if available_until is not None and is_before_now(available_until):
            return "unpublished"
        return "published"

    return "unpublished"
