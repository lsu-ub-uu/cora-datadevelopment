import xml.etree.ElementTree as ET
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link_using_name_type_id
from common.xml_utils import append_if_value
from fedora_to_cora.transform.identifiers.create_identifier import create_identifier
from cora.context import Context

DIVA_JOURNAL_RECORD_TYPE = "diva-journal"


def create_related_item_type_journal(
    source_record: ET.Element, context: Context
) -> ET.Element:
    related_item = ET.Element("relatedItem", type="journal")
    title_text = source_record.findtext("./journal/journalTitle/mainTitle")
    sub_title_text = source_record.findtext("./journal/journalTitle/subTitle")

    title_info = ET.Element("titleInfo")

    if title_text is not None:
        title_element = ET.SubElement(title_info, "title")
        title_element.text = title_text

    if sub_title_text is not None:
        sub_title_element = ET.SubElement(title_info, "subtitle")
        sub_title_element.text = sub_title_text
    append_if_value(related_item, title_info)

    journal_old_id = source_record.findtext("./journal/journalId")
    if journal_old_id is not None:
        cora_id = get_cora_id_by_old_id(
            journal_old_id, record_type=DIVA_JOURNAL_RECORD_TYPE, context=context
        )
        journal = create_record_link_using_name_type_id(
            name_in_data="journal",
            record_type=DIVA_JOURNAL_RECORD_TYPE,
            record_id=cora_id,
        )
        append_if_value(related_item, journal)

    _create_identifiers(source_record, related_item)

    return related_item


def _create_identifiers(
    source_record: ET.Element, related_item: ET.Element
) -> ET.Element | None:
    pissn = create_identifier(
        source_record=source_record,
        type="issn",
        source_selector="./journal/printedIssn",
    )
    pissn.set("displayLabel", "pissn")
    append_if_value(related_item, pissn)

    eissn = create_identifier(
        source_record=source_record,
        type="issn",
        source_selector="./journal/electronicIssn",
    )
    eissn.set("displayLabel", "eissn")
    append_if_value(related_item, eissn)
