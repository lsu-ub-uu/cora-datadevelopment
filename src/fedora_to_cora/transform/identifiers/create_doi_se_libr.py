import xml.etree.ElementTree as ET


def create_identifier_doi(source_record):
    entries = source_record.findall("./identifiers/entry")
    for entry in entries:
        if _is_entry_of_type(entry, "doi"):
            return _create_identifier(
                value=entry.findtext("./publicationIdentifier/value"),
                id_type="doi",
            )


def create_identifier_se_libr(source_record: ET.Element):
    entries = source_record.findall("./identifiers/entry")

    def extract_values_from_entry(entry: ET.Element) -> list[str]:
        """Extract all libris identifier values from an entry."""
        value = entry.findtext("./publicationIdentifier/value")

        values = [value] if value is not None else []

        alt_values = entry.findall("./publicationIdentifier/alternativeValues/value")
        values.extend(
            content
            for alt_value in alt_values
            if (content := alt_value.findtext("./content")) is not None
        )

        return values

    all_values = [
        value
        for entry in entries
        if _is_entry_of_type(entry, "libris")
        for value in extract_values_from_entry(entry)
    ]

    return [
        _create_identifier(value=value, id_type="se-libr", repeat_id=str(index))
        for index, value in enumerate(all_values)
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
