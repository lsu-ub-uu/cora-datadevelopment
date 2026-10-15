from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET

from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
from scripts.one_off.CORA_3835_update_binaries_with_status import fix_records


@patch("scripts.one_off.CORA_3835_update_binaries_with_status.list_records")
@patch("scripts.one_off.CORA_3835_update_binaries_with_status.update_record")
@patch("scripts.one_off.CORA_3835_update_binaries_with_status.run_with_threads")
def test_updates_binary_records_with_done_status(
    mock_run_with_threads, mock_update_record, mock_list_records
):
    mock_run_with_threads.side_effect = lambda iterable, function, *args: [
        function(item) for item in iterable
    ]
    mock_update_record.return_value = Mock(success=True)
    mock_list_records.return_value = [ET.fromstring("""
            <record>
                <data>
                    <binary type="generic">
                        <recordInfo>
                            <id>binary-1</id>
                        </recordInfo>
                    </binary>
                </data>
            </record>
            """)]

    context = MockContext()
    fix_records(context)

    mock_list_records.assert_called_once_with(context, "binary")
    mock_update_record.assert_called_once()
    assert_equal_for_xml_and_xml_string(
        mock_update_record.call_args.args[0],
        """
        <record>
            <data>
                <binary type="generic">
                    <recordInfo>
                        <id>binary-1</id>
                        <status>done</status>
                    </recordInfo>
                </binary>
            </data>
        </record>
        """,
    )


@patch("scripts.one_off.CORA_3835_update_binaries_with_status.list_records")
@patch("scripts.one_off.CORA_3835_update_binaries_with_status.update_record")
@patch("scripts.one_off.CORA_3835_update_binaries_with_status.run_with_threads")
def test_skips_binary_record_that_has_status(
    mock_run_with_threads, mock_update_record, mock_list_records
):
    mock_run_with_threads.side_effect = lambda iterable, function, *args: [
        function(item) for item in iterable
    ]
    mock_update_record.return_value = Mock(success=True)
    mock_list_records.return_value = [ET.fromstring("""
            <record>
                <data>
                    <binary type="generic">
                        <recordInfo>
                            <id>binary-1</id>
                            <status>someStatus</status>
                        </recordInfo>
                    </binary>
                </data>
            </record>
            """)]

    context = MockContext()
    fix_records(context)

    mock_list_records.assert_called_once_with(context, "binary")
    mock_update_record.assert_not_called()
