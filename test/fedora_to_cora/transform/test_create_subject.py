from xml.etree import ElementTree as ET
from fedora_to_cora.transform.create_subject import create_subjects
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
                    <string>Sinologi</string>
                    <string>Arkeologi</string>
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
            <topic>Sinologi</topic>
        </subject>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        subject[1],
        """
        <subject lang="eng" repeatId="1">
            <topic>Arkeologi</topic>
        </subject>
        """,
    )

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
                    <string>enKeyword1</string>
                    <string>enKeyword2</string>
                </list>
            </entry>
            <entry>
                <language>
                    <languageCode3>swe</languageCode3>
                </language>
                <list>
                    <string>svKeyword3</string>
                    <string>svKeyword4</string>
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
            <topic>enKeyword1</topic>
        </subject>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        subjects[1],
        """
        <subject lang="eng" repeatId="1">
            <topic>enKeyword2</topic>
        </subject>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        subjects[2],
        """
        <subject lang="swe" repeatId="2">
            <topic>svKeyword3</topic>
        </subject>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        subjects[3],
        """
        <subject lang="swe" repeatId="3">
            <topic>svKeyword4</topic>
        </subject>
        """,
    )
