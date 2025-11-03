import xml.etree.ElementTree as ET

from common.xml_utils import append_if_value
from fedora_to_cora.transform.identifiers.create_doi_se_libr import (
    create_identifier_doi,
)
from fedora_to_cora.transform.identifiers.create_isbn import create_identifier_type_isbn


def create_book(source_record: ET.Element) -> ET.Element | None:
    source_book_title = source_record.find("./bookTitle")
    language = source_record.findtext(
        "./originalPublicationTitle/language/languageCode3"
    )
    if source_book_title is None or language is None:
        return None

    related_item = ET.Element("relatedItem", type="book", otherType="text")
    title_info = ET.SubElement(related_item, "titleInfo", lang=language)
    title_text = source_book_title.findtext("./title")
    subtitle_text = source_book_title.findtext("./subTitle")
    ET.SubElement(title_info, "title").text = title_text

    if subtitle_text is not None:
        ET.SubElement(title_info, "subTitle").text = subtitle_text

    append_if_value(related_item, _create_statement_of_responsibility(source_record))

    # TODO How do we map ISBNs and DOIs?

    append_if_value(related_item, _create_part(source_record))

    return related_item


def _create_statement_of_responsibility(source_record: ET.Element) -> ET.Element | None:
    editor = source_record.findtext("./bookEditor")
    if editor is None:
        return None

    note = ET.Element("note", type="statementOfResponsibility")
    note.text = editor
    return note


def _create_part(source_record: ET.Element) -> ET.Element:
    part = ET.Element("part")

    extent = ET.Element("extent")

    start_page = source_record.findtext("./startPage")
    if start_page is not None:
        ET.SubElement(extent, "start").text = start_page

    end_page = source_record.findtext("./endPage")
    if end_page is not None:
        ET.SubElement(extent, "end").text = end_page

    append_if_value(part, extent)

    return part
