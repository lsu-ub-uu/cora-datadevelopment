import xml.etree.ElementTree as ET

VALIDATION_TYPE_PREFIX = "classic_"


def transform_output_to_classic_quality(
    cora_output: ET.Element, validation_errors: list[str] | None
):
    classic_quality_output = ET.fromstring(ET.tostring(cora_output))

    _update_validation_type(classic_quality_output)
    _update_data_quality(classic_quality_output)
    _add_validation_errors_to_internal_note(classic_quality_output, validation_errors)

    return classic_quality_output


def _update_validation_type(classic_quality_output: ET.Element):
    validation_type_link = classic_quality_output.find(
        "./recordInfo/validationType/linkedRecordId"
    )
    assert validation_type_link is not None and validation_type_link.text is not None
    validation_type_link.text = VALIDATION_TYPE_PREFIX + validation_type_link.text


def _update_data_quality(classic_quality_output: ET.Element):
    data_quality = classic_quality_output.find("./dataQuality")
    assert data_quality is not None
    data_quality.text = "classic"

def _add_validation_errors_to_internal_note(
    classic_quality_output: ET.Element, validation_errors: list[str] | None
):
    if not validation_errors or len(validation_errors) == 0:
        return None

    existing_admin_info = classic_quality_output.find("./adminInfo")
    if existing_admin_info is None:
        admin_info = ET.Element("adminInfo")
        classic_quality_output.append(admin_info)
    else:
        admin_info = existing_admin_info

    existing_internal_note = admin_info.find("./note[@type='internal']")

    validation_error_text = (
        'Record created with dataQuality "classic" due to validation errors during migration from DiVA Classic. Validation errors:- '
        + "- ".join(validation_errors)
    )

    if existing_internal_note is not None:
        note_element = existing_internal_note
        note_element.text = (note_element.text or "") + validation_error_text
    else:
        note_element = ET.Element("note", type="internal")
        admin_info.append(note_element)
        note_element.text = validation_error_text
