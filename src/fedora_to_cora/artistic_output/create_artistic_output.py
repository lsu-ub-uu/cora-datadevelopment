import xml.etree.ElementTree as ET


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
    source_strings = source_record.findall(f"./{source_tag}/entry/list/string")
    source_language = source_record.find(f"./{source_tag}/entry/language/languageCode3")

    if source_language is None or not source_language.text:
        raise ValueError(f"Language code must be present the {new_tag_name }")

    tags = []
    for i, source_string in enumerate(source_strings):
        new_tag = ET.Element(new_tag_name, lang=source_language.text)
        if source_string is not None and source_string.text:
            new_tag.text = source_string.text
            new_tag.set("repeatId", str(i))
            tags.append(new_tag)

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


def create_physical_desctiption(source_record: ET.Element) -> ET.Element:
    physical_description_source = source_record.find(
        "./mediaInformation/physicalDescriptions/abstract/text/p"
    )
    physical_description = ET.Element("physicalDescription")

    extent = ET.SubElement(physical_description, "extent")
    if physical_description_source is not None:
        extent.append(physical_description_source)
    return physical_description
