import xml.etree.ElementTree as ET
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link_using_name_type_id
from common.xml_utils import append_if_value
from fedora_to_cora.transform.identifiers.create_identifier import create_identifier
from cora.context import Context

DIVA_JOURNAL_RECORD_TYPE = "diva-journal"


def create_related_item_type_journal(
    source_record: ET.Element, context: Context
) -> list[ET.Element]:
    journals = []

    uncontrolled_journal = source_record.find("./uncontrolledJournal")
    if uncontrolled_journal is not None:
        journals.append(_create_uncontrolled_journal(uncontrolled_journal))

    journal_old_id = source_record.findtext("./journal/journalId")
    if journal_old_id is not None:
        journals.append(_create_controlled_journal(journal_old_id, context))

    return journals


def _create_uncontrolled_journal(uncontrolled_journal: ET.Element) -> ET.Element:
    related_item = ET.Element("relatedItem", type="journal", otherType="text")

    journal_name_uncontrolled = uncontrolled_journal.findtext(
        "./journalNameUncontrolled"
    )
    if journal_name_uncontrolled is not None:
        title_info = ET.Element("titleInfo")
        title_element = ET.SubElement(title_info, "title")
        title_element.text = journal_name_uncontrolled
        related_item.append(title_info)

    printed_issn = uncontrolled_journal.findtext("./printedIssn")
    if printed_issn is not None:
        pissn = ET.Element("identifier", type="issn", displayLabel="pissn")
        pissn.text = printed_issn
        related_item.append(pissn)

    electronic_issn = uncontrolled_journal.findtext("./electronicIssn")
    if electronic_issn is not None:
        eissn = ET.Element("identifier", type="issn", displayLabel="eissn")
        eissn.text = electronic_issn
        related_item.append(eissn)

    return related_item


def _create_controlled_journal(journal_old_id: str, context: Context) -> ET.Element:
    related_item = ET.Element("relatedItem", type="journal", otherType="link")

    cora_id = get_cora_id_by_old_id(
        journal_old_id, record_type=DIVA_JOURNAL_RECORD_TYPE, context=context
    )
    journal = create_record_link_using_name_type_id(
        name_in_data="journal",
        record_type=DIVA_JOURNAL_RECORD_TYPE,
        record_id=cora_id,
    )
    related_item.append(journal)

    return related_item
