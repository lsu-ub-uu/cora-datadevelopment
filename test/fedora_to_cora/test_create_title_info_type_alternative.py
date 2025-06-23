from xml.etree import ElementTree as ET
from fedora_to_cora.create_title_info import (
    create_title_info_type_alternative,
)
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_title_info_type_alternative():
    source_record = ET.fromstring(
        """
        <publication>
            <alternativePublicationTitles>
                <title>
                    <title>Alternative Title</title>
                    <language>
                        <languageCode3>eng</languageCode3>
                        <languageCode2>en</languageCode2>
                        <showsOnList>true</showsOnList>
                    </language>
                </title>
            </alternativePublicationTitles>
        </publication>
        """
    )
    alternative_titles = create_title_info_type_alternative(source_record)

    assert_equal_for_xml_and_xml_string(
        alternative_titles[0],
        """
        <titleInfo type="alternative" lang="eng" repeatId="0">
            <title>Alternative Title</title>
        </titleInfo>
        """,
    )


def test_create_title_info_type_alternative_with_subtitle():
    source_record = ET.fromstring(
        """
        <publication>
            <alternativePublicationTitles>
                <title>
                    <title>Alternative Title</title>
                    <subTitle>A subtitle</subTitle>
                    <language>
                        <languageCode3>eng</languageCode3>
                        <languageCode2>en</languageCode2>
                        <showsOnList>true</showsOnList>
                    </language>
                </title>
            </alternativePublicationTitles>
        </publication>
        """
    )

    alternative_titles = create_title_info_type_alternative(source_record)

    assert_equal_for_xml_and_xml_string(
        alternative_titles[0],
        """
        <titleInfo type="alternative" lang="eng" repeatId="0">
            <title>Alternative Title</title>
            <subTitle>A subtitle</subTitle>
        </titleInfo>
        """,
    )


def test_create_multiple_alternative_titles():
    source_record = ET.fromstring(
        """
        <publication>
            <alternativePublicationTitles>
                <title>
                    <title>Alternative Title 1</title>
                    <language>
                        <languageCode3>eng</languageCode3>
                        <languageCode2>en</languageCode2>
                        <showsOnList>true</showsOnList>
                    </language>
                </title>
                <title>
                    <title>Alternative Title 2</title>
                    <language>
                        <languageCode3>swe</languageCode3>
                        <languageCode2>sv</languageCode2>
                        <showsOnList>true</showsOnList>
                    </language>
                </title>
            </alternativePublicationTitles>
        </publication>
        """
    )

    alternative_titles = create_title_info_type_alternative(source_record)

    assert isinstance(alternative_titles, list)
    assert len(alternative_titles) == 2

    assert_equal_for_xml_and_xml_string(
        alternative_titles[0],
        """
        <titleInfo type="alternative" lang="eng" repeatId="0">
            <title>Alternative Title 1</title>
        </titleInfo>
        """,
    )

    assert_equal_for_xml_and_xml_string(
        alternative_titles[1],
        """
        <titleInfo type="alternative" lang="swe" repeatId="1">
            <title>Alternative Title 2</title>
        </titleInfo>
        """,
    )
