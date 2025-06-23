from xml.etree import ElementTree as ET
from fedora_to_cora.create_subject import create_subject


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
    subject = create_subject(source_record)
    assert subject is not None
    assert subject.attrib["lang"] == "eng"


def test_create_subject_sets_topic_replaces_spaces_with_comma():
    subject = create_subject(source_record)
    assert subject is not None
    topic = subject.find("topic")
    assert topic is not None
    assert topic.text == "Sinologi, Arkeologi"


def test_handles_no_keywrods():
    source_record_no_keywords = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )
    subject = create_subject(source_record_no_keywords)
    assert subject is None
