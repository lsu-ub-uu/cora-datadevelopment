import xml.etree.ElementTree as ET
import pytest

from fedora_to_cora.transform.artistic_output.create_artistic_output import (
    create_duration,
    create_size,
    create_techniques,
    create_materials,
    create_types,
)
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_types():
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


def test_multiple_languages():
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
                            <string>Swe01</string>
                            <string>Swe02</string>
                        </list>
                    </entry>
                    <entry>
                        <language>
                            <languageCode3>eng</languageCode3>
                        </language>
                        <list>
                            <string>Eng01</string>
                            <string>Eng02</string>
                        </list>
                    </entry>
                </types>
            </mediaInformation>
        </publication>
        """
    )

    types = create_types(source_record)

    assert len(types) == 4

    assert_equal_for_xml_and_xml_string(
        types[0],
        """
        <type lang="swe" repeatId="0">
            Swe01
        </type>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        types[1],
        """
        <type lang="swe" repeatId="1">
            Swe02
        </type>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        types[2],
        """
        <type lang="eng" repeatId="2">
            Eng01
        </type>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        types[3],
        """
        <type lang="eng" repeatId="3">
            Eng02
        </type>
        """,
    )


def test_create_types_without_language():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
                <types class="hashtable">
                    <entry>
                        <list>
                            <string>Typ01</string>
                        </list>
                    </entry>
                </types>
            </mediaInformation>
        </publication>
        """
    )

    types = create_types(source_record)

    assert_equal_for_xml_and_xml_string(
        types[0],
        """
        <type lang="" repeatId="0">
            Typ01
        </type>
        """,
    )


def test_create_types_empty_media_information():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
            </mediaInformation>
        </publication>
        """
    )

    types = create_types(source_record)

    assert len(types) == 0


def test_create_types_missing_media_information():
    source_record = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )

    types = create_types(source_record)

    assert len(types) == 0


def test_create_materials():
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


def test_create_materials_empty_media_information():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
            </mediaInformation>
        </publication>
        """
    )

    materials = create_materials(source_record)

    assert len(materials) == 0


def test_create_materials_missing_media_information():
    source_record = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )

    materials = create_materials(source_record)

    assert len(materials) == 0


def test_create_techniques():
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


def test_create_techniques_empty_media_information():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
            </mediaInformation>
        </publication>
        """
    )

    techniques = create_techniques(source_record)

    assert len(techniques) == 0


def test_create_techniques_missing_media_information():
    source_record = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )

    techniques = create_techniques(source_record)

    assert len(techniques) == 0


def test_create_size():
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


def test_create_size_empty_media_information():
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


def test_create_size_missing_media_information():
    source_record = ET.fromstring(
        """
        <publication>
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


def test_create_duration():
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


def test_create_duration_empty_media_information():
    source_record = ET.fromstring(
        """
        <publication>
            <mediaInformation>
            </mediaInformation>
        </publication>
        """
    )

    duration = create_duration(source_record)

    assert_equal_for_xml_and_xml_string(
        duration,
        """
        <duration></duration>
        """,
    )


def test_create_duration_missing_media_information():
    source_record = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )

    duration = create_duration(source_record)

    assert_equal_for_xml_and_xml_string(
        duration,
        """
        <duration></duration>
        """,
    )
