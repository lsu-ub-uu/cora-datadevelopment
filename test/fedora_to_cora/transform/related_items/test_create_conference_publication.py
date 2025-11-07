import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
from fedora_to_cora.transform.related_items.create_conference_publication import (
    create_related_item_type_conference_publication,
)
from unittest.mock import MagicMock


def test_complete_conference_minimal():
    source_record = ET.fromstring(
        """
        <publication>
            <proceedingsTitle>
                <title>Proceedings of the International Conference on Testing</title>
                <subTitle>Advances in Testing Methodologies</subTitle>
            </proceedingsTitle>
        </publication>
        """
    )

    conference = create_related_item_type_conference_publication(
        source_record, MockContext()
    )

    assert_equal_for_xml_and_xml_string(
        conference,
        """
        <relatedItem type="conferencePublication" otherType="text">
            <titleInfo>
                <title>Proceedings of the International Conference on Testing</title>
                <subtitle>Advances in Testing Methodologies</subtitle>
            </titleInfo>
        </relatedItem>   
        """,
    )


def test_complete_conference_maximal(monkeypatch):
    get_cora_id_by_old_id_mock = MagicMock(return_value="diva-series:12345")
    monkeypatch.setattr(
        "fedora_to_cora.transform.related_items.create_series.get_cora_id_by_old_id",
        get_cora_id_by_old_id_mock,
    )

    source_record = ET.fromstring(
        """
        <publication>
            <conference>En fiktiv konferens</conference>
            <proceedingsTitle>
                <title>Proceedings of the International Conference on Testing</title>
                <subTitle>Advances in Testing Methodologies</subTitle>
            </proceedingsTitle>
            <proceedingsEditor>Dr. Test Example</proceedingsEditor>
            <startPage>10</startPage>
            <endPage>30</endPage>
            <volume>12</volume>   
            <articleId>123456</articleId>
            <issueNumber>5</issueNumber>
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
                <series>
                    <seriesId>12345</seriesId>
                </series>
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

    conference = create_related_item_type_conference_publication(
        source_record, MockContext()
    )

    assert_equal_for_xml_and_xml_string(
        conference,
        """
        <relatedItem type="conferencePublication" otherType="text">
            <titleInfo>
                <title>Proceedings of the International Conference on Testing</title>
                <subtitle>Advances in Testing Methodologies</subtitle>
            </titleInfo>
            <note type="statementOfResponsibility">Dr. Test Example</note>
            <part>
                <detail type="volume"><number>12</number></detail>
                <detail type="issue"><number>5</number></detail>
                <detail type="artNo"><number>123456</number></detail>
                <extent>
                    <start>10</start>
                    <end>30</end>
                </extent>
            </part>
            <identifier type="isbn" repeatId="0" displayLabel="print">978-91-506-2649-0</identifier>
            <identifier type="isbn" repeatId="1" displayLabel="online">978-92-893-7379-1</identifier>
            <identifier type="isbn" repeatId="2" displayLabel="undefined">978-92-893-7380-7</identifier>
            <identifier type="doi">10.1038/s41698-022-00278-4</identifier>
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
