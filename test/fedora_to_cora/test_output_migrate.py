import xml.etree.ElementTree as ET
from unittest.mock import MagicMock
from fedora_to_cora.output_migrate import output_migrate
from cora.context import MockContext


def test_migrate_with_dry_run(monkeypatch):
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

    valid, errors = output_migrate(source_record, mock_context, dry_run=True)

    assert valid is True
    assert errors == []

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    mock_create.assert_not_called()


def test_migrate_with_wet_run(monkeypatch):
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

    mock_create = MagicMock(return_value=(True, []))
    monkeypatch.setattr("fedora_to_cora.output_migrate.create_record", mock_create)

    valid, errors = output_migrate(source_record, mock_context, dry_run=False)

    assert valid is True
    assert errors == []

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


def test_migrate_with_dry_run_validation_errors(monkeypatch):
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

    valid, errors = output_migrate(source_record, mock_context, dry_run=True)

    assert valid is False
    assert errors == expected_errors

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )
