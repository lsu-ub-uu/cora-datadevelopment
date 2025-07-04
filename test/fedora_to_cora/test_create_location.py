from fedora_to_cora.create_location import create_location
from common.test_helper import assert_equal_for_xml_and_xml_string
import xml.etree.ElementTree as ET


def test_create_location():
    source_record = ET.fromstring(
        """
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
        """
    )

    location = create_location(source_record)

    assert_equal_for_xml_and_xml_string(
        location[0],
        """
        <location>
            <url>http://www.test.se</url>
            <displayLabel>En URL</displayLabel>
        </location>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        location[1],
        """
        <location>
            <url>http://www.test2.se</url>
            <displayLabel>En annan URL</displayLabel>
        </location>
        """,
    )
