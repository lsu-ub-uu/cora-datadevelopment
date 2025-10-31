import xml.etree.ElementTree as ET

publication_status_id_to_publication_status = {
    "50": "accepted",
    "51": "inPress",
    "53": "published",
    "54": "submitted",
    "55": "aheadOfPrint",
}


def create_note_type_publication_status(source_record: ET.Element) -> ET.Element | None:
    """
    Create a note element for publication status based on the source record.
    """
    publication_status_id = source_record.findtext(
        "./publicationStatus/publicationStatusId"
    )

    if publication_status_id is None:
        return None

    note = ET.Element("note", type="publicationStatus")

    note.text = _get_publication_status(publication_status_id)

    return note


def _get_publication_status(publication_status_id: str) -> str | None:
    publication_status = publication_status_id_to_publication_status.get(
        publication_status_id
    )

    if publication_status is None:
        return f"UNKNOWN PUBLICATION STATUS: {publication_status_id}"

    return publication_status
