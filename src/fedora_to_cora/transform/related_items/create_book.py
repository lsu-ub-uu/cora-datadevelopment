import xml.etree.ElementTree as ET
from cora.context import Context
from common.xml_utils import append_if_value, create_group, create_text
from fedora_to_cora.transform.identifiers.create_doi_se_libr import (
    create_identifier_doi,
    create_identifier_se_libr,
)
from fedora_to_cora.transform.identifiers.create_isbn import create_identifier_type_isbn
from fedora_to_cora.transform.related_items.create_series import (
    create_related_item_type_series,
)
from fedora_to_cora.clean_rich_text import clean_rich_text


def create_book(source_record: ET.Element, context: Context) -> ET.Element | None:
    source_book_title = source_record.find("./bookTitle")

    if source_book_title is None or source_book_title.text is None:
        return None

    related_item = create_group(
        "relatedItem",
        [
            _create_title_info(source_record),
            _create_statement_of_responsibility(source_record),
            create_identifier_type_isbn(source_record),
            create_identifier_doi(source_record),
            create_identifier_se_libr(source_record),
            _create_part(source_record),
            create_related_item_type_series(source_record, context),
        ],
        type="book",
        otherType="text",
    )
    return related_item


def _create_title_info(source_record: ET.Element) -> ET.Element | None:
    return create_group(
        "titleInfo",
        [
            create_text(
                "title", clean_rich_text(source_record.findtext("./bookTitle/title"))
            ),
            create_text(
                "subtitle",
                clean_rich_text(source_record.findtext("./bookTitle/subTitle")),
            ),
        ],
    )


def _create_statement_of_responsibility(source_record: ET.Element) -> ET.Element | None:
    editor = source_record.findtext("./bookEditor")
    if editor is None:
        return None

    note = ET.Element("note", type="statementOfResponsibility")
    note.text = editor
    return note


def _create_part(source_record: ET.Element) -> ET.Element | None:
    return create_group(
        "part",
        [
            create_group(
                "extent",
                [
                    create_text("start", source_record.findtext("./startPage")),
                    create_text("end", source_record.findtext("./endPage")),
                ],
            )
        ],
    )
