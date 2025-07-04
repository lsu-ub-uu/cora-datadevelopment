import xml.etree.ElementTree as ET
from cora.context import Context
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link_using_name_type_id


def create_student_degrees(
    source_record: ET.Element, context: Context
) -> list[ET.Element]:
    """
    Create a student degree element from the source record.
    """
    source_student_degrees = source_record.findall("./studentDegrees/studentDegree")
    return [
        _create_student_degree(sd, repeat_id, context)
        for repeat_id, sd in enumerate(source_student_degrees)
    ]


def _create_student_degree(
    source_student_degree: ET.Element, repeat_id: int, context: Context
) -> ET.Element:
    student_degree = ET.Element("studentDegree", repeatId=str(repeat_id))

    thesis_level = source_student_degree.findtext("./thesisLevel/thesisLevelCode")
    if thesis_level:
        degree_level = ET.SubElement(student_degree, "degreeLevel")
        degree_level.text = thesis_level

    university_points = source_student_degree.findtext("./universityPoints/hp")
    if university_points:
        points = ET.SubElement(student_degree, "universityPoints")
        points.text = university_points

    # TODO Linked course
    course_old_id = source_student_degree.findtext("./undergraduateSubject/subjectId")
    if course_old_id:
        cora_id = get_cora_id_by_old_id(
            context=context,
            old_id=course_old_id,
            record_type="diva-course",
        )
        student_degree.append(
            create_record_link_using_name_type_id(
                "course",
                "diva-course",
                cora_id,
            )
        )

    # TODO Linked programme

    return student_degree
