import xml.etree.ElementTree as ET


def create_academic_semester(source_record: ET.Element) -> ET.Element:
    """
    Create a academicSemester element with the given year and semester.
    """
    academic_semester = ET.Element("academicSemester")
    academic_semester_year = source_record.find("./academicTerm/year")
    academic_semester_academic_semester = source_record.findtext("./academicTerm/term")

    if academic_semester_year is not None:
        academic_semester.append(academic_semester_year)

    if academic_semester_academic_semester is not None:
        academic_semester_sub_element = ET.SubElement(
            academic_semester, "academicSemester"
        )
        academic_semester_sub_element.text = academic_semester_academic_semester.lower()

    return academic_semester
