import xml.etree.ElementTree as ET


def create_subjects(source_record: ET.Element) -> list[ET.Element]:
    keyword_entries = source_record.findall("./keyWords/entry")

    return [create_subject(entry, i) for (i, entry) in enumerate(keyword_entries)]


def create_subject(keyword_entry: ET.Element, repeat_id: int) -> ET.Element:
    language_code = keyword_entry.find("./language/languageCode3")
    topic = keyword_entry.find("./list/string")

    assert (
        language_code is not None and language_code.text is not None
    ), "keyWord languageCode3 is missing"
    assert (
        topic is not None and topic.text is not None
    ), "keyWord list/string is missing"

    subject = ET.Element("subject", lang=language_code.text, repeatId=str(repeat_id))
    ET.SubElement(subject, "topic").text = topic.text.replace(" ", ", ")

    return subject
