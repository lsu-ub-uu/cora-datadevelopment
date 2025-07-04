from fedora_to_cora.create_location import create_locations
from common.test_helper import assert_equal_for_xml_and_xml_string
import xml.etree.ElementTree as ET


def test_create_location():
    source_record = ET.fromstring(
        """
        <publication>
            <urls>
                <url>
                    <url>http://www.test.se</url>
                    <label>En URL</label>
                    <openAccess>true</openAccess>
                </url>
                <url>
                    <url>http://www.test2.se</url>
                    <label>En annan URL</label>
                    <openAccess>false</openAccess>
                    </url> 
            </urls>
        </publication>
        """
    )

    location = create_locations(source_record)

    assert_equal_for_xml_and_xml_string(
        location[0],
        """
        <location repeatId="0">
            <url>http://www.test.se</url>
            <displayLabel>En URL</displayLabel>
        </location>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        location[1],
        """
        <location repeatId="1">
            <url>http://www.test2.se</url>
            <displayLabel>En annan URL</displayLabel>
        </location>
        """,
    )


def test_create_location_without_display_label():
    source_record = ET.fromstring(
        """
        <publication>
            <urls>
                <url>
                    <url>http://www.test.se</url>
                </url>
            </urls>
        </publication>
        """
    )

    location = create_locations(source_record)

    assert_equal_for_xml_and_xml_string(
        location[0],
        """
        <location repeatId="0">
            <url>http://www.test.se</url>
        </location>
        """,
    )


def test_create_location_without_url():
    source_record = ET.fromstring(
        """
        <publication>
            <urls>
                <url>
                    <label>En URL utan URL</label>
                </url>
            </urls>
        </publication>
        """
    )

    location = create_locations(source_record)

    assert_equal_for_xml_and_xml_string(
        location[0],
        """
        <location repeatId="0">
            <displayLabel>En URL utan URL</displayLabel>
        </location>
        """,
    )
