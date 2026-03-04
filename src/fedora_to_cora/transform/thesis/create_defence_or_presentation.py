import xml.etree.ElementTree as ET

from common.xml_utils import append_if_value, create_group, create_text
from fedora_to_cora.transform.get_validation_type import (
    get_validation_type_from_fedora_record,
)


def create_defence_or_presentation(source_record: ET.Element) -> ET.Element | None:
    tag_name = "presentation" if _is_degree_project(source_record) else "defence"
    return create_group(
        tag_name,
        children=[
            _create_language(source_record),
            _create_duration(source_record),
            _create_address(source_record),
        ],
    )


def _is_degree_project(source_record: ET.Element) -> bool:
    return (
        get_validation_type_from_fedora_record(source_record) == "diva_degree-project"
    )


def _create_address(source_record: ET.Element):
    return create_group(
        "address",
        children=[
            create_text("location", source_record.findtext("./defence/room/name")),
            create_text("street", source_record.findtext("./defence/room/street")),
            create_text("city", source_record.findtext("./defence/room/city")),
        ],
    )


def _create_language(source_record: ET.Element):
    return create_group(
        "language",
        children=[
            create_text(
                "languageTerm",
                type="code",
                authority="iso639-2b",
                value=source_record.findtext("./defence/language/languageCode3"),
            )
        ],
    )


def _create_duration(source_record: ET.Element):
    duration_source = source_record.findtext("./defence/date")

    if duration_source is None:
        return None

    date_part, time_part = duration_source.split("T")
    year, month, day = date_part.split("-")
    time_part = time_part.split("+")[0]  # Remove timezone offset
    hh, mm, _ = time_part.split(":")

    return create_group(
        "dateOther",
        type="presentation",
        children=[
            create_text("year", year),
            create_text("month", month),
            create_text("day", day),
            create_text("hh", hh),
            create_text("mm", mm),
        ],
    )
