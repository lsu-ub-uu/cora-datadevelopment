import xml.etree.ElementTree as ET

import pytest
from fedora_to_cora.transform.related_items.create_journal import (
    create_related_item_type_journal,
)
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext


def test_create_related_item_type_journal_with_title():
    mock_context = MockContext()

    source_record = ET.fromstring(
        """
        <publication>
            <uncontrolledJournal>
                <journalNameUncontrolled>
                    Design, Automation and Test in Europe
                </journalNameUncontrolled>
                <openAccess>false</openAccess>
            </uncontrolledJournal>
        </publication>
        """
    )

    journal = create_related_item_type_journal(source_record, mock_context)

    assert_equal_for_xml_and_xml_string(
        journal,
        """
        <relatedItem type="journal" otherType="text">
            <titleInfo>
                <title>Design, Automation and Test in Europe</title>
            </titleInfo>
        </relatedItem>
        """,
    )


def test_create_related_item_type_journal_with_identifiers():
    mock_context = MockContext()

    source_record = ET.fromstring(
        """
        <publication>
            <uncontrolledJournal>
                <printedIssn>1530-1591</printedIssn>
                <electronicIssn>1558-1101</electronicIssn>
                <openAccess>false</openAccess>
            </uncontrolledJournal>
        </publication>
        """
    )

    journal = create_related_item_type_journal(source_record, mock_context)

    assert_equal_for_xml_and_xml_string(
        journal,
        """
        <relatedItem type="journal" otherType="text">
            <identifier type="issn" displayLabel="pissn">
                1530-1591
            </identifier>
            <identifier type="issn" displayLabel="eissn">
                1558-1101
            </identifier>
        </relatedItem>
        """,
    )


def test_create_related_item_type_journal_with_part():
    mock_context = MockContext()

    source_record = ET.fromstring(
        """
        <publication>
            <uncontrolledJournal>
                <journalNameUncontrolled>
                    Design, Automation and Test in Europe
                </journalNameUncontrolled>
            </uncontrolledJournal>
            <volume>2021</volume>
            <issueNumber>4</issueNumber>
            <articleId>123456</articleId>
            <startPage>100</startPage>
            <endPage>110</endPage>
        </publication>
        """
    )

    journal = create_related_item_type_journal(source_record, mock_context)

    assert_equal_for_xml_and_xml_string(
        journal,
        """
        <relatedItem type="journal" otherType="text">
            <titleInfo>
                <title>Design, Automation and Test in Europe</title>
            </titleInfo>
            <part>
                <detail type="volume">
                    <number>2021</number>
                </detail>
                <detail type="issue">
                    <number>4</number>
                </detail>
                <detail type="artNo">
                    <number>123456</number>
                </detail>
                <extent>
                    <start>100</start>
                    <end>110</end>
                </extent>
            </part>
        </relatedItem>
        """,
    )


def test_create_related_item_type_journal_with_part_without_extent():
    mock_context = MockContext()

    source_record = ET.fromstring(
        """
        <publication>
            <uncontrolledJournal>
                <journalNameUncontrolled>
                    Design, Automation and Test in Europe
                </journalNameUncontrolled>
            </uncontrolledJournal>
            <volume>2021</volume>
            <issueNumber>4</issueNumber>
            <articleId>123456</articleId>
        </publication>
        """
    )

    journal = create_related_item_type_journal(source_record, mock_context)

    assert_equal_for_xml_and_xml_string(
        journal,
        """
        <relatedItem type="journal" otherType="text">
            <titleInfo>
                <title>Design, Automation and Test in Europe</title>
            </titleInfo>
            <part>
                <detail type="volume">
                    <number>2021</number>
                </detail>
                <detail type="issue">
                    <number>4</number>
                </detail>
                <detail type="artNo">
                    <number>123456</number>
                </detail>
            </part>
        </relatedItem>
        """,
    )


def test_create_controlled_journal(monkeypatch):
    journal_old_id = "985"
    journal_cora_id = "diva-journal:21849327760208536"

    mock_context = MockContext()

    def mock_get_id(old_id, *args, **kwargs):
        if old_id == journal_old_id:
            return journal_cora_id
        else:
            return None

    monkeypatch.setattr(
        "fedora_to_cora.transform.related_items.create_journal.get_cora_id_by_old_id",
        mock_get_id,
    )

    source_record = ET.fromstring(
        f"""
        <publication>
            <journal>
                <journalId>{journal_old_id}</journalId>
            </journal>
            <volume>2021</volume>
            <issueNumber>4</issueNumber>
            <articleId>123456</articleId>
            <startPage>100</startPage>
            <endPage>110</endPage>
        </publication>
        """
    )

    journal = create_related_item_type_journal(source_record, mock_context)

    assert_equal_for_xml_and_xml_string(
        journal,
        f"""
        <relatedItem type="journal" otherType="link">
            <journal>
                <linkedRecordType>diva-journal</linkedRecordType>
                <linkedRecordId>{journal_cora_id}</linkedRecordId>
            </journal>
             <part>
                <detail type="volume">
                    <number>2021</number>
                </detail>
                <detail type="issue">
                    <number>4</number>
                </detail>
                <detail type="artNo">
                    <number>123456</number>
                </detail>
                <extent>
                    <start>100</start>
                    <end>110</end>
                </extent>
            </part>
        </relatedItem>
        """,
    )


def test_create_controlled_journal_with_part(monkeypatch):
    journal_old_id = "985"
    journal_cora_id = "diva-journal:21849327760208536"

    mock_context = MockContext()

    def mock_get_id(old_id, *args, **kwargs):
        if old_id == journal_old_id:
            return journal_cora_id
        else:
            return None

    monkeypatch.setattr(
        "fedora_to_cora.transform.related_items.create_journal.get_cora_id_by_old_id",
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

    journal = create_related_item_type_journal(source_record, mock_context)

    assert_equal_for_xml_and_xml_string(
        journal,
        f"""
        <relatedItem type="journal" otherType="link">
            <journal>
                <linkedRecordType>diva-journal</linkedRecordType>
                <linkedRecordId>{journal_cora_id}</linkedRecordId>
            </journal>
        </relatedItem>
        """,
    )


def test_empty_uncontrolled_journal():
    mock_context = MockContext()

    source_record = ET.fromstring(
        """
        <publication>
            <uncontrolledJournal>
                <controlled>false</controlled>
                <openAccess>false</openAccess>
                <subjects />
                <relationships />
            </uncontrolledJournal>
        </publication>
        """
    )

    journal = create_related_item_type_journal(source_record, mock_context)
    assert journal is None


def test_create_uncontrolled_and_controlled_journal(monkeypatch):
    journal_old_id = "985"
    journal_cora_id = "diva-journal:21849327760208536"

    mock_context = MockContext()

    def mock_get_id(old_id, *args, **kwargs):
        if old_id == journal_old_id:
            return journal_cora_id
        else:
            return None

    monkeypatch.setattr(
        "fedora_to_cora.transform.related_items.create_journal.get_cora_id_by_old_id",
        mock_get_id,
    )

    source_record = ET.fromstring(
        """
        <publication>
            <journal>
                <journalId>{journal_old_id}</journalId>
            </journal>
            <uncontrolledJournal>
                <printedIssn>1530-1591</printedIssn>
                <controlled>false</controlled>
                <openAccess>false</openAccess>
                <subjects />
                <relationships />
            </uncontrolledJournal>
            <part>
                <detail type="volume">
                    <number>2021</number>
                </detail>
                <detail type="issue">
                    <number>4</number>
                </detail>
                <detail type="artNo">
                    <number>123456</number>
                </detail>
                <extent>
                    <start>100</start>
                    <end>110</end>
                </extent>
            </part>
        </publication>
        """
    )

    with pytest.raises(
        ValueError,
        match="Record has both controlled and uncontrolled journal.",
    ):
        create_related_item_type_journal(source_record, mock_context)
