import xml.etree.ElementTree as ET
from common.xml_utils import append_if_value, create_group, create_text


def create_academic_semester(source_record: ET.Element) -> ET.Element | None:
    """
    Create a academicSemester element with the given year and semester.
    """
    academic_term = source_record.findtext("./academicTerm/term")
    return create_group(
        "academicSemester",
        [
            create_text("year", source_record.findtext("./academicTerm/year")),
            create_text(
                "academicSemester",
                academic_term.lower() if academic_term is not None else None,
            ),
        ],
    )
