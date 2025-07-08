import xml.etree.ElementTree as ET
from fedora_to_cora.related_items.create_journal import create_related_item_type_journal
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext

def test_create_related_item_type_journal_with_title():
    mock_context = MockContext()

    source_record = ET.fromstring(
        """
        <publication>
            <journal>
                <journalTitle>
                    <titleId>1082</titleId>
                    <mainTitle>Design, Automation and Test in Europe</mainTitle>
                    <subTitle>Journal of Testing</subTitle>
                    <locale>und</locale>
                </journalTitle>
                <openAccess>false</openAccess>
            </journal>
        </publication>
        """
    )

    related_item = create_related_item_type_journal(source_record, mock_context)

    assert_equal_for_xml_and_xml_string(
        related_item,
        """
        <relatedItem type="journal">
            <titleInfo>
                <title>Design, Automation and Test in Europe</title>
                <subTitle>Journal of Testing</subTitle>
            </titleInfo>
        </relatedItem>
        """,
    )

def test_create_related_item_type_journal_with_identifiers():
    mock_context = MockContext()

    source_record = ET.fromstring(
        """
        <publication>
            <journal>
                <printedIssn>1530-1591</printedIssn>
                <electronicIssn>1558-1101</electronicIssn>
                <openAccess>false</openAccess>
            </journal>
        </publication>
        """
    )

    related_item = create_related_item_type_journal(source_record, mock_context)

    assert_equal_for_xml_and_xml_string(
        related_item,
        """
        <relatedItem type="journal">
            <identifier type="issn" displayLabel="pissn">
                1530-1591
            </identifier>
            <identifier type="issn" displayLabel="eissn">
                1558-1101
            </identifier>
        </relatedItem>
        """,
    )

def test_create_related_item_type_journal_with_linked_journal(monkeypatch):
    journal_old_id = "985"
    journal_cora_id = "diva-journal:21849327760208536"
    
    mock_context = MockContext()

    def mock_get_id(old_id, *args, **kwargs):
        if old_id == journal_old_id:
            return journal_cora_id
        else:
            return None

    monkeypatch.setattr(
        "fedora_to_cora.related_items.create_journal.get_cora_id_by_old_id",
        mock_get_id,
    )


    source_record = ET.fromstring(
        f"""
        <publication>
            <journal>
                <journalId>{journal_old_id}</journalId>
            </journal>
        </publication>
        """
    )

    related_item = create_related_item_type_journal(source_record, mock_context)

    assert_equal_for_xml_and_xml_string(
        related_item,
        f"""
        <relatedItem type="journal">
            <journal>
                <linkedRecordType>diva-journal</linkedRecordType>
                <linkedRecordId>{journal_cora_id}</linkedRecordId>
            </journal>
        </relatedItem>
        """,
    )
    # <part>
    #     <detail type="volume">
    #         <number>
    #             /.+/
    #         </number>
    #     </detail>
    #     <detail type="issue">
    #         <number>
    #             /.+/
    #         </number>
    #     </detail>
    #     <detail type="artNo">
    #         <number>
    #             /.+/
    #         </number>
    #     </detail>
    #         <extent>
    #             <start>
    #                  /.+/
    #             </start>
    #             <end>
    #                 /.+/
    #             </end>
    #         </extent>
    #     </part>


