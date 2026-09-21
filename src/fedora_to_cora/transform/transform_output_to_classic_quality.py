import xml.etree.ElementTree as ET

VALIDATION_TYPE_PREFIX = "classic_"


def transform_output_to_classic_quality(
    cora_output: ET.Element, validation_errors: list[str] | None
):
    classic_quality_output = ET.fromstring(ET.tostring(cora_output))

    _update_validation_type(classic_quality_output)
    _update_data_quality(classic_quality_output)
    _handle_known_errors(classic_quality_output, validation_errors)
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

    validation_error_text = (
        'Record created with dataQuality "classic" due to validation errors during migration from DiVA Classic. Validation errors:- '
        + "- ".join(validation_errors)
    )

    _add_internal_note(classic_quality_output, validation_error_text)


def _add_internal_note(classic_quality_output: ET.Element, note_text: str):
    existing_admin_info = classic_quality_output.find("./adminInfo")
    if existing_admin_info is None:
        admin_info = ET.Element("adminInfo")
        classic_quality_output.append(admin_info)
    else:
        admin_info = existing_admin_info

    existing_internal_note = admin_info.find("./note[@type='internal']")

    if existing_internal_note is not None:
        note_element = existing_internal_note
        note_element.text = (note_element.text or "") + note_text
    else:
        note_element = ET.Element("note", type="internal")
        admin_info.append(note_element)
        note_element.text = note_text


def _handle_known_errors(
    classic_quality_output: ET.Element, validation_errors: list[str] | None
):
    if not validation_errors or len(validation_errors) == 0:
        return None

    for i, error in enumerate(validation_errors):
        if (
            "Could not find metadata for child with nameInData: relatedItem and attributes: type:conference"
            in error
        ):
            related_conference = classic_quality_output.find(
                "./relatedItem[@type='conference']"
            )
            if related_conference is not None:

                validation_errors[i] = (
                    error
                    + f" (conference: \"{related_conference.findtext('./conference')}\")"
                )
                classic_quality_output.remove(related_conference)
