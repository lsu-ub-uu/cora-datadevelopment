import xml.etree.ElementTree as ET


def create_note(
    source_record: ET.Element, type: str, source_selector: str
) -> ET.Element:
    """
    Create a note element from the source record.
    """
    note = ET.Element("note", type=type)

    note_text = source_record.findtext(source_selector)

    if note_text:
        note.text = note_text

    return note
