import xml.etree.ElementTree as ET
from unittest.mock import patch

from cora.context import MockContext
from scripts.one_off.CORA_3812_unpublish_old_record_binaries import fix_record


@patch("scripts.one_off.CORA_3812_unpublish_old_record_binaries.update_record")
@patch("scripts.one_off.CORA_3812_unpublish_old_record_binaries.get_record")
def test_fix_record_sets_binary_visibility_to_unpublished(
    mock_get_record, mock_update_record
):
    old_record = ET.fromstring(
        """
        <record>
            <data>
                <oldRecord>
                    <record>
                        <linkedRecordId>binary-123</linkedRecordId>
                    </record>
                </oldRecord>
            </data>
        </record>
        """
    )
    binary = ET.fromstring(
        """
        <record>
            <data>
                <binary>
                    <recordInfo><visibility>published</visibility></recordInfo>
                </binary>
            </data>
        </record>
        """
    )
    mock_get_record.return_value = binary
    mock_update_record.return_value.success = True
    context = MockContext()

    result = fix_record(old_record, context, apply=True)

    assert result == "updated"
    mock_get_record.assert_called_once_with(context, "binary", "binary-123")
    assert binary.findtext("./data/binary/recordInfo/visibility") == "unpublished"
    mock_update_record.assert_called_once_with(binary, context)