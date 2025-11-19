import xml.etree.ElementTree as ET

from fedora_to_cora.transform.identifiers.create_doi_se_libr import (
    create_identifier_doi,
    create_identifier_se_libr,
)
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
                <publicationIdentifierType>doi</publicationIdentifierType>
                <publicationIdentifier>
                    <value>10.1038/s41698-022-00278-5</value>
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
            <entry>
                <publicationIdentifierType>libris</publicationIdentifierType>
                <publicationIdentifier>
                    <value>0006</value>
                    <alternativeValues>
                        <value>
                            <content>0007</content>
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
        libris[0],
        """<identifier type="se-libr" repeatId="0">0004</identifier>""",
    )


def test_create_identifier_se_libr_when_missing():
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
                </identifiers>
            </publication>
        """
    )
    libris = create_identifier_se_libr(source_record)
    assert len(libris) == 0


def test_create_multiple_identifier_se_libr():
    libris_identifiers = create_identifier_se_libr(source_record)
    assert len(libris_identifiers) == 4
    assert_equal_for_xml_and_xml_string(
        libris_identifiers[0],
        """<identifier type="se-libr" repeatId="0">0004</identifier>""",
    )
    assert_equal_for_xml_and_xml_string(
        libris_identifiers[1],
        """<identifier type="se-libr" repeatId="1">0005</identifier>""",
    )
    assert_equal_for_xml_and_xml_string(
        libris_identifiers[2],
        """<identifier type="se-libr" repeatId="2">0006</identifier>""",
    )
    assert_equal_for_xml_and_xml_string(
        libris_identifiers[3],
        """<identifier type="se-libr" repeatId="3">0007</identifier>""",
    )


def test_create_identifier_doi_when_missing():
    source_record = ET.fromstring(
        """
            <publication>
                <identifiers>
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
    doi_identifier = create_identifier_doi(source_record)
    assert doi_identifier is None
