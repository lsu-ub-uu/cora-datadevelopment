import xml.etree.ElementTree as ET

from common.xml_utils import create_group, create_text
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
            new_tag = create_text(
                new_tag_name,
                string.text,
                repeatId=str(repeat_id),
                lang=language_code if language_code else "",
            )
            if new_tag is not None:
                tags.append(new_tag)
                repeat_id += 1

    return tags


def create_duration(source_record: ET.Element) -> ET.Element | None:
    duration_source = source_record.find("./mediaInformation/duration")
    if duration_source is None or not duration_source.text:
        return None

    hh, mm, ss = duration_source.text.split(":")
    return create_group(
        "duration",
        [
            create_text(
                "hh",
                hh,
            ),
            create_text(
                "mm",
                mm,
            ),
            create_text(
                "ss",
                ss,
            ),
        ],
    )


def create_note_type_context(source_record: ET.Element) -> list[ET.Element]:
    descriptions = source_record.findall("./descriptions/abstract")
    repeat_id = 0

    notes = []
    for description in descriptions:
        note = _create_note_from_abstract(description)
        if note is not None:
            note.set("repeatId", str(repeat_id))
            notes.append(note)
            repeat_id += 1

    return notes


def _create_note_from_abstract(
    abstract: ET.Element,
) -> ET.Element | None:
    language_code = abstract.findtext("./language/languageCode3")
    abstract_text = abstract.findtext("./text")

    if abstract_text is None or len(abstract_text) == 0:
        return None

    return create_text(
        "note",
        clean_rich_text(abstract_text),
        type="context",
        lang=language_code,
    )
