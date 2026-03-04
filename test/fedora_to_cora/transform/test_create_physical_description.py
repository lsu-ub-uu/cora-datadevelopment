import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.create_physical_description import (
    create_physical_description,
)


def test_create_physical_description_from_pages():
    source_record = ET.fromstring(
        """
        <publication>
            <pages>208</pages>
        </publication>
        """
    )

    physical_description = create_physical_description(source_record)

    assert_equal_for_xml_and_xml_string(
        physical_description,
        """
        <physicalDescription>
            <extent unit="pages">208</extent>
        </physicalDescription>
        """,
    )


def test_create_physical_description_empty_pages():
    source_record = ET.fromstring(
        """
        <publication>
            <pages />
        </publication>
        """
    )

    physical_description = create_physical_description(source_record)

    assert physical_description is None


def test_create_physical_description_empty_data():
    source_record = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )

    physical_description = create_physical_description(source_record)

    assert physical_description is None


def test_create_physical_description_from_media_information():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
                <physicalDescriptions>
                    <abstract>
                        <text>&lt;p&gt;Fysisk beskrivning Fysisk beskrivning &lt;em&gt;Fysisk beskrivning&lt;/em&gt;&lt;/p&gt;</text>
                    </abstract>
                </physicalDescriptions>
            </mediaInformation>
        </publication>
        """
    )

    description = create_physical_description(source_record)

    assert_equal_for_xml_and_xml_string(
        description,
        """
        <physicalDescription>
            <extent unit="other">
                Fysisk beskrivning Fysisk beskrivning Fysisk beskrivning
            </extent>
        </physicalDescription>
        """,
    )


def test_create_physical_description_from_media_information_multiple():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
                <physicalDescriptions>
                    <abstract>
                        <text>123</text>
                    </abstract>
                    <abstract>
                        <text>456</text>
                    </abstract>
                </physicalDescriptions>
            </mediaInformation>
        </publication>
        """
    )

    description = create_physical_description(source_record)

    assert_equal_for_xml_and_xml_string(
        description,
        """
        <physicalDescription>
            <extent unit="other">
                123, 456
            </extent>
        </physicalDescription>
        """,
    )


def test_create_physical_description_from_media_information_and_pages():
    source_record = ET.fromstring(
        """
        <publication>
            <pages>208</pages>
            <mediaInformation>
                <physicalDescriptions>
                    <abstract>
                        <text>&lt;p&gt;Fysisk beskrivning Fysisk beskrivning &lt;em&gt;Fysisk beskrivning&lt;/em&gt;&lt;/p&gt;</text>
                    </abstract>
                </physicalDescriptions>
            </mediaInformation>
        </publication>
        """
    )

    description = create_physical_description(source_record)

    assert_equal_for_xml_and_xml_string(
        description,
        """
        <physicalDescription>
            <extent unit="pages">208</extent>
            <extent unit="other">
                Fysisk beskrivning Fysisk beskrivning Fysisk beskrivning
            </extent>
        </physicalDescription>
        """,
    )


def test_create_physical_description_empty_media_information():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
            </mediaInformation>
        </publication>
        """
    )

    description = create_physical_description(source_record)

    assert description is None
