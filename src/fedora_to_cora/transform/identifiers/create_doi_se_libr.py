import xml.etree.ElementTree as ET


def create_identifier_doi(source_record):
    entries = source_record.findall("./identifiers/entry")
    for entry in entries:
        if _is_entry_of_type(entry, "doi"):
            return _create_identifier(
                value=entry.findtext("./publicationIdentifier/value"),
                id_type="doi",
            )


def create_identifier_se_libr(source_record):
    entries = source_record.findall("./identifiers/entry")
    return [
        _create_identifier(
            value=entry.findtext("./publicationIdentifier/value"),
            id_type="se-libr",
            repeat_id=str(index),
        )
        for (index, entry) in enumerate(entries)
        if _is_entry_of_type(entry, "libris")
    ]


def _create_identifier(
    value: str, id_type: str, repeat_id: str | None = None
) -> ET.Element:
    identifier = ET.Element("identifier", type=id_type)
    if repeat_id is not None:
        identifier.set("repeatId", repeat_id)
    identifier.text = value
    return identifier


def _is_entry_of_type(entry: ET.Element, id_type: str) -> bool:
    return (
        entry.findtext("publicationIdentifierType") == id_type
        and entry.findtext("./publicationIdentifier/value") is not None
    )
