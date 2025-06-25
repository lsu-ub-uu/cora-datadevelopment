from xml.etree import ElementTree as ET
from fedora_to_cora import create_subjects
from common.test_helper import assert_equal_for_xml_and_xml_string


source_record = ET.fromstring(
    """
    <publication>
        <keyWords class="hashtable">
            <entry>
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
            <list>
                <string>Sinologi Arkeologi</string>
            </list>
            </entry>
        </keyWords>
    </publication>
"""
)


def test_create_subject_sets_language():
    subject = create_subjects(source_record)

    assert_equal_for_xml_and_xml_string(
        subject[0],
        """
        <subject lang="eng" repeatId="0">
            <topic>Sinologi, Arkeologi</topic>
        </subject>
        """,
    )


def test_create_subject_sets_topic_replaces_spaces_with_comma():
    subjects = create_subjects(source_record)
    topic = subjects[0].find("topic")
    assert topic is not None
    assert topic.text == "Sinologi, Arkeologi"


def test_handles_no_keywords():
    source_record_no_keywords = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )
    subjects = create_subjects(source_record_no_keywords)
    assert subjects == []


def test_create_subject_sets_topic_with_multiple_languages():
    source_record_multi_lang = ET.fromstring(
        """
    <publication>
        <keyWords class="hashtable">
            <entry>
            <language>
                <languageCode3>eng</languageCode3>
            </language>
            <list>
                <string>enKeyword1 enKeyword2</string>
            </list>
            </entry>
            <entry>
            <language>
                <languageCode3>swe</languageCode3>
            </language>
            <list>
                <string>svKeyword3 svKeyword4</string>
            </list>
            </entry>
        </keyWords>
    </publication>
    """
    )

    subjects = create_subjects(source_record_multi_lang)
    assert_equal_for_xml_and_xml_string(
        subjects[0],
        """
        <subject lang="eng" repeatId="0">
            <topic>enKeyword1, enKeyword2</topic>
        </subject>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        subjects[1],
        """
        <subject lang="swe" repeatId="1">
            <topic>svKeyword3, svKeyword4</topic>
        </subject>
        """,
    )
