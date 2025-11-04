import xml.etree.ElementTree as ET

def get_language_code(entry: ET.Element) -> str | None:
    language_code = entry.find("./language/languageCode3")
    return language_code.text if language_code is not None else None

def get_topic_strings(entry: ET.Element) -> list[str]:
    return [string.text for string in entry.findall("./list/string") if string is not None and string.text is not None]

def create_subject(language: str, topic: str, repeat_id: int) -> ET.Element:
    subject = ET.Element("subject", lang=language, repeatId=str(repeat_id))
    ET.SubElement(subject, "topic").text = topic
    return subject

def create_subjects(source_record: ET.Element) -> list[ET.Element]:
    keyword_entries = source_record.findall("./keyWords/entry")
    subjects = [
        create_subject(language, topic, repeat_id)
        for repeat_id, (language, topic) in enumerate(
            (
                (get_language_code(entry), topic)
                for entry in keyword_entries
                for topic in get_topic_strings(entry)
            )
        )
        if language is not None
    ]
    return subjects
