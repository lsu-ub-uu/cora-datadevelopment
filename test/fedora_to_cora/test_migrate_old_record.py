from unittest.mock import patch
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
from cora.create import CreateRecordFailureResult, CreateRecordSuccessResult
import xml.etree.ElementTree as ET
from cora.update import UpdateRecordResult
from cora.upload import UploadError
from fedora_to_cora.migrate_old_record import old_record_migrate


@patch("fedora_to_cora.migrate_old_record.create_record")
@patch("fedora_to_cora.migrate_old_record.upload_binary")
@patch("fedora_to_cora.migrate_old_record.update_record")
def test_successfully_creates_old_record_with_binary(
    mock_update, mock_upload, mock_create
):
    binary_response = ET.Element("record")
    mock_created_old_record = """<record>
        <data>
            <oldRecord>
                <recordInfo>
                    <id>someId</id>
                    <validationType>
                        <linkedRecordType>validationType</linkedRecordType>
                        <linkedRecordId>diva-oldRecord</linkedRecordId>
                    </validationType>
                    <dataDivider>
                        <linkedRecordType>system</linkedRecordType>
                        <linkedRecordId>divaData</linkedRecordId>
                    </dataDivider>
                    <oldId>somePid</oldId>
                </recordInfo>
            </oldRecord>
        </data>
    </record>"""

    def create_record_side_effect(record, *, record_type, context, **kwargs):
        if record_type == "diva-oldRecord":
            return CreateRecordSuccessResult(
                record_id="old-record-123",
                response_data=ET.fromstring(mock_created_old_record),
            )
        if record_type == "binary":
            return CreateRecordSuccessResult(
                record_id="binary-record-123",
                response_data=binary_response,
            )
        raise AssertionError(f"Unexpected record_type: {record_type}")

    mock_create.side_effect = create_record_side_effect

    source_record = ET.fromstring("<publication><pid>somePid</pid></publication>")
    context = MockContext()

    result = old_record_migrate(source_record, context)

    assert result.status == "CREATED"
    assert result.cora_old_record_id == "old-record-123"
    assert result.error is None
    assert mock_create.call_count == 2

    records_by_type = {
        call.kwargs["record_type"]: call.args[0] for call in mock_create.call_args_list
    }

    assert set(records_by_type) == {"diva-oldRecord", "binary"}

    created_old_record = records_by_type["diva-oldRecord"]
    created_binary_record = records_by_type["binary"]

    # Assert create old record
    assert_equal_for_xml_and_xml_string(
        created_old_record,
        """
        <oldRecord>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-oldRecord</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <oldId>somePid</oldId>
            </recordInfo>
        </oldRecord>
    """,
    )

    # Assert create binary record
    assert_equal_for_xml_and_xml_string(
        created_binary_record,
        """
        <binary type="generic">
            <recordInfo>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>genericBinary</linkedRecordId>
                </validationType>
                <visibility>published</visibility>
                <hostRecord>
                    <linkedRecordType>diva-oldRecord</linkedRecordType>
                    <linkedRecordId>old-record-123</linkedRecordId>  
                </hostRecord>
                <status>created</status>
            </recordInfo>
            <originalFileName>somePid.xml</originalFileName>
            <expectedFileSize>88</expectedFileSize>
            <expectedChecksum>167e9b7f2e512a8aeb45c8fb455e475ed2b3050e6b7fa783f15d0f150bcbf41fd50460887b30221e1289280fa9ddfe1fe163cb8dc88a1e9a6bb7267c1bf51c2d</expectedChecksum>
        </binary>
        """,
    )

    # Assert upload binary
    mock_upload.assert_called_once_with(
        binary_response,
        "somePid.xml",
        b"<?xml version='1.0' encoding='utf-8'?>\n"
        b"<publication>\n"
        b"  <pid>somePid</pid>\n"
        b"</publication>",
        context=context,
    )

    # Assert update old record with link to binary record
    mock_update.assert_called_once()
    update_call = mock_update.call_args
    assert update_call.kwargs["context"] == context

    assert_equal_for_xml_and_xml_string(
        update_call.args[0],
        """
        <record>
            <data>
                <oldRecord>
                    <recordInfo>
                        <id>someId</id>
                        <validationType>
                            <linkedRecordType>validationType</linkedRecordType>
                            <linkedRecordId>diva-oldRecord</linkedRecordId>
                        </validationType>
                        <dataDivider>
                            <linkedRecordType>system</linkedRecordType>
                            <linkedRecordId>divaData</linkedRecordId>
                        </dataDivider>
                        <oldId>somePid</oldId>
                    </recordInfo>
                    <record repeatId="0">
                        <linkedRecordType>binary</linkedRecordType>
                        <linkedRecordId>binary-record-123</linkedRecordId>
                    </record>
                </oldRecord>
            </data>
        </record>
        """,
    )


@patch("fedora_to_cora.migrate_old_record.create_record")
def test_returns_failed_when_failed_to_create_old_record_record(mock_create):
    mock_create.return_value = CreateRecordFailureResult("something went wrong", 500)
    source_record = ET.fromstring("<publication><pid>somePid</pid></publication>")
    context = MockContext()

    result = old_record_migrate(source_record, context)

    assert result.status == "FAILED"
    assert result.cora_old_record_id is None
    assert result.error == "Failed to create diva-oldRecord: something went wrong"


@patch("fedora_to_cora.migrate_old_record.create_record")
def test_returns_skipped_when_old_record_already_exists(mock_create):
    mock_create.return_value = CreateRecordFailureResult(
        "A record matching the unique rule with [key: oldId, value: somePid] already exists in the system",
        409,
    )
    source_record = ET.fromstring("<publication><pid>somePid</pid></publication>")
    context = MockContext()

    result = old_record_migrate(source_record, context)

    assert result.status == "SKIPPED"
    assert result.cora_old_record_id is None
    assert result.error == "Cora diva-oldRecord record already exists"


@patch("fedora_to_cora.migrate_old_record.create_record")
def test_returs_failed_when_failed_to_create_binary_record(mock_create):
    def create_record_side_effect(record, *, record_type, context, **kwargs):
        if record_type == "diva-oldRecord":
            return CreateRecordSuccessResult(
                record_id="old-record-123",
                response_data=ET.Element("record"),
            )
        if record_type == "binary":
            return CreateRecordFailureResult("something went wrong", 500)
        raise AssertionError(f"Unexpected record_type: {record_type}")

    mock_create.side_effect = create_record_side_effect

    source_record = ET.fromstring("<publication><pid>somePid</pid></publication>")
    context = MockContext()

    result = old_record_migrate(source_record, context)

    assert result.status == "FAILED"
    assert result.cora_old_record_id is None
    assert result.error == "Failed to create binary for oldRecord: something went wrong"


@patch("fedora_to_cora.migrate_old_record.create_record")
@patch("fedora_to_cora.migrate_old_record.upload_binary")
def test_returns_failed_when_uploading_binary_fails(mock_upload, mock_create):
    def create_record_side_effect(record, *, record_type, context, **kwargs):
        if record_type == "diva-oldRecord":
            return CreateRecordSuccessResult(
                record_id="old-record-123",
                response_data=ET.Element("record"),
            )
        if record_type == "binary":
            return CreateRecordSuccessResult(
                record_id="binary-record-123",
                response_data=ET.Element("record"),
            )
        raise AssertionError(f"Unexpected record_type: {record_type}")

    mock_create.side_effect = create_record_side_effect

    mock_upload.side_effect = UploadError("Something went wrong uploading file")

    source_record = ET.fromstring("<publication><pid>somePid</pid></publication>")
    context = MockContext()

    result = old_record_migrate(source_record, context)

    assert result.status == "FAILED"
    assert result.cora_old_record_id is None
    assert (
        result.error
        == "Failed to upload binary for oldRecord: UploadError: Something went wrong uploading file"
    )


@patch("fedora_to_cora.migrate_old_record.create_record")
@patch("fedora_to_cora.migrate_old_record.upload_binary")
@patch("fedora_to_cora.migrate_old_record.update_record")
def test_returns_failed_when_updating_old_record_fails(
    mock_update, mock_upload, mock_create
):
    binary_response = ET.Element("record")
    mock_created_old_record = """<record>
            <data>
                <oldRecord>
                    <recordInfo>
                        <id>someId</id>
                        <validationType>
                            <linkedRecordType>validationType</linkedRecordType>
                            <linkedRecordId>diva-oldRecord</linkedRecordId>
                        </validationType>
                        <dataDivider>
                            <linkedRecordType>system</linkedRecordType>
                            <linkedRecordId>divaData</linkedRecordId>
                        </dataDivider>
                        <oldId>somePid</oldId>
                    </recordInfo>
                </oldRecord>
            </data>
        </record>"""

    def create_record_side_effect(record, *, record_type, context, **kwargs):
        if record_type == "diva-oldRecord":
            return CreateRecordSuccessResult(
                record_id="old-record-123",
                response_data=ET.fromstring(mock_created_old_record),
            )
        if record_type == "binary":
            return CreateRecordSuccessResult(
                record_id="binary-record-123",
                response_data=binary_response,
            )
        raise AssertionError(f"Unexpected record_type: {record_type}")

    mock_create.side_effect = create_record_side_effect

    mock_update.return_value = UpdateRecordResult(
        success=False, error="something went wrong"
    )

    source_record = ET.fromstring("<publication><pid>somePid</pid></publication>")
    context = MockContext()

    result = old_record_migrate(source_record, context)

    assert result.status == "FAILED"
    assert result.cora_old_record_id is None
    assert (
        result.error
        == "Failed to update oldRecord with binary link: something went wrong"
    )
