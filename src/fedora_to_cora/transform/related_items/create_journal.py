import xml.etree.ElementTree as ET
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link_using_name_type_id
from common.xml_utils import append_if_value, create_group, create_text
from fedora_to_cora.transform.identifiers.create_identifier import create_identifier
from cora.context import Context

DIVA_JOURNAL_RECORD_TYPE = "diva-journal"


def create_related_item_type_journal(
    source_record: ET.Element, context: Context
) -> ET.Element | None:

    journal = None

    journal_old_id = source_record.findtext("./journal/journalId")
    if journal_old_id is not None:
        journal = _create_controlled_journal(journal_old_id, context)

    uncontrolled_journal = source_record.find("./uncontrolledJournal")
    if uncontrolled_journal is not None:
        journal = _create_uncontrolled_journal(uncontrolled_journal)

    if journal is not None and len(journal) > 0:
        part = _create_part(source_record)
        append_if_value(journal, part)
        return journal

    return None


def _create_uncontrolled_journal(uncontrolled_journal: ET.Element) -> ET.Element | None:
    journal_name_uncontrolled = uncontrolled_journal.findtext(
        "./journalNameUncontrolled"
    )
    printed_issn = uncontrolled_journal.findtext("./printedIssn")
    electronic_issn = uncontrolled_journal.findtext("./electronicIssn")

    return create_group(
        "relatedItem",
        type="journal",
        otherType="text",
        children=[
            create_group(
                "titleInfo", [create_text("title", journal_name_uncontrolled)]
            ),
            create_text("identifier", printed_issn, type="issn", displayLabel="pissn"),
            create_text(
                "identifier", electronic_issn, type="issn", displayLabel="eissn"
            ),
        ],
    )


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


def _create_part(source_record: ET.Element) -> ET.Element | None:

    return create_group(
        "part",
        [
            create_group(
                "detail",
                type="volume",
                children=[
                    create_text("number", value=source_record.findtext("./volume"))
                ],
            ),
            create_group(
                "detail",
                type="issue",
                children=[
                    create_text("number", value=source_record.findtext("./issueNumber"))
                ],
            ),
            create_group(
                "detail",
                type="artNo",
                children=[
                    create_text("number", value=source_record.findtext("./articleId"))
                ],
            ),
            create_group(
                "extent",
                children=[
                    create_text("start", value=source_record.findtext("./startPage")),
                    create_text("end", value=source_record.findtext("./endPage")),
                ],
            ),
        ],
    )
