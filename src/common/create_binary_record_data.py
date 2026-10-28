import xml.etree.ElementTree as ET

from common.common_data import create_record_link
from common.xml_utils import create_group, create_text


def create_binary_record_data(
    visibility: str,
    host_record_type: str,
    host_record_id: str,
    original_file_name: str,
    expected_file_size: str | None,
    expected_checksum: str | None,
) -> ET.Element:
    binary = create_group(
        "binary",
        type="generic",
        children=[
            create_group(
                "recordInfo",
                children=[
                    create_record_link("dataDivider", "system", "divaData"),
                    create_record_link(
                        "validationType", "validationType", "genericBinary"
                    ),
                    create_text("visibility", visibility),
                    create_record_link("hostRecord", host_record_type, host_record_id),
                    create_text("status", "created"),
                ],
            ),
            create_text("originalFileName", original_file_name),
            (
                create_text("expectedFileSize", expected_file_size)
                if expected_file_size is not None
                else None
            ),
            (
                create_text("expectedChecksum", expected_checksum)
                if expected_checksum is not None
                else None
            ),
        ],
    )
    assert binary is not None
    return binary
