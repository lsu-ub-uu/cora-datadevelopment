from db_to_cora.records_import import records_import
from cora.context import MockContext
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch


@patch("db_to_cora.records_import.validate_record")
@patch("db_to_cora.records_import.create_record")
@patch("builtins.print")
def test_dry_run_all_valid(mock_print, mock_create_record, mock_validate_record):
    mock_source_records = [
        ET.fromstring("<source><old_id>1</old_id><field>value1</field></source>"),
        ET.fromstring("<source><old_id>2</old_id><field>value2</field></source>"),
    ]
    mock_context = MockContext()

    mock_transform_function = MagicMock()

    mock_validate_record.side_effect = [(True, "Valid"), (True, "Valid")]

    records_import(
        mock_context,
        "test-type",
        mock_source_records,
        mock_transform_function,
        None,
        apply=False,
    )

    assert mock_transform_function.call_count == 2
    assert mock_validate_record.call_count == 2
    assert mock_create_record.call_count == 0
    mock_print.assert_any_call("✅ 2 valid")


@patch("db_to_cora.records_import.validate_record")
@patch("db_to_cora.records_import.create_record")
@patch("builtins.print")
def test_dry_run_one_invalid(mock_print, mock_create_record, mock_validate_record):
    mock_source_records = [
        ET.fromstring("<source><old_id>1</old_id><field>value1</field></source>"),
        ET.fromstring("<source><old_id>2</old_id><field>value2</field></source>"),
    ]
    mock_context = MockContext()

    mock_transform_function = MagicMock()

    mock_validate_record.side_effect = [(True, "Valid"), (False, "Invalid")]

    records_import(
        mock_context,
        "test-type",
        mock_source_records,
        mock_transform_function,
        None,
        apply=False,
    )

    assert mock_transform_function.call_count == 2
    assert mock_validate_record.call_count == 2
    assert mock_create_record.call_count == 0

    mock_print.assert_any_call("✅ 1 valid")
    mock_print.assert_any_call("❌ 1 invalid")


@patch("db_to_cora.records_import.validate_record")
@patch("db_to_cora.records_import.create_record")
def test_records_import_no_relations(mock_create_record, mock_validate_record):
    mock_source_records = [
        ET.fromstring("<source><old_id>1</old_id><field>value1</field></source>"),
        ET.fromstring("<source><old_id>2</old_id><field>value2</field></source>"),
    ]
    mock_context = MockContext()
    mock_transform_function = MagicMock()

    records_import(
        mock_context,
        "test-type",
        mock_source_records,
        mock_transform_function,
        None,
        apply=True,
    )

    assert mock_validate_record.call_count == 0
    assert mock_create_record.call_count == 2


@patch("db_to_cora.records_import.validate_record")
@patch("db_to_cora.records_import.create_record")
@patch("db_to_cora.update_relations.update_relations")
def xtest_records_import_with_relations(
    mock_update_relations, mock_create_record, mock_validate_record
):
    mock_source_records = [
        ET.fromstring("<source><old_id>1</old_id><field>value1</field></source>"),
        ET.fromstring("<source><old_id>2</old_id><field>value2</field></source>"),
    ]
    mock_context = MockContext()
    mock_transform_function = MagicMock()

    records_import(
        mock_context,
        "test-type",
        mock_source_records,
        mock_transform_function,
        [("relatedRecord", "related_id"), ("anotherRelation", "another_id")],
        apply=True,
    )

    assert mock_validate_record.call_count == 0
    assert mock_create_record.call_count == 2
    assert mock_update_relations.call_count == 1
