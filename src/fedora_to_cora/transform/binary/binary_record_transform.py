import xml.etree.ElementTree as ET
from common.binary_record_data_create import create_binary_record_data
from .get_binary_visibility import get_binary_visibility


def binary_record_transform(
    attachment: ET.Element, host_record: ET.Element
) -> ET.Element:
    return create_binary_record_data(
        visibility=get_binary_visibility(attachment),
        host_record_type=host_record.findtext("linkedRecordType", default=""),
        host_record_id=host_record.findtext("linkedRecordId", default=""),
        original_file_name=attachment.findtext("./path", default="").split("/")[-1],
        expected_file_size=attachment.findtext("./fileSize"),
        expected_checksum=attachment.findtext(".//checksum/digest"),
    )
