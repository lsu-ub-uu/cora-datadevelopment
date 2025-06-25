from xml.etree import ElementTree as ET
from fedora_to_cora.create_identifier_type_isbn import create_identifier_type_isbn
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_identifier_type_isbn():
    source_record = ET.fromstring(
        """
        <publication>
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
        </publication>
        """
    )

    identifiers = create_identifier_type_isbn(source_record)

    assert_equal_for_xml_and_xml_string(
        identifiers[0],
        """
        <identifier type="isbn" displayLabel="print" repeatId="0">978-91-506-2649-0</identifier>
        """,
    )

    assert_equal_for_xml_and_xml_string(
        identifiers[1],
        """
        <identifier type="isbn" displayLabel="online" repeatId="1">978-92-893-7379-1</identifier>
        """,
    )

    assert_equal_for_xml_and_xml_string(
        identifiers[2],
        """
        <identifier type="isbn" displayLabel="undefined" repeatId="2">978-92-893-7380-7</identifier>
        """,
    )
