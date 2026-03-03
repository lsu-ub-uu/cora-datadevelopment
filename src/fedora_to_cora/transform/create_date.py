from xml.etree import ElementTree as ET

from common.xml_utils import create_group, create_text


def create_date(
    date_source: str | None, tag_name: str, **attribs: str | None
) -> ET.Element | None:
    if (date_source is None) or (date_source.strip() == ""):
        return None
    date_part = date_source.split("T")[0]
    year, month, day = date_part.split("-")
    return create_group(
        tag_name,
        [
            create_text("year", year),
            create_text("month", month),
            create_text("day", day),
        ],
        **attribs,
    )
