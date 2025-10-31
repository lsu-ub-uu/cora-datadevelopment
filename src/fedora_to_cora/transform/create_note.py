import xml.etree.ElementTree as ET

from fedora_to_cora.clean_rich_text import clean_rich_text


def create_note(
    source_record: ET.Element, type: str, source_selector: str
) -> ET.Element:
    """
    Create a note element from the source record.
    """
    note = ET.Element("note", type=type)

    note_text = source_record.findtext(source_selector)

    if note_text:
        note.text = clean_rich_text(note_text)

    return note
