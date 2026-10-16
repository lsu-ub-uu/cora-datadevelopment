from unittest.mock import patch
import xml.etree.ElementTree as ET
from pathlib import Path
import pytest
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
from fedora_to_cora.migrate_old_record import MigrateOldRecordResult
from scripts.one_off.CORA_3812_update_existing_output_with_old_record import (
    _get_old_record_xml,
    fix_records,
    fix_record,
)


@patch(
    "scripts.one_off.CORA_3812_update_existing_output_with_old_record.read_source_xml"
)
@patch("scripts.one_off.CORA_3812_update_existing_output_with_old_record.list_records")
@patch("scripts.one_off.CORA_3812_update_existing_output_with_old_record.update_record")
@patch(
    "scripts.one_off.CORA_3812_update_existing_output_with_old_record.old_record_migrate"
)
def test_fix_records_prints_old_ids_when_dry_run(
    mock_old_record_migrate,
    mock_update_record,
    mock_list_records,
    mock_read_source_xml,
    capsys,
):
    mock_list_records.return_value = [
        ET.fromstring(
            "<record><data><output><recordInfo><oldId>old-id-1</oldId></recordInfo></output></data></record>"
        ),
        ET.fromstring(
            "<record><data><output><recordInfo><oldId>old-id-2</oldId></recordInfo></output></data></record>"
        ),
    ]

    context = MockContext()
    fix_records(context, apply=False, xml_dir="data/fedora_xml/nordiskamuseet")

    mock_list_records.assert_called_once_with(context, "diva-output")
    mock_read_source_xml.assert_any_call(
        Path("data/fedora_xml/nordiskamuseet/old-id-1.xml")
    )
    mock_read_source_xml.assert_any_call(
        Path("data/fedora_xml/nordiskamuseet/old-id-2.xml")
    )
    output_lines = capsys.readouterr().out.splitlines()

    assert mock_old_record_migrate.call_count == 0
    assert mock_update_record.call_count == 0
    assert output_lines == [
        "==================== Summary ====================",
        "Total diva-output records: 2",
        "Not updated (dry-run mode): 2",
        "Failed: 0",
        "Skipped: 0",
        "================================================",
    ]


@patch(
    "scripts.one_off.CORA_3812_update_existing_output_with_old_record.read_source_xml"
)
@patch("scripts.one_off.CORA_3812_update_existing_output_with_old_record.list_records")
@patch("scripts.one_off.CORA_3812_update_existing_output_with_old_record.update_record")
@patch(
    "scripts.one_off.CORA_3812_update_existing_output_with_old_record.old_record_migrate"
)
def test_fix_records_updates_records_when_applied(
    mock_old_record_migrate,
    mock_update_record,
    mock_list_records,
    mock_read_source_xml,
    capsys,
):
    mock_list_records.return_value = [
        ET.fromstring(
            "<record><data><output><recordInfo><oldId>old-id-1</oldId></recordInfo></output></data></record>"
        ),
        ET.fromstring(
            "<record><data><output><recordInfo><oldId>old-id-2</oldId></recordInfo></output></data></record>"
        ),
    ]
    old_record = ET.fromstring("<record><pid>source-id</pid></record>")
    mock_read_source_xml.return_value = old_record
    mock_old_record_migrate.return_value = MigrateOldRecordResult("CREATED", "old-record-id", None)
    mock_update_record.return_value.success = True

    context = MockContext()
    fix_records(context, apply=True, xml_dir="data/fedora_xml/nordiskamuseet")

    mock_list_records.assert_called_once_with(context, "diva-output")
    mock_read_source_xml.assert_any_call(
        Path("data/fedora_xml/nordiskamuseet/old-id-1.xml")
    )
    mock_read_source_xml.assert_any_call(
        Path("data/fedora_xml/nordiskamuseet/old-id-2.xml")
    )

    output_lines = capsys.readouterr().out.splitlines()

    assert mock_old_record_migrate.call_count == 2
    mock_old_record_migrate.assert_called_with(old_record, context)
    assert mock_update_record.call_count == 2
    for update_call in mock_update_record.call_args_list:
        record, update_context = update_call.args
        assert record in mock_list_records.return_value
        assert update_context is context
        assert (
            record.findtext("data/output/recordInfo/oldRecord/linkedRecordType")
            == "diva-oldRecord"
        )
        assert (
            record.findtext("data/output/recordInfo/oldRecord/linkedRecordId")
            == "old-record-id"
        )

    assert output_lines == [
        "==================== Summary ====================",
        "Total diva-output records: 2",
        "Updated: 2",
        "Failed: 0",
        "Skipped: 0",
        "================================================",
    ]


@patch(
    "scripts.one_off.CORA_3812_update_existing_output_with_old_record.read_source_xml"
)
@patch("scripts.one_off.CORA_3812_update_existing_output_with_old_record.update_record")
@patch(
    "scripts.one_off.CORA_3812_update_existing_output_with_old_record.old_record_migrate"
)
def test_fix_record_updates_output_with_old_record(
    mock_old_record_migrate, mock_update_record, mock_read_source_xml
):
    old_record = ET.fromstring("<record><pid>source-id</pid></record>")
    mock_read_source_xml.return_value = old_record
    mock_old_record_migrate.return_value = MigrateOldRecordResult("CREATED", "old-record-id", None)
    mock_update_record.return_value.success = True

    context = MockContext()
    record = ET.fromstring("""
        <record>
            <data>
                <output>
                    <recordInfo>
                        <id>123</id>
                        <oldId>old-id-1</oldId>
                    </recordInfo>
                </output>
            </data>
        </record>
    """)

    result = fix_record(
        record, context, apply=True, xml_dir="data/fedora_xml/nordiskamuseet"
    )

    assert result == "updated"
    updated_record = mock_update_record.call_args.args[0]
    assert_equal_for_xml_and_xml_string(
        updated_record,
        """
        <record>
            <data>
                <output>
                    <recordInfo>
                        <id>123</id>
                        <oldId>old-id-1</oldId>
                        <oldRecord>
                            <linkedRecordType>diva-oldRecord</linkedRecordType>
                            <linkedRecordId>old-record-id</linkedRecordId>
                        </oldRecord>
                    </recordInfo>
                </output>
            </data>
        </record>
        """,
    )


@pytest.mark.parametrize("apply", [True, False])
@patch(
    "scripts.one_off.CORA_3812_update_existing_output_with_old_record.read_source_xml"
)
@patch("scripts.one_off.CORA_3812_update_existing_output_with_old_record.update_record")
@patch(
    "scripts.one_off.CORA_3812_update_existing_output_with_old_record.old_record_migrate"
)
def test_fix_record_skips_missing_old_record_xml(
    mock_old_record_migrate, mock_update_record, mock_read_source_xml, apply, caplog
):
    mock_read_source_xml.side_effect = FileNotFoundError
    record = ET.fromstring(
        "<record><data><output><recordInfo><oldId>missing-id</oldId></recordInfo></output></data></record>"
    )

    result = fix_record(
        record, MockContext(), apply=apply, xml_dir="data/fedora_xml/nordiskamuseet"
    )

    assert result == "skipped"
    mock_old_record_migrate.assert_not_called()
    mock_update_record.assert_not_called()
    assert "data/fedora_xml/nordiskamuseet/missing-id.xml" in caplog.text
    assert "Skipping" in caplog.text


@patch("scripts.one_off.CORA_3812_update_existing_output_with_old_record.list_records")
def test_fix_records_skips_missing_old_id(mock_list_records, capsys):
    mock_list_records.return_value = [
        ET.fromstring("<record><data><output /></data></record>")
    ]

    fix_records(MockContext(), apply=False, xml_dir="data/fedora_xml/nordiskamuseet")
    assert "Skipped: 1" in capsys.readouterr().out


@pytest.mark.parametrize("status", ["SKIPPED", "FAILED"])
@pytest.mark.parametrize("update_success", [True, False])
def test_fix_record_handles_migration_results(monkeypatch, status, update_success):
    from scripts.one_off import CORA_3812_update_existing_output_with_old_record as script
    from unittest.mock import Mock
    context = MockContext()
    record = ET.fromstring("<record><data><output><recordInfo><oldId>old:1</oldId></recordInfo></output></data></record>")
    monkeypatch.setattr(script, "read_source_xml", Mock(return_value=ET.fromstring("<record><pid>old:1</pid></record>")))
    monkeypatch.setattr(script, "old_record_migrate", Mock(return_value=MigrateOldRecordResult(status, None, "Already exists")))
    lookup = Mock(return_value="existing-old-record")
    monkeypatch.setattr(script, "get_cora_id_by_old_id", lookup, raising=False)
    update = Mock()
    update.return_value.success = update_success
    monkeypatch.setattr(script, "update_record", update)

    result = script.fix_record(record, context, True, "xml")

    if status == "FAILED":
        assert result == "failed"
        lookup.assert_not_called()
        update.assert_not_called()
    else:
        assert result == ("updated" if update_success else "failed")
        lookup.assert_called_once_with("old:1", record_type="diva-oldRecord", context=context)
        assert record.findtext("data/output/recordInfo/oldRecord/linkedRecordId") == "existing-old-record"


@patch(
    "scripts.one_off.CORA_3812_update_existing_output_with_old_record.read_source_xml"
)
def test_get_old_record_loads_xml_for_old_id(mock_read_source_xml):
    old_id = "fedora-id"
    mock_read_source_xml.return_value = ET.fromstring(
        "<record><id>fedora-id</id></record>"
    )

    old_record = _get_old_record_xml(old_id, "data/fedora_xml/nordiskamuseet")

    mock_read_source_xml.assert_called_once_with(
        Path("data/fedora_xml/nordiskamuseet/fedora-id.xml")
    )
    assert old_record.findtext("id") == old_id
