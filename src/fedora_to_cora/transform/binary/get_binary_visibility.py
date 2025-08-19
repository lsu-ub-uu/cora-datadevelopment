import xml.etree.ElementTree as ET
from datetime import datetime


def get_binary_visibility(fedora_attachment: ET.Element) -> str:
    today = _get_today()
    deleted = fedora_attachment.findtext("./deleted")
    on_hold = fedora_attachment.findtext("./onHold")
    available_from = _parse_date(fedora_attachment.findtext("./availableFrom"))
    available_until = _parse_date(fedora_attachment.findtext("./availableUntil"))

    if deleted == "true":
        return "hidden"

    if on_hold == "true":
        return "unpublished"

    if available_from is not None and available_from < today:
        if available_until is not None and available_until < today:
            return "unpublished"
        return "published"

    return "unpublished"


def _get_today() -> datetime:
    return datetime.now().astimezone()


def _parse_date(date_string: str | None) -> datetime | None:
    if date_string is None:
        return None

    try:
        return datetime.fromisoformat(date_string)
    except ValueError:
        return None
