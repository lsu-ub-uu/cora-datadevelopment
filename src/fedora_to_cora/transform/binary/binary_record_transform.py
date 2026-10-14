import xml.etree.ElementTree as ET
from common.common_data import create_record_link
from common.xml_utils import create_group, create_text
from .get_binary_visibility import get_binary_visibility


def binary_record_transform(
    attachment: ET.Element, host_record: ET.Element
) -> ET.Element:
    binary = create_group(
        "binary",
        [
            _create_record_info(attachment, host_record),
            _create_original_file_name(attachment),
            _create_expected_file_size(attachment),
            _create_expected_checksum(attachment),
        ],
        type="generic",
    )

    assert binary is not None
    return binary


def _create_record_info(attachment: ET.Element, host_record: ET.Element):
    return create_group(
        "recordInfo",
        children=[
            create_record_link(
                name_in_data="validationType",
                record_type="validationType",
                record_id="genericBinary",
            ),
            create_record_link(
                name_in_data="dataDivider", record_type="system", record_id="divaData"
            ),
            create_text("visibility", get_binary_visibility(attachment)),
            host_record,
            create_text("status", "created"),
        ],
    )


def _create_original_file_name(source_record: ET.Element):
    return create_text(
        "originalFileName",
        source_record.findtext("./path", default="").split("/")[-1],
    )


def _create_expected_file_size(source_record: ET.Element):
    return create_text("expectedFileSize", source_record.findtext("./fileSize"))


def _create_expected_checksum(source_record: ET.Element):
    return create_text("expectedChecksum", source_record.findtext(".//checksum/digest"))
