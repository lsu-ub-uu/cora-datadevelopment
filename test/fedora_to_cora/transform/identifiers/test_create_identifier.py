import xml.etree.ElementTree as ET
from fedora_to_cora.transform.identifiers.create_identifier import create_identifier
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_identifier():
    source_record = ET.fromstring(
        """
        <publication>
            <someOldIdentifier>Arkivnummer.01</someOldIdentifier>
        </publication>
        """
    )

    identifier = create_identifier(
        source_record, source_selector="./someOldIdentifier", type="someNewIdentifier"
    )

    assert_equal_for_xml_and_xml_string(
        identifier[0],
        """
        <identifier type="someNewIdentifier">Arkivnummer.01</identifier>
        """,
    )


def test_create_identifier_with_default_selector():
    source_record = ET.fromstring(
        """
        <publication>
            <archiveNumber>Arkivnummer.01</archiveNumber>
        </publication>
        """
    )

    identifier = create_identifier(source_record, type="archiveNumber")

    assert_equal_for_xml_and_xml_string(
        identifier[0],
        """
        <identifier type="archiveNumber">Arkivnummer.01</identifier>
        """,
    )


def test_create_identifier_with_empty_tag():
    source_record = ET.fromstring(
        """
        <publication>
            <archiveNumber></archiveNumber>
        </publication>
        """
    )

    identifier = create_identifier(
        source_record, source_selector="./archiveNumber", type="archiveNumber"
    )

    assert_equal_for_xml_and_xml_string(
        identifier[0],
        """
        <identifier type="archiveNumber" />
        """,
    )


def test_create_identifier_for_local_id():
    source_record = ET.fromstring(
        """
        <publication>
            <localId>Local.12345</localId>
            <localId>Local.67890</localId>
        </publication>
        """
    )

    identifier = create_identifier(
        source_record, source_selector="./localId", type="localId"
    )

    assert_equal_for_xml_and_xml_string(
        identifier[0],
        """
        <identifier type="localId" repeatId="0">Local.12345</identifier>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        identifier[1],
        """
        <identifier type="localId" repeatId="1">Local.67890</identifier>
        """,
    )
