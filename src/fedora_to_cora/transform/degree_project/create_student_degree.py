import xml.etree.ElementTree as ET
from cora.context import Context
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link
from common.xml_utils import create_group, create_text


def create_student_degrees(
    source_record: ET.Element, context: Context
) -> list[ET.Element | None]:
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
):
    return create_group(
        "studentDegree",
        children=[
            create_text(
                "degreeLevel",
                source_student_degree.findtext("./thesisLevel/thesisLevelCode"),
            ),
            create_text(
                "universityPoints",
                source_student_degree.findtext("./universityPoints/hp"),
            ),
            _create_course(source_student_degree, context),
            _create_programme(source_student_degree, context),
        ],
        repeatId=str(repeat_id),
    )


def _create_course(
    source_student_degree: ET.Element, context: Context
) -> ET.Element | None:
    course_old_id = source_student_degree.findtext("./undergraduateSubject/subjectId")
    if course_old_id:
        cora_id = get_cora_id_by_old_id(
            context=context,
            old_id=course_old_id,
            record_type="diva-course",
        )
        return create_record_link(
            "course",
            "diva-course",
            cora_id,
        )


def _create_programme(
    source_student_degree: ET.Element, context: Context
) -> ET.Element | None:
    programme_old_id = source_student_degree.findtext(
        "./educationalProgramme/subjectId"
    )
    if programme_old_id:
        cora_id = get_cora_id_by_old_id(
            context=context,
            old_id=programme_old_id,
            record_type="diva-programme",
        )
        return create_record_link(
            "programme",
            "diva-programme",
            cora_id,
        )
