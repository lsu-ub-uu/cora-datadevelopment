from unittest.mock import patch
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from cora.context import MockContext

from common.test_helper import assert_equal_for_xml_and_xml_string
from common.xml_utils import pretty_print_xml
from scripts.one_off.CORA_3812_update_existing_output_with_old_record import (
    _get_old_record,
    _update_record_info,
    fix_records,
)


@patch(
    "scripts.one_off.CORA_3812_update_existing_output_with_old_record._get_old_record"
)
@patch("scripts.one_off.CORA_3812_update_existing_output_with_old_record.list_records")
def test_fix_records_prints_old_ids(mock_list_records, mock_get_old_record, capsys):
    mock_list_records.return_value = [
        ET.fromstring(
            "<output><recordInfo><oldId>old-id-1</oldId></recordInfo></output>"
        ),
        ET.fromstring(
            "<output><recordInfo><oldId>old-id-2</oldId></recordInfo></output>"
        ),
    ]

    context = MockContext()
    fix_records(context, apply=False)

    mock_list_records.assert_called_once_with(context, "diva-output")
    mock_get_old_record.assert_any_call("old-id-1")
    mock_get_old_record.assert_any_call("old-id-2")
    output_lines = capsys.readouterr().out.splitlines()
    assert set(output_lines[:2]) == {"old-id-1", "old-id-2"}
    assert output_lines[2:] == [
        "==================== Summary ====================",
        "Total diva-output records: 2",
        "Not updated (dry-run mode): 2",
        "Failed: 0",
        "Skipped: 0",
        "================================================",
    ]


@patch("scripts.one_off.CORA_3812_update_existing_output_with_old_record.list_records")
def test_fix_records_requires_old_id(mock_list_records):
    mock_list_records.return_value = [ET.fromstring("<output />")]

    with pytest.raises(AssertionError, match="old_id should not be None"):
        fix_records(MockContext(), apply=False)


@patch("scripts.one_off.CORA_3812_update_existing_output_with_old_record.ET.parse")
def test_get_old_record_loads_xml_for_old_id(mock_parse):
    old_id = "fedora-id"
    mock_parse.return_value = ET.ElementTree(
        ET.fromstring("<record><id>fedora-id</id></record>")
    )

    old_record = _get_old_record(old_id)

    mock_parse.assert_called_once_with(
        Path("data/fedora_xml/nordiskamuseet/fedora-id.xml")
    )
    assert old_record.findtext("id") == old_id


def test_update_record_info():
    pid = "some_test_pid"
    record = ET.fromstring(f"""
        <output>
            <recordInfo>
            <id>some_id</id>
            <type>
                <linkedRecordType>recordType</linkedRecordType>
                <linkedRecordId>diva-output</linkedRecordId>
            </type>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>diva-output</linkedRecordId>
            </validationType>
            </recordInfo>
        </output>""")
    updated_record = _update_record_info(pid, record)
    assert_equal_for_xml_and_xml_string(
        updated_record,
        pretty_print_xml(ET.fromstring(f"""<output>
                        <recordInfo>
                            <id>some_id</id>
                            <type>
                                <linkedRecordType>recordType</linkedRecordType>
                                <linkedRecordId>diva-output</linkedRecordId>
                            </type>
                            <validationType>
                                <linkedRecordType>validationType</linkedRecordType>
                                <linkedRecordId>diva-output</linkedRecordId>
                            </validationType>
                            <oldRecord>
                                <linkedRecordType>diva-oldRecord</linkedRecordType>
                                <linkedRecordId>{pid}</linkedRecordId>
                            </oldRecord>
                        </recordInfo>
                    </output>""")),
    )
