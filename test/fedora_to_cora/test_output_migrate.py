import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.create import CreateRecordFailureResult, CreateRecordSuccessResult
from fedora_to_cora.output_migrate import output_migrate
from cora.context import MockContext


@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.create_record")
def test_migrate_with_apply_false(mock_create, mock_validate, mock_transform):
    mock_context = MockContext()

    source_record = ET.fromstring(
        """
        <publication>
            <title>Test Publication</title>
        </publication>
        """
    )

    mock_cora_output = ET.fromstring(
        """
        <record>
            <recordInfo>
                <id>test-id</id>
            </recordInfo>
        </record>
        """
    )

    mock_transform.return_value = mock_cora_output
    mock_validate.return_value = (True, [])

    result = output_migrate(source_record, mock_context, apply=False)

    assert result.status == "SUCCESS"
    assert result.errors is None

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    mock_create.assert_not_called()


@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.attachments_migrate")
def test_success_migrate_with_apply_true_and_with_binaries_true(
    mock_attachments_migrate, mock_create_record, mock_validate_record, mock_transform
):
    mock_context = MockContext()

    source_record = ET.fromstring(
        """
        <publication>
            <title>Test Publication</title>
        </publication>
        """
    )

    mock_cora_output = ET.fromstring(
        """
        <record>
            <recordInfo>
                <id>test-id</id>
            </recordInfo>
        </record>
        """
    )

    mock_transform.return_value = mock_cora_output

    mock_validate_record.return_value = (True, [])

    mock_created_record = ET.Element("record")
    mock_create_record.return_value = CreateRecordSuccessResult(
        record_id="123", response_data=mock_created_record
    )

    mock_attachments_migrate.return_value = (True, [])

    result = output_migrate(source_record, mock_context, apply=True, with_binaries=True)

    assert result.status == "SUCCESS"
    assert result.errors is None

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate_record.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    mock_create_record.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    mock_attachments_migrate.assert_called_once_with(
        source_record, mock_created_record, mock_context
    )


@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.attachments_migrate")
def test_success_migrate_with_apply_true_and_with_binaries_false(
    mock_attachments_migrate, mock_create_record, mock_validate_record, mock_transform
):
    mock_context = MockContext()

    source_record = ET.fromstring(
        """
        <publication>
            <title>Test Publication</title>
        </publication>
        """
    )

    mock_cora_output = ET.fromstring(
        """
        <record>
            <recordInfo>
                <id>test-id</id>
            </recordInfo>
        </record>
        """
    )

    mock_transform.return_value = mock_cora_output

    mock_validate_record.return_value = (True, [])

    mock_created_record = ET.Element("record")
    mock_create_record.return_value = CreateRecordSuccessResult(
        record_id="123", response_data=mock_created_record
    )

    mock_attachments_migrate.return_value = (True, [])

    result = output_migrate(
        source_record, mock_context, apply=True, with_binaries=False
    )

    assert result.status == "SUCCESS"
    assert result.errors is None

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate_record.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    mock_create_record.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    mock_attachments_migrate.assert_not_called()


@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.attachments_migrate")
@patch("fedora_to_cora.output_migrate.delete_record")
def test_rollback_when_failed_to_migrate_attachment(
    mock_delete_record,
    mock_attachments_migrate,
    mock_create,
    mock_validate,
    mock_transform,
):
    mock_context = MockContext()

    source_record = ET.fromstring(
        """
        <publication>
            <title>Test Publication</title>
        </publication>
        """
    )

    mock_cora_output = ET.fromstring(
        """
        <record>
            <recordInfo>
                <id>test-id</id>
            </recordInfo>
        </record>
        """
    )

    mock_transform.return_value = mock_cora_output
    mock_validate.return_value = (True, [])

    mock_created_record = ET.Element("record")
    mock_create.return_value = CreateRecordSuccessResult(
        record_id="123", response_data=mock_created_record
    )

    mock_attachments_migrate.return_value = (False, ["Failed to upload file"])

    result = output_migrate(source_record, mock_context, apply=True, with_binaries=True)

    assert result.status == "FAILED"
    assert result.errors == ["Failed to upload file"]
    mock_delete_record.assert_called_once_with(mock_created_record, mock_context)


@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.create_record")
def test_migrate_with_classic_quality(mock_create, mock_transform, mock_validate):
    mock_context = MockContext()

    source_record = ET.fromstring(
        """
        <publication>
            <title>Test Publication</title>
        </publication>
        """
    )

    mock_cora_output = ET.fromstring(
        """
        <record>
            <recordInfo>
                <id>test-id</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>2026</dataQuality>
        </record>
        """
    )

    mock_transform.return_value = mock_cora_output

    expected_errors = ["Missing required field", "Invalid format"]
    mock_validate.return_value = (False, expected_errors)

    result = output_migrate(source_record, mock_context, apply=False)

    assert result.status == "CLASSIC_QUALITY"
    assert result.errors == expected_errors

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    assert mock_create.call_count == 1
    created_output = mock_create.call_args[0][0]
    assert_equal_for_xml_and_xml_string(
        created_output,
        """
        <record>
            <recordInfo>
                <id>test-id</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>classic_publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality repeatId="1">classic</dataQuality>
        </record>
        """,
    )


@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.create_record")
def test_migrate_with_classic_quality_failure(
    mock_create, mock_transform, mock_validate
):
    mock_context = MockContext()

    source_record = ET.fromstring(
        """
        <publication>
            <title>Test Publication</title>
        </publication>
        """
    )

    mock_cora_output = ET.fromstring(
        """
        <record>
            <recordInfo>
                <id>test-id</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>2026</dataQuality>
        </record>
        """
    )

    mock_transform.return_value = mock_cora_output

    mock_validate.return_value = (
        False,
        [
            "Missing required field",
            "Invalid format",
        ],
    )

    mock_create.return_value = CreateRecordFailureResult(
        error="Failed to create record"
    )

    result = output_migrate(source_record, mock_context, apply=False)

    assert result.status == "FAILED"
    assert result.errors == [
        "Missing required field",
        "Invalid format",
        "Failed to create record",
    ]

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    assert mock_create.call_count == 1
