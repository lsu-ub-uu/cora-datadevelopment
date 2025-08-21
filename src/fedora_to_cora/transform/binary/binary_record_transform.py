import xml.etree.ElementTree as ET
from common.record_info_create import record_info_create
from common.xml_utils import append_if_value
from .get_binary_visibility import get_binary_visibility


def binary_record_transform(attachment: ET.Element) -> ET.Element:
    binary_record = ET.Element("binary")
    binary_record.set("type", "generic")

    binary_record.append(
        record_info_create(
            validation_type_id="genericBinary",
            visibility=get_binary_visibility(attachment),
        )
    )

    append_if_value(binary_record, _create_original_file_name(attachment))
    append_if_value(binary_record, _create_expected_file_size(attachment))

    return binary_record


def _create_original_file_name(source_record: ET.Element) -> ET.Element:
    original_file_name = ET.Element("originalFileName")
    path = source_record.findtext("./path")
    if path is not None:
        original_file_name.text = path.split("/")[-1]
    return original_file_name


def _create_expected_file_size(source_record: ET.Element) -> ET.Element:
    expected_file_size = ET.Element("expectedFileSize")
    file_size = source_record.findtext("./fileSize")
    if file_size is not None:
        expected_file_size.text = file_size
    return expected_file_size
