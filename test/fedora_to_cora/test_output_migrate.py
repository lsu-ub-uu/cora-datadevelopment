import xml.etree.ElementTree as ET
from unittest.mock import MagicMock
from cora.create import CreateRecordSuccessResult
from fedora_to_cora.output_migrate import output_migrate
from cora.context import MockContext


def test_migrate_with_apply_false(monkeypatch):
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

    mock_transform = MagicMock(return_value=mock_cora_output)
    monkeypatch.setattr(
        "fedora_to_cora.output_migrate.transform_to_cora_output",
        mock_transform,
    )

    mock_validate = MagicMock(return_value=(True, []))
    monkeypatch.setattr("fedora_to_cora.output_migrate.validate_record", mock_validate)

    mock_create = MagicMock()
    monkeypatch.setattr("fedora_to_cora.output_migrate.create_record", mock_create)

    valid, errors = output_migrate(
        source_record, mock_context, xml_dir="test/xml", apply=False
    )

    assert valid is True
    assert errors == None

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    mock_create.assert_not_called()


def test_migrate_with_apply_when_create_record_success(monkeypatch):
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

    mock_transform = MagicMock(return_value=mock_cora_output)
    monkeypatch.setattr(
        "fedora_to_cora.output_migrate.transform_to_cora_output",
        mock_transform,
    )

    mock_validate = MagicMock(return_value=(True, []))
    monkeypatch.setattr("fedora_to_cora.output_migrate.validate_record", mock_validate)

    mock_created_record = ET.Element("record")
    mock_create = MagicMock(
        return_value=CreateRecordSuccessResult(
            record_id="123", response_data=mock_created_record
        )
    )
    monkeypatch.setattr("fedora_to_cora.output_migrate.create_record", mock_create)

    mock_attachments_migrate = MagicMock(return_value=(True, []))
    monkeypatch.setattr(
        "fedora_to_cora.output_migrate.attachments_migrate",
        mock_attachments_migrate,
    )

    mock_xml_dir = "test/xml"
    valid, errors = output_migrate(
        source_record, mock_context, xml_dir=mock_xml_dir, apply=True
    )

    assert valid is True
    assert errors == None

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    mock_create.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    # mock_attachments_migrate.assert_called_once_with(
    #     source_record,
    #     mock_created_record,
    #     mock_context,
    #     mock_xml_dir,
    # )


def test_rollback_when_failed_to_migrate_attachment(monkeypatch):
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

    mock_transform = MagicMock(return_value=mock_cora_output)
    monkeypatch.setattr(
        "fedora_to_cora.output_migrate.transform_to_cora_output",
        mock_transform,
    )

    mock_validate = MagicMock(return_value=(True, []))
    monkeypatch.setattr("fedora_to_cora.output_migrate.validate_record", mock_validate)

    mock_created_record = ET.Element("record")
    mock_create = MagicMock(
        return_value=CreateRecordSuccessResult(
            record_id="123", response_data=mock_created_record
        )
    )
    monkeypatch.setattr("fedora_to_cora.output_migrate.create_record", mock_create)

    mock_attachments_migrate = MagicMock(
        return_value=(False, ["Failed to upload file"])
    )
    monkeypatch.setattr(
        "fedora_to_cora.output_migrate.attachments_migrate",
        mock_attachments_migrate,
    )

    mock_delete_record = MagicMock()
    monkeypatch.setattr(
        "fedora_to_cora.output_migrate.delete_record", mock_delete_record
    )

    mock_xml_dir = "test/xml"
    valid, errors = output_migrate(
        source_record, mock_context, xml_dir=mock_xml_dir, apply=True
    )

    assert valid is False
    assert errors == ["Failed to upload file"]
    mock_delete_record.assert_called_once_with(mock_created_record, mock_context)


def test_migrate_with_apply_validation_errors(monkeypatch):
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

    mock_transform = MagicMock(return_value=mock_cora_output)
    monkeypatch.setattr(
        "fedora_to_cora.output_migrate.transform_to_cora_output",
        mock_transform,
    )

    expected_errors = ["Missing required field", "Invalid format"]
    mock_validate = MagicMock(return_value=(False, expected_errors))
    monkeypatch.setattr("fedora_to_cora.output_migrate.validate_record", mock_validate)

    valid, errors = output_migrate(
        source_record, mock_context, xml_dir="test/xml", apply=False
    )

    assert valid is False
    assert errors == expected_errors

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )
