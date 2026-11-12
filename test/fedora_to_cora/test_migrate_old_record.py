from unittest.mock import Mock, patch
from cora_python_client import (
    CoraClient,
    CoraHTTPError,
    CoraConflictError,
    CoraRecord,
    CoraUploadError,
)
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
from cora.create import CreateRecordFailureResult, CreateRecordSuccessResult
import xml.etree.ElementTree as ET
from cora.update import UpdateRecordResult
from cora.upload import UploadError
from fedora_to_cora.migrate_old_record import old_record_migrate


def test_successfully_creates_old_record_with_binary():
    mock_cora_client = Mock(CoraClient)
    mock_created_old_record = """<record>
        <data>
            <oldRecord>
                <recordInfo>
                    <id>old-record-123</id>
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

    mock_cora_client.create_record.return_value = CoraRecord(
        xml=ET.fromstring(mock_created_old_record)
    )

    mock_cora_client.create_and_upload_binary.return_value = CoraRecord(
        xml=ET.fromstring("""
        <record>
            <data>
                <binary type="generic">
                    <recordInfo>
                        <id>binary-record-123</id>
                    </recordInfo>
                </binary>
            </data>
        </record>
    """)
    )

    source_record = ET.fromstring("<publication><pid>somePid</pid></publication>")

    result = old_record_migrate(source_record, mock_cora_client)

    assert result.status == "CREATED"
    assert result.cora_old_record_id == "old-record-123"
    assert result.error is None

    mock_cora_client.create_record.assert_called_once()
    created_old_record = mock_cora_client.create_record.call_args[0][0]

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

    # Assert upload binary
    mock_cora_client.create_and_upload_binary.assert_called_once_with(
        visibility="published",
        host_record_type="diva-oldRecord",
        host_record_id="old-record-123",
        original_file_name="somePid.xml",
        data=b"<?xml version='1.0' encoding='utf-8'?>\n"
        b"<publication>\n"
        b"  <pid>somePid</pid>\n"
        b"</publication>",
    )

    # Assert update old record with link to binary record
    mock_cora_client.update_record.assert_called_once()
    update_call = mock_cora_client.update_record.call_args
    assert_equal_for_xml_and_xml_string(
        update_call.args[0].xml,
        """
        <record>
            <data>
                <oldRecord>
                    <recordInfo>
                        <id>old-record-123</id>
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


def test_returns_failed_when_failed_to_create_old_record_record():
    mock_cora_client = Mock(CoraClient)
    mock_cora_client.create_record.side_effect = CoraHTTPError(
        500, "something went wrong"
    )
    source_record = ET.fromstring("<publication><pid>somePid</pid></publication>")

    result = old_record_migrate(source_record, mock_cora_client)

    assert result.status == "FAILED"
    assert result.cora_old_record_id is None
    assert (
        result.error
        == "Failed to create diva-oldRecord: CoraHTTPError (HTTP 500): something went wrong"
    )


def test_returns_skipped_when_old_record_already_exists():
    mock_cora_client = Mock(CoraClient)
    mock_cora_client.create_record.side_effect = CoraConflictError(
        409,
        "A record matching the unique rule with [key: oldId, value: somePid] already exists in the system",
    )
    source_record = ET.fromstring("<publication><pid>somePid</pid></publication>")
    context = MockContext()

    result = old_record_migrate(source_record, mock_cora_client)

    assert result.status == "SKIPPED"
    assert result.cora_old_record_id is None
    assert result.error == "Cora diva-oldRecord record already exists"


def test_returs_failed_when_failed_to_create_binary():
    mock_cora_client = Mock(CoraClient)
    mock_cora_client.create_record.return_value = CoraRecord(
        xml=ET.fromstring(
            "<record><data><oldRecord><recordInfo><id>old-record-123</id></recordInfo></oldRecord></data></record>"
        )
    )
    mock_cora_client.create_and_upload_binary.side_effect = CoraHTTPError(
        500, "Something went wrong creating binary record"
    )

    source_record = ET.fromstring("<publication><pid>somePid</pid></publication>")

    result = old_record_migrate(source_record, mock_cora_client)

    assert result.status == "FAILED"
    assert result.cora_old_record_id is None
    assert (
        result.error
        == "Failed to create and upload binary: CoraHTTPError (HTTP 500): Something went wrong creating binary record"
    )


def test_returns_failed_when_uploading_binary_fails():
    mock_cora_client = Mock(CoraClient)
    mock_cora_client.create_record.return_value = CoraRecord(
        xml=ET.fromstring(
            "<record><data><oldRecord><recordInfo><id>old-record-123</id></recordInfo></oldRecord></data></record>"
        )
    )
    mock_cora_client.create_and_upload_binary.side_effect = CoraUploadError(
        "Something went wrong uploading binary",
        CoraRecord(xml=ET.Element("record")),
        500,
    )

    source_record = ET.fromstring("<publication><pid>somePid</pid></publication>")

    result = old_record_migrate(source_record, mock_cora_client)

    assert result.status == "FAILED"
    assert result.cora_old_record_id is None
    assert (
        result.error
        == "Failed to create and upload binary: CoraUploadError (HTTP 500): Something went wrong uploading binary"
    )


def test_returns_failed_when_updating_old_record_fails():
    mock_cora_client = Mock(CoraClient)
    mock_created_old_record = """<record>
        <data>
            <oldRecord>
                <recordInfo>
                    <id>old-record-123</id>
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

    mock_cora_client.create_record.return_value = CoraRecord(
        xml=ET.fromstring(mock_created_old_record)
    )

    mock_cora_client.create_and_upload_binary.return_value = CoraRecord(
        xml=ET.fromstring("""
        <record>
            <data>
                <binary type="generic">
                    <recordInfo>
                        <id>binary-record-123</id>
                    </recordInfo>
                </binary>
            </data>
        </record>
    """)
    )

    source_record = ET.fromstring("<publication><pid>somePid</pid></publication>")

    mock_cora_client.update_record.side_effect = CoraHTTPError(
        500, "something went wrong"
    )

    source_record = ET.fromstring("<publication><pid>somePid</pid></publication>")

    result = old_record_migrate(source_record, mock_cora_client)

    assert result.status == "FAILED"
    assert result.cora_old_record_id is None
    assert (
        result.error
        == "Failed to update oldRecord with binary link: CoraHTTPError (HTTP 500): something went wrong"
    )
