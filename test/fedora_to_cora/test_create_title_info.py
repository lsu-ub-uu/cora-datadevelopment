import pytest
from xml.etree import ElementTree as ET
from fedora_to_cora.create_title_info import create_title_info


source_record = ET.fromstring(
    """
    <publication>
        <originalPublicationTitle>
            <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
            <subTitle></subTitle>
            <language>
                <languageCode3>eng</languageCode3>
                <languageCode2>en</languageCode2>
                <languageNames>
                    <languageName>
                    <languageNameId>1145</languageNameId>
                    <locale>en</locale>
                    <languageName>English</languageName>
                    </languageName>
                    <languageName>
                    <languageNameId>10120</languageNameId>
                    <locale>no</locale>
                    <languageName>engelsk</languageName>
                    </languageName>
                    <languageName>
                    <languageNameId>1144</languageNameId>
                    <locale>sv</locale>
                    <languageName>Engelska</languageName>
                    </languageName>
                </languageNames>
                <showsOnList>true</showsOnList>
            </language>
        </originalPublicationTitle>
    </publication>
"""
)


def test_create_title_info():
    title_info = create_title_info(source_record)
    assert title_info.tag == "titleInfo"
    assert title_info.attrib["lang"] == "eng"

    title = title_info.find("title")
    assert title is not None
    assert title.text == "Bulletin of the Museum of Far Eastern Antiquities (BMFEA)"
    assert title_info.find("subTitle") is None


def test_create_title_info_with_subtitle():
    source_record_with_subtitle = ET.fromstring(
        """
        <publication>
            <originalPublicationTitle>
                <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
                <subTitle>subtitle</subTitle>
                <language><languageCode3>eng</languageCode3></language>
            </originalPublicationTitle>
        </publication>
    """
    )

    title_info = create_title_info(source_record_with_subtitle)
    assert title_info.tag == "titleInfo"
    assert title_info.attrib["lang"] == "eng"

    title = title_info.find("title")
    assert title is not None
    assert title.text == "Bulletin of the Museum of Far Eastern Antiquities (BMFEA)"
    sub_title = title_info.find("subTitle")
    assert sub_title is not None
    assert sub_title.text == "subtitle"


def test_create_title_info_raises_error_on_missing_title():
    source_record_with_subtitle = ET.fromstring(
        """
        <publication>
            <originalPublicationTitle>
                <language><languageCode3>eng</languageCode3></language>
            </originalPublicationTitle>
        </publication>
    """
    )

    pytest.raises(AssertionError, create_title_info, source_record_with_subtitle)


def test_create_title_info_raises_error_on_missing_language_code3():
    source_record_with_subtitle = ET.fromstring(
        """
        <publication>
            <originalPublicationTitle>
                <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
            </originalPublicationTitle>
        </publication>
    """
    )

    pytest.raises(AssertionError, create_title_info, source_record_with_subtitle)
