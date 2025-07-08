import xml.etree.ElementTree as ET


def create_classification_authority_ssif(source_record):
    return [
        _create_classification_element(subject.text, i)
        for i, subject in enumerate(
            source_record.findall("./nationalCategories/subject/subjectCode")
        )
        if subject.text
    ]


def _create_classification_element(subject_code, repeat_id):
    classification = ET.Element(
        "classification", authority="ssif", repeatId=str(repeat_id)
    )
    classification.text = subject_code
    return classification
