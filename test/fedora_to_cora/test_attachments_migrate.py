import xml.etree.ElementTree as ET
from unittest.mock import MagicMock

from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.create import CreateRecordFailureResult, CreateRecordSuccessResult
from cora.update import UpdateRecordResult
from cora.upload import UploadError
from fedora_to_cora.attachments_migrate import attachments_migrate
from cora.context import MockContext


def test_attachments_migrate(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    upload_binary_mock = _set_up_upload_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)
    binary_record_transform_mock = _set_up_binary_record_transform_mock(monkeypatch)
    attachments_transform_mock = _set_up_attachments_transform_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <path>test.pdf</path>
                </attachment>
                 <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <path>test2.pdf</path>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(
        source_record,
        cora_record,
        MockContext(),
        xml_dir="test/xml",
    )

    assert binary_record_transform_mock.call_count == 2
    assert create_record_mock.call_count == 2
    assert upload_binary_mock.call_count == 2
    assert attachments_transform_mock.call_count == 2
    assert update_record_mock.call_count == 1

    assert len(update_record_mock.mock_calls) == 1
    updated_cora_record = update_record_mock.mock_calls[0].args[0]
    assert_equal_for_xml_and_xml_string(
        updated_cora_record,
        """
        <record>
            <data>
                <output>
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
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
                </output>
            </data>
        </record>
        """,
    )


def test_failed_to_create_binary_record(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch, fail=True)
    upload_binary_mock = _set_up_upload_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)
    binary_record_transform_mock = _set_up_binary_record_transform_mock(monkeypatch)
    attachments_transform_mock = _set_up_attachments_transform_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <path>test.pdf</path>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    success, errors = attachments_migrate(
        source_record,
        cora_record,
        MockContext(),
        xml_dir="test/xml",
    )

    assert binary_record_transform_mock.call_count == 1
    assert create_record_mock.call_count == 1
    assert upload_binary_mock.call_count == 0
    assert attachments_transform_mock.call_count == 0
    assert update_record_mock.call_count == 0

    assert not success
    assert errors is not None
    assert len(errors) == 1
    assert errors[0] == "Failed to create binary record"


def test_failed_to_upload_binary(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    upload_binary_mock = _set_up_upload_binary_mock(monkeypatch, fail=True)
    update_record_mock = _set_up_update_record_mock(monkeypatch)
    binary_record_transform_mock = _set_up_binary_record_transform_mock(monkeypatch)
    attachments_transform_mock = _set_up_attachments_transform_mock(monkeypatch)
    delete_record_mock = _set_up_delete_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <path>test.pdf</path>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    success, errors = attachments_migrate(
        source_record,
        cora_record,
        MockContext(),
        xml_dir="test/xml",
    )

    assert binary_record_transform_mock.call_count == 1
    assert create_record_mock.call_count == 1
    assert upload_binary_mock.call_count == 1
    assert attachments_transform_mock.call_count == 0
    assert update_record_mock.call_count == 0
    assert delete_record_mock.call_count == 1

    assert not success
    assert errors is not None
    assert len(errors) == 1
    assert errors[0] == "UploadError: Failed to upload binary"


def failed_to_update_record(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    upload_binary_mock = _set_up_upload_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch, fail=True)
    binary_record_transform_mock = _set_up_binary_record_transform_mock(monkeypatch)
    attachments_transform_mock = _set_up_attachments_transform_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <path>test.pdf</path>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    success, errors = attachments_migrate(
        source_record,
        cora_record,
        MockContext(),
        xml_dir="test/xml",
    )

    assert binary_record_transform_mock.call_count == 1
    assert create_record_mock.call_count == 1
    assert upload_binary_mock.call_count == 1
    assert attachments_transform_mock.call_count == 0
    assert update_record_mock.call_count == 0

    assert not success
    assert errors is not None
    assert len(errors) == 1
    assert errors[0] == "UploadError: Failed to upload binary"


def test_roll_back_binary_records_when_something_fails(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)

    upload_binary_mock = _set_up_upload_binary_mock(monkeypatch)
    upload_binary_mock.side_effect = [None, UploadError("Failed to upload binary")]

    update_record_mock = _set_up_update_record_mock(monkeypatch)

    binary_record_transform_mock = _set_up_binary_record_transform_mock(monkeypatch)
    attachments_transform_mock = _set_up_attachments_transform_mock(monkeypatch)

    delete_record_mock = MagicMock()
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.delete_record", delete_record_mock
    )

    source_record = ET.fromstring(
        """
        <publication>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <path>test.pdf</path>
                </attachment>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <path>test2.pdf</path>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    success, errors = attachments_migrate(
        source_record,
        cora_record,
        MockContext(),
        xml_dir="test/xml",
    )

    assert binary_record_transform_mock.call_count == 2
    assert create_record_mock.call_count == 2
    assert upload_binary_mock.call_count == 2
    assert attachments_transform_mock.call_count == 1
    assert update_record_mock.call_count == 0
    assert delete_record_mock.call_count == 2

    assert not success
    assert errors is not None
    assert len(errors) == 1
    assert errors[0] == "UploadError: Failed to upload binary"


def _set_up_create_record_mock(monkeypatch, fail=False):
    create_record_mock = MagicMock(
        return_value=(
            CreateRecordSuccessResult(
                record_id="binary:12345", response_data=ET.Element("response")
            )
            if not fail
            else CreateRecordFailureResult(error="Failed to create binary record")
        )
    )
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.create_record", create_record_mock
    )
    return create_record_mock


def _set_up_upload_binary_mock(monkeypatch, fail=False):
    upload_binary_mock = MagicMock()
    if fail:
        upload_binary_mock.side_effect = UploadError("Failed to upload binary")
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.upload_binary", upload_binary_mock
    )
    return upload_binary_mock


def _set_up_update_record_mock(monkeypatch, fail=False):
    update_record_mock = MagicMock(
        return_value=UpdateRecordResult(
            success=not fail,
            record_id="test" if not fail else None,
            response_data=ET.Element("data") if not fail else None,
            error="Failed to update record" if fail else None,
        )
    )
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.update_record", update_record_mock
    )
    return update_record_mock


def _set_up_binary_record_transform_mock(monkeypatch):
    binary_record_mock = MagicMock()
    binary_record_transform_mock = MagicMock(return_value=binary_record_mock)
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.binary_record_transform",
        binary_record_transform_mock,
    )
    return binary_record_transform_mock


def _set_up_attachments_transform_mock(monkeypatch):
    mock_attachment = ET.fromstring(
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
        """
    )

    attachments_transform_mock = MagicMock(return_value=mock_attachment)
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.attachment_transform",
        attachments_transform_mock,
    )
    return attachments_transform_mock


def _set_up_delete_record_mock(monkeypatch):
    delete_record_mock = MagicMock()
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.delete_record", delete_record_mock
    )
    return delete_record_mock
