import xml.etree.ElementTree as ET
from common.record_info_create import record_info_create
from common.xml_utils import append_if_value, create_group, create_text
from .get_binary_visibility import get_binary_visibility


def binary_record_transform(
    attachment: ET.Element, host_record: ET.Element | None
) -> ET.Element:
    binary = create_group(
        "binary",
        [
            record_info_create(
                validation_type_id="genericBinary",
                visibility=get_binary_visibility(attachment),
                host_record_id=host_record,
            ),
            _create_original_file_name(attachment),
            _create_expected_file_size(attachment),
            _create_expected_checksum(attachment),
        ],
        type="generic",
    )
    assert binary is not None
    return binary


def _create_original_file_name(source_record: ET.Element):
    return create_text(
        "originalFileName",
        source_record.findtext("./path", default="").split("/")[-1],
    )


def _create_expected_file_size(source_record: ET.Element):
    return create_text("expectedFileSize", source_record.findtext("./fileSize"))


def _create_expected_checksum(source_record: ET.Element):
    return create_text("expectedChecksum", source_record.findtext(".//checksum/digest"))
