from unittest.mock import MagicMock
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.attachment_transform import attachment_transform


def test_attachment_transform(monkeypatch):
    get_attachment_type_mock = MagicMock(return_value="fullText")
    monkeypatch.setattr(
        "fedora_to_cora.transform.attachment_transform.get_attachment_type",
        get_attachment_type_mock,
    )

    source_record = ET.fromstring(
        """
            <attachment>
                <fileLabel>
                    <fileLabelId>50</fileLabelId>
                </fileLabel>
                <path>test.pdf</path>
            </attachment>
        """
    )
    binary_record_id = "binary:12345"

    attachment = attachment_transform(source_record, binary_record_id)

    assert_equal_for_xml_and_xml_string(
        attachment,
        """
        <attachment repeatId="binary:12345">
            <attachmentFile>
              <linkedRecordType>binary</linkedRecordType>
              <linkedRecordId>binary:12345</linkedRecordId>
            </attachmentFile>
            <type>fullText</type>
            <adminInfo>
                <availability>availableNow</availability>
            </adminInfo>
        </attachment>
        """,
    )
