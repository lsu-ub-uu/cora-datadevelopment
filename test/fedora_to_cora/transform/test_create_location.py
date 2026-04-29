from fedora_to_cora.transform.create_location import (
    create_location_display_label_order_link,
    create_locations,
)
from common.test_helper import assert_equal_for_xml_and_xml_string
import xml.etree.ElementTree as ET


def test_create_location():
    source_record = ET.fromstring("""
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
        """)

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
    source_record = ET.fromstring("""
        <publication>
            <urls>
                <url>
                    <url>http://www.test.se</url>
                </url>
            </urls>
        </publication>
        """)

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
    source_record = ET.fromstring("""
        <publication>
            <urls>
                <url>
                    <label>En URL utan URL</label>
                </url>
            </urls>
        </publication>
        """)

    location = create_locations(source_record)

    assert_equal_for_xml_and_xml_string(
        location[0],
        """
        <location repeatId="0">
            <displayLabel>En URL utan URL</displayLabel>
        </location>
        """,
    )


def test_create_order_link():
    source_record = ET.fromstring("""
        <publication>
            <publicationOrder>
                <orderProfileId>OrderProfile-2</orderProfileId>
                <orderURL>http://order.test.se</orderURL>
                <orderLink>true</orderLink>
                <validFrom>2013-05-14T15:20:53.957+02:00</validFrom>
                <parameters />
            </publicationOrder>
        </publication>
        """)

    location = create_location_display_label_order_link(source_record)

    assert_equal_for_xml_and_xml_string(
        location,
        """
        <location displayLabel="orderLink" repeatId="0">
            <url>http://order.test.se</url>
            <displayLabel>Beställ/Order</displayLabel>
        </location>
        """,
    )


def test_create_order_link_no_order_url():
    source_record = ET.fromstring("""
        <publication>
            <publicationOrder>
                <orderProfileId>OrderProfile-2</orderProfileId>
                <orderLink>true</orderLink>
                <validFrom>2013-05-14T15:20:53.957+02:00</validFrom>
                <parameters />
            </publicationOrder>
        </publication>
        """)

    location = create_location_display_label_order_link(source_record)

    assert location is None


def test_create_order_link_empty_order_url():
    source_record = ET.fromstring("""
        <publication>
            <publicationOrder>
                <orderProfileId>OrderProfile-2</orderProfileId>
                <orderURL/>
                <orderLink>true</orderLink>
                <validFrom>2013-05-14T15:20:53.957+02:00</validFrom>
                <parameters />
            </publicationOrder>
        </publication>
        """)

    location = create_location_display_label_order_link(source_record)

    assert location is None
