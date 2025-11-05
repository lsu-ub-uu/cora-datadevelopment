import xml.etree.ElementTree as ET
from unittest.mock import MagicMock
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.related_items.create_book import create_book
from cora.context import MockContext


def test_create_minimal_book():
    source_record = ET.fromstring(
        """
        <publication>
            <originalPublicationTitle>
                <title>En titel</title>
                <subTitle>En undertitel</subTitle>
                <language>
                    <languageCode3>swe</languageCode3>
                </language>
            </originalPublicationTitle>
            <bookTitle>
                <title>En boktitel</title>
            </bookTitle>

        </publication>
        """
    )
    result = create_book(source_record, MockContext())
    assert_equal_for_xml_and_xml_string(
        result,
        """
        <relatedItem type="book" otherType="text">
            <titleInfo lang="swe"><title>En boktitel</title></titleInfo>
        </relatedItem>
    """,
    )


def test_create_maximal_book(monkeypatch):

    get_cora_id_by_old_id_mock = MagicMock(return_value="diva-series:12345")
    monkeypatch.setattr(
        "fedora_to_cora.transform.related_items.create_series.get_cora_id_by_old_id",
        get_cora_id_by_old_id_mock,
    )

    source_record = ET.fromstring(
        """
        <publication>
            <originalPublicationTitle>
                <title>En titel</title>
                <subTitle>En undertitel</subTitle>
                <language>
                    <languageCode3>swe</languageCode3>
                </language>
            </originalPublicationTitle>
            <bookTitle>
                <title>En boktitel</title>
                <subTitle>En bokundertitel</subTitle>
            </bookTitle>
            <bookEditor>En redaktör</bookEditor>
            <startPage>10</startPage>
            <endPage>30</endPage>   
            <isbnNumbers>
                <isbn>
                    <number>978-91-506-2649-0</number>
                    <type>print</type>
                </isbn>
                <isbn>
                    <number>978-92-893-7379-1</number>
                    <type>electronic</type>
                </isbn>
                <isbn>
                    <number>978-92-893-7380-7</number>
                </isbn>
            </isbnNumbers>
            <identifiers>
                <entry>
                    <publicationIdentifierType>doi</publicationIdentifierType>
                    <publicationIdentifier>
                        <value>10.1038/s41698-022-00278-4</value>
                        <type>doi</type>
                        <openAccess>true</openAccess>
                    </publicationIdentifier>
                </entry>
                <entry>
                    <publicationIdentifierType>libris</publicationIdentifierType>
                    <publicationIdentifier>
                        <value>0004</value>
                        <alternativeValues>
                        <value>
                            <content>0005</content>
                        </value>
                        </alternativeValues>
                        <type>libris</type>
                        <openAccess>false</openAccess>
                    </publicationIdentifier>
                </entry>
            </identifiers>
            <seriesInfos>
                <seriesInfo>
                    <series>
                       <seriesId>12345</seriesId>
                    </series>
                    <numberInSeries>66</numberInSeries>
                </seriesInfo>
            </seriesInfos>
        </publication>
        """
    )
    result = create_book(source_record, MockContext())
    assert_equal_for_xml_and_xml_string(
        result,
        """
        <relatedItem type="book" otherType="text">
            <titleInfo lang="swe">
                <title>En boktitel</title>
                <subTitle>En bokundertitel</subTitle>
            </titleInfo>
            <note type="statementOfResponsibility">En redaktör</note>
            <part>
                <extent>
                    <start>10</start>
                    <end>30</end>
                </extent>
            </part>
            <relatedItem type="series" otherType="link" repeatId="controlled0">
                <series>
                    <linkedRecordType>diva-series</linkedRecordType>
                    <linkedRecordId>diva-series:12345</linkedRecordId>
                </series>
                <partNumber>66</partNumber>
            </relatedItem>
        </relatedItem>
    """,
    )


def test_returns_none_if_no_book_title():
    source_record = ET.fromstring(
        """
        <publication>
            <originalPublicationTitle>
                <title>En titel</title>
                <subTitle>En undertitel</subTitle>
                <language>
                    <languageCode3>swe</languageCode3>
                </language>
            </originalPublicationTitle>
            <startPage>10</startPage>
            <endPage>30</endPage>
        </publication>
        """
    )
    result = create_book(source_record, MockContext())
    assert result is None
