import xml.etree.ElementTree as ET
import pytest

from fedora_to_cora.artistic_output.create_artistic_output import (
    create_physical_desctiption,
    create_duration,
    create_size,
    create_techniques,
    create_materials,
    create_types,
)
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_artistic_output_with_type():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
                <types class="hashtable">
                    <entry>
                        <language>
                            <languageCode3>swe</languageCode3>
                        </language>
                        <list>
                            <string>Typ01</string>
                            <string>Typ02</string>
                        </list>
                    </entry>
                </types>
            </mediaInformation>
        </publication>
        """
    )

    type = create_types(source_record)

    assert_equal_for_xml_and_xml_string(
        type[0],
        """
        <type lang="swe" repeatId="0">
            Typ01
        </type>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        type[1],
        """
        <type lang="swe" repeatId="1">
            Typ02
        </type>
        """,
    )


def test_create_artistic_output_with_material():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
                <materials class="hashtable">
                    <entry>
                        <language>
                            <languageCode3>swe</languageCode3>
                        </language>
                        <list>
                            <string>Material01</string>
                            <string>Material02</string>
                        </list>
                    </entry>
                </materials>
            </mediaInformation>
        </publication>
        """
    )

    material = create_materials(source_record)

    assert_equal_for_xml_and_xml_string(
        material[0],
        """
        <material lang="swe" repeatId="0">
            Material01
        </material>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        material[1],
        """
        <material lang="swe" repeatId="1">
            Material02
        </material>
        """,
    )


def test_create_artistic_output_with_technique():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
                <techniques class="hashtable">
                    <entry>
                        <language>
                            <languageCode3>swe</languageCode3>
                        </language>
                        <list>
                            <string>Teknik01</string>
                            <string>Teknik02</string>
                        </list>
                    </entry>
                </techniques>
            </mediaInformation>
        </publication>
        """
    )

    technique = create_techniques(source_record)

    assert_equal_for_xml_and_xml_string(
        technique[0],
        """
        <technique lang="swe" repeatId="0">
            Teknik01
        </technique>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        technique[1],
        """
        <technique lang="swe" repeatId="1">
            Teknik02
        </technique>
        """,
    )


def test_create_artistic_output_with_size():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
                <size>22*32 km2</size>
            </mediaInformation>
        </publication>
        """
    )

    size = create_size(source_record)

    assert_equal_for_xml_and_xml_string(
        size,
        """
        <size>
            22*32 km2
        </size>
        """,
    )


def test_create_artistic_output_with_no_size():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
            </mediaInformation>
        </publication>
        """
    )

    size = create_size(source_record)

    assert_equal_for_xml_and_xml_string(
        size,
        """
        <size></size>
        """,
    )


def test_create_artistic_output_with_duration():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
                <duration>01:10:00</duration>
            </mediaInformation>
        </publication>
        """
    )

    duration = create_duration(source_record)

    assert_equal_for_xml_and_xml_string(
        duration,
        """
        <duration>
            <hh>01</hh>
            <mm>10</mm>
            <ss>00</ss>
        </duration>
        """,
    )


def test_create_artistic_output_with_physical_description():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
                <physicalDescriptions>
                    <abstract>
                        <text>
                            <p>Fysisk beskrivning Fysisk beskrivning <em>Fysisk beskrivning</em></p>
                        </text>
                    </abstract>
                </physicalDescriptions>
            </mediaInformation>
        </publication>
        """
    )

    description = create_physical_desctiption(source_record)

    assert_equal_for_xml_and_xml_string(
        description,
        """
        <physicalDescription>
            <extent>
                <p>Fysisk beskrivning Fysisk beskrivning <em>Fysisk beskrivning</em></p>
            </extent>
        </physicalDescription>
        """,
    )


def test_create_artistic_output_without_language():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
                <types class="hashtable">
                    <entry>
                        <list>
                            <string>Typ01</string>
                            <string>Typ02</string>
                        </list>
                    </entry>
                </types>
            </mediaInformation>
        </publication>
        """
    )

    with pytest.raises(ValueError):
        create_types(source_record)
