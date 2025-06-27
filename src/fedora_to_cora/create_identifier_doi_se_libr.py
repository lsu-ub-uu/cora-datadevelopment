import xml.etree.ElementTree as ET


def create_identifier_doi(source_record):
    """
    Create a DOI identifier element from the source record.
    """
    return _create_identifier_doi_se_libr(source_record, "doi")


def create_identifier_se_libr(source_record):
    """
    Create a DOI identifier element from the source record.
    """
    return _create_identifier_doi_se_libr(source_record, "libris")


def _create_identifier_doi_se_libr(
    source_record: ET.Element, identifier_type: str
) -> ET.Element:
    """
    Create a DOI or SE Libris identifier element from the source record.
    """
    identifier = ET.Element(
        "identifier", type=_convert_libris_to_se_libr(identifier_type)
    )
    entries = source_record.findall("identifiers/entry")

    for entry in entries:
        id_type = entry.find("publicationIdentifierType")
        id_value = entry.find("publicationIdentifier/value")

        if (
            id_type is not None
            and id_value is not None
            and id_type.text == identifier_type
        ):
            identifier.text = id_value.text
            break

    return identifier


def _convert_libris_to_se_libr(value: str) -> str:
    """
    Convert a Libris identifier to a SE Libris identifier.
    """
    if value == "libris":
        return "se-libr"
    return value
