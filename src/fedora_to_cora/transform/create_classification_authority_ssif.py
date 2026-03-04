import xml.etree.ElementTree as ET

from common.xml_utils import create_text


def create_classification_authority_ssif(source_record):
    return [
        _create_classification_element(subject.text, i)
        for i, subject in enumerate(
            source_record.findall("./nationalCategories/subject/subjectCode")
        )
        if subject.text
    ]


def _create_classification_element(subject_code, repeat_id):
    return create_text(
        "classification",
        authority="ssif",
        repeatId=str(repeat_id),
        value=subject_code,
    )
