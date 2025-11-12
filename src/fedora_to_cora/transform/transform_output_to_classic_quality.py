import xml.etree.ElementTree as ET

VALIDATION_TYPE_PREFIX = "classic_"
TAGS_WITHOUT_REPEAT_ID = {"recordInfo"}


def transform_output_to_classic_quality(cora_output: ET.Element):
    classic_quality_output = ET.fromstring(ET.tostring(cora_output))

    _update_validation_type(classic_quality_output)
    _update_data_quality(classic_quality_output)
    _add_repeat_ids(classic_quality_output)

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


def _add_repeat_ids(classic_quality_output: ET.Element):
    [
        _add_repeat_ids_recursive(child, index)
        for index, child in enumerate(classic_quality_output)
    ]


def _add_repeat_ids_recursive(element: ET.Element, repeat_id: int = 0):
    if element.tag in TAGS_WITHOUT_REPEAT_ID:
        return

    if element.get("repeatId") is None:
        element.set("repeatId", str(repeat_id))

    if len(element) > 0:
        for index, child in enumerate(element):
            _add_repeat_ids_recursive(child, index)
