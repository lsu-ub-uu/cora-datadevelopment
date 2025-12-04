import xml.etree.ElementTree as ET

from fedora_to_cora.clean_rich_text import clean_rich_text


def create_types(
    source_record: ET.Element,
) -> list[ET.Element]:
    return _create_tags(
        source_record,
        source_tag="./mediaInformation/types",
        new_tag_name="type",
    )


def create_materials(
    source_record: ET.Element,
) -> list[ET.Element]:
    return _create_tags(
        source_record,
        source_tag="./mediaInformation/materials",
        new_tag_name="material",
    )


def create_techniques(
    source_record: ET.Element,
) -> list[ET.Element]:
    return _create_tags(
        source_record,
        source_tag="./mediaInformation/techniques",
        new_tag_name="technique",
    )


def _create_tags(
    source_record: ET.Element, source_tag: str, new_tag_name: str
) -> list[ET.Element]:
    entries = source_record.findall(f"./{source_tag}/entry")
    tags = []
    repeat_id = 0
    for entry in entries:
        language_code = entry.findtext("./language/languageCode3")
        strings = entry.findall("./list/string")
        for string in strings:
            new_tag = ET.Element(
                new_tag_name, lang=language_code if language_code else ""
            )
            if string is not None and string.text:
                new_tag.text = string.text
                new_tag.set("repeatId", str(repeat_id))
                tags.append(new_tag)
                repeat_id += 1

    return tags


def create_size(source_record: ET.Element) -> ET.Element:
    size = source_record.find("./mediaInformation/size")
    return size if size is not None else ET.Element("size")


def create_duration(source_record: ET.Element) -> ET.Element:
    duration_source = source_record.find("./mediaInformation/duration")
    duration = ET.Element("duration")

    if duration_source is not None and duration_source.text:
        hh, mm, ss = duration_source.text.split(":")

        hh_element = ET.SubElement(duration, "hh")
        hh_element.text = hh

        mm_element = ET.SubElement(duration, "mm")
        mm_element.text = mm

        ss_element = ET.SubElement(duration, "ss")
        ss_element.text = ss

    return duration
