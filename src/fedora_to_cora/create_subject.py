import xml.etree.ElementTree as ET


def create_subject(source_record: ET.Element) -> ET.Element:
    language_code, topic = _validate(source_record)

    subject = ET.Element("subject", lang=language_code)
    ET.SubElement(subject, "topic").text = topic.replace(" ", ", ")

    return subject


def _validate(source_record: ET.Element):
    languageCode = source_record.find("./keyWords/entry/language/languageCode3")
    topic = source_record.find("./keyWords/entry/list/string")
    assert (
        languageCode is not None and languageCode.text is not None
    ), "originalPublicationTitle/language/languageCode3 must be present in source_record"
    assert (
        topic is not None and topic.text is not None
    ), "topic must be present in source_record"

    return (languageCode.text, topic.text)
