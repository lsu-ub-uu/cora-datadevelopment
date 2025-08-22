from unittest.mock import MagicMock
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.attachment_transform import attachment_transform
import pytest


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


@pytest.mark.parametrize(
    "tagName,expected_attachment_version",
    [
        ("prePrint", "submitted"),
        ("postPrint", "accepted"),
        ("print", "published"),
    ],
)
def test_attachment_version_submitted_when_preprint(
    tagName, expected_attachment_version
):
    source_record = ET.fromstring(
        f"""
            <attachment>
                <fileLabel>
                    <fileLabelId>50</fileLabelId>
                </fileLabel>
                <path>test.pdf</path>
                <{tagName}>true</{tagName}>
            </attachment>
        """
    )

    binary_record_id = "binary:12345"

    attachment = attachment_transform(source_record, binary_record_id)

    attachment_version = attachment.findtext("note[@type='attachmentVersion']")
    assert attachment_version == expected_attachment_version


def test_raises_error_when_multiple_attachment_versions():
    source_record = ET.fromstring(
        """
        <attachment>
            <fileLabel>
                <fileLabelId>50</fileLabelId>
            </fileLabel>
            <path>test.pdf</path>
            <prePrint>true</prePrint>
            <postPrint>true</postPrint>
        </attachment>
        """
    )

    binary_record_id = "binary:12345"

    with pytest.raises(ValueError, match="Multiple attachment versions found"):
        attachment_transform(source_record, binary_record_id)


def test_secrecy():
    source_record = ET.fromstring(
        """
        <attachment>
            <fileLabel>
                <fileLabelId>50</fileLabelId>
            </fileLabel>
            <path>test.pdf</path>
            <secrecyInfo>
                <secrecy>true</secrecy>
            </secrecyInfo>
        </attachment>
        """
    )

    binary_record_id = "binary:12345"

    attachment = attachment_transform(source_record, binary_record_id)

    assert attachment.findtext("./adminInfo/secrecy") == "true"


def test_registration_number():
    source_record = ET.fromstring(
        """
        <attachment>
            <fileLabel>
                <fileLabelId>50</fileLabelId>
            </fileLabel>
            <path>test.pdf</path>
            <registrationNumber>1234</registrationNumber>
        </attachment>
        """
    )

    binary_record_id = "binary:12345"

    attachment = attachment_transform(source_record, binary_record_id)

    assert (
        attachment.findtext("./adminInfo/identifier[@type='registrationNumber']")
        == "1234"
    )


# <displayLabel>
# <note type="attachmentVersion">
# <adminInfo>
#     <availability>
#     <dateAvailability>
#         <year>
#         <month>
#         <day>
#     </availability>
#     <note type="attachment">
# </adminInfo>
