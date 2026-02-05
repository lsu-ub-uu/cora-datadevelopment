import xml.etree.ElementTree as ET
from fedora_to_cora.transform.binary.get_binary_visibility import get_binary_visibility


def get_availablity(source_attachment: ET.Element) -> str:
    published = get_binary_visibility(source_attachment) == "published"
    to_be_published = source_attachment.findtext("./toBePublished") == "true"
    to_be_archived = source_attachment.findtext("./toBeArchived") == "true"
    secrecy = source_attachment.findtext("./secrecyInfo/secrecy") == "true"

    if secrecy:
        return "secrecy"
    
    if published:
         return "available"

    if to_be_archived:
        return "unavailable"

    if to_be_published:
        return "available"
    
    return "unavailable"