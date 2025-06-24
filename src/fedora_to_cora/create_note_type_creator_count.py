import xml.etree.ElementTree as ET


def create_note_type_creator_count(source_record: ET.Element) -> ET.Element | None:
    """
    Create a note element for the number of contributors in the source record.

    Args:
        source_record (ET.Element): The source XML element containing publication data.

    Returns:
        ET.Element | None: A note element with type "creatorCount" if noOfContributors exists, otherwise None.
    """
    no_of_contributors = source_record.find("./noOfContributors")
    if no_of_contributors is not None and no_of_contributors.text:
        note = ET.Element("note", type="creatorCount")
        note.text = no_of_contributors.text.strip()
        return note
    return None
