import xml.etree.ElementTree as ET
from common.xml_utils import append_if_value


def create_academic_semester(source_record: ET.Element) -> ET.Element:
    """
    Create a academicSemester element with the given year and semester.
    """
    academic_semester = ET.Element("academicSemester")
    academic_semester_year = source_record.findtext("./academicTerm/year")
    academic_semester_academic_semester = source_record.findtext("./academicTerm/term")

    if academic_semester_year is not None:
        year = ET.Element("year")
        year.text = academic_semester_year
        append_if_value(academic_semester, year)

    if academic_semester_academic_semester is not None:
        academic_semester_sub_element = ET.SubElement(
            academic_semester, "academicSemester"
        )
        academic_semester_sub_element.text = academic_semester_academic_semester.lower()

    return academic_semester
