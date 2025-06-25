import xml.etree.ElementTree as ET

from fedora_to_cora import create_identifier_doi, create_identifier_se_libr
from common.test_helper import assert_equal_for_xml_and_xml_string

source_record = ET.fromstring(
    """
    <publication>
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
    </publication>
"""
)


def test_create_identifier_doi():
    doi = create_identifier_doi(source_record)
    assert_equal_for_xml_and_xml_string(
        doi,
        """<identifier type="doi">10.1038/s41698-022-00278-4</identifier>""",
    )


def test_create_identifier_se_libr():
    libris = create_identifier_se_libr(source_record)
    assert_equal_for_xml_and_xml_string(
        libris,
        """<identifier type="se-libris">0004</identifier>""",
    )
