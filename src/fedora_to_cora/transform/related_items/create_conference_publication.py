import xml.etree.ElementTree as ET

from common.xml_utils import append_if_value
from fedora_to_cora.transform.identifiers.create_doi_se_libr import (
    create_identifier_doi,
)
from fedora_to_cora.transform.identifiers.create_isbn import create_identifier_type_isbn
from fedora_to_cora.transform.related_items.create_series import (
    create_related_item_type_series,
)
from cora.context import Context


def create_related_item_type_conference_publication(
    source_record: ET.Element, context: Context
) -> ET.Element | None:
    related_item = ET.Element(
        "relatedItem", type="conferencePublication", otherType="text"
    )

    append_if_value(related_item, _create_title_info(source_record))
    append_if_value(related_item, _create_statement_of_responsibility(source_record))
    append_if_value(related_item, _create_part(source_record))
    append_if_value(related_item, create_identifier_type_isbn(source_record))
    append_if_value(related_item, create_identifier_doi(source_record))
    append_if_value(
        related_item, create_related_item_type_series(source_record, context)
    )

    return related_item


def _create_title_info(source_record: ET.Element) -> ET.Element | None:
    proceedings_title = source_record.find("./proceedingsTitle")

    if proceedings_title is None:
        return None

    title_info = ET.Element("titleInfo")

    source_title = proceedings_title.findtext("./title")
    if source_title:
        ET.SubElement(title_info, "title").text = source_title

    source_subtitle = proceedings_title.findtext("./subTitle")
    if source_subtitle:
        ET.SubElement(title_info, "subtitle").text = source_subtitle

    return title_info


def _create_statement_of_responsibility(source_record: ET.Element) -> ET.Element | None:
    editor = source_record.findtext("./proceedingsEditor")
    if editor is None:
        return None

    note = ET.Element("note", type="statementOfResponsibility")
    note.text = editor
    return note


def _create_part(source_record: ET.Element) -> ET.Element:
    part = ET.Element("part")

    source_volume = source_record.findtext("./volume")
    if source_volume is not None:
        volume = ET.SubElement(part, "detail", type="volume")
        ET.SubElement(volume, "number").text = source_volume

    source_issue = source_record.findtext("./issueNumber")
    if source_issue is not None:
        issue = ET.SubElement(part, "detail", type="issue")
        ET.SubElement(issue, "number").text = source_issue

    source_article_id = source_record.findtext("./articleId")
    if source_article_id is not None:
        art_no = ET.SubElement(part, "detail", type="artNo")
        ET.SubElement(art_no, "number").text = source_article_id

    extent = ET.Element("extent")

    start_page = source_record.findtext("./startPage")
    if start_page is not None:
        ET.SubElement(extent, "start").text = start_page

    end_page = source_record.findtext("./endPage")
    if end_page is not None:
        ET.SubElement(extent, "end").text = end_page
    append_if_value(part, extent)

    return part
