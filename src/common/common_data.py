import xml.etree.ElementTree as ET

from common.xml_utils import create_group, create_text


def read_source_xml(filePath_sourceXml) -> ET.Element:
    sourceFile_xml = ET.parse(filePath_sourceXml)
    root = sourceFile_xml.getroot()
    return root


def create_title_info(title: str, subtitle: str | None) -> ET.Element | None:
    return create_group(
        "titleInfo",
        children=[create_text("title", title), create_text("subtitle", subtitle)],
    )


def create_title_info_type_alternative(
    title: str, subtitle: str | None
) -> ET.Element | None:
    return create_group(
        "titleInfo",
        children=[create_text("title", title), create_text("subtitle", subtitle)],
        type="alternative",
    )


def create_identifiers_from_source_with_repeat_id(
    identifier: str, identifier_type: str, identifier_repeat_id: dict
) -> ET.Element:
    identifier_element = create_identifiers_from_source(identifier, identifier_type)
    identifier_element.set("displayLabel", identifier_type)
    identifier_element.set("repeatId", str(identifier_repeat_id["repeatId"]))
    identifier_repeat_id["repeatId"] = identifier_repeat_id["repeatId"] + 1
    identifier_element.set("type", "issn")
    return identifier_element


def create_identifiers_from_source_with_type_issn(
    identifier: str, identifier_type: str
) -> ET.Element:
    identifier_element = create_identifiers_from_source(identifier, identifier_type)
    identifier_element.set("displayLabel", identifier_type)
    identifier_element.set("type", "issn")
    return identifier_element


def create_identifiers_from_source(identifier: str, identifier_type: str) -> ET.Element:
    id = create_text("identifier", type=identifier_type, value=identifier)
    assert id is not None
    return id


def create_origin_info(date: str, origin_type: str):
    year, month, day = map(str.strip, date.split("-"))
    return create_group(
        origin_type,
        children=[
            create_group(
                "dateIssued",
                point="end",
                children=[
                    create_text("year", year),
                    create_text("month", month),
                    create_text("day", day),
                ],
            )
        ],
    )


def create_location(url: str) -> ET.Element | None:
    return create_group("location", children=[create_text("url", url)])


def create_note(note: str, note_type: str) -> ET.Element | None:
    return create_text("note", note, type=note_type)


def create_record_link(
    name_in_data: str, record_type: str, record_id: str
) -> ET.Element | None:
    return create_group(
        name_in_data,
        children=[
            create_text("linkedRecordType", record_type),
            create_text("linkedRecordId", record_id),
        ],
    )


def name_type_corporate_create(name: str) -> ET.Element | None:
    return create_group(
        "name", children=[create_text("namePart", name)], type="corporate"
    )


def create_end_date(date: str) -> ET.Element | None:
    year, month, day = map(str.strip, date.split("-"))
    return create_group(
        "endDate",
        children=[
            create_text("year", year),
            create_text("month", month),
            create_text("day", day),
        ],
    )


def create_genre(publication_type: str, repeat_id: str):
    return create_text(
        "genre",
        value=publication_map[publication_type],
        repeatId=repeat_id,
        type="outputType",
    )


publication_map = {
    "50": "publication_journal-article",
    "51": "publication_review-article",
    "52": "publication_book-review",
    "53": "publication_doctoral-thesis-compilation",
    "54": "publication_doctoral-thesis-monograph",
    "55": "publication_licentiate-thesis-compilation",
    "56": "publication_licentiate-thesis-monograph",
    "57": "publication_book",
    "58": "publication_book-chapter",
    "59": "conference_paper",
    "60": "conference_proceeding",
    "61": "intellectual-property_patent",
    "62": "publication_report",
    "63": "publication_edited-book",
    "64": "publicationPreprintItem",
    "65": "diva_degree-project",
    "66": "publication_other",
    "67": "diva_dissertation",
    "71": "artistic-work_original-creative-work",
}
