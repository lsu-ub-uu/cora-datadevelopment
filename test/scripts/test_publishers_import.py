import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch

from cora.context import MockContext
from scripts.publishers_import import publishers_import
import common.common_data


@patch("scripts.publishers_import.create_record_list")
@patch("scripts.publishers_import.validate_record_list")
@patch("scripts.publishers_import.common_data.read_source_xml")
def test_publishers_import_does_not_create_when_apply_false(
    mock_read_source_xml, mock_validate_record_list, mock_create_record_list
):
    mock_source_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <SELECT_p_publishing_house_id_as_old_id_p_name_FROM_publishing_house_p>
            <DATA_RECORD>
                <old_id>8204</old_id>
                <name>The Society for the Study of Ethnic Relations and International Migration (ETMU)</name>
            </DATA_RECORD>
            <DATA_RECORD>
                <old_id>55</old_id>
                <name>Blackwell Publishing</name>
            </DATA_RECORD>
            <DATA_RECORD>
                <old_id>92</old_id>
                <name>Martinus Nijhoff Publishers</name>
            </DATA_RECORD>
        </SELECT_p_publishing_house_id_as_old_id_p_name_FROM_publishing_house_p>
    """

    # Setup mock return values
    mock_read_source_xml.return_value = ET.fromstring(mock_source_xml)
    mock_validate_record_list.return_value = [(True, None), (True, None), (True, None)]

    publishers_import(MockContext(), "some/path.xml", 4, False)

    mock_create_record_list.assert_not_called()


@patch("scripts.publishers_import.create_record_list")
@patch("scripts.publishers_import.validate_record_list")
@patch("scripts.publishers_import.common_data.read_source_xml")
def test_publishers_import_does_not_create_when_apply_true_and_not_valid(
    mock_read_source_xml, mock_validate_record_list, mock_create_record_list
):
    mock_source_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <SELECT_p_publishing_house_id_as_old_id_p_name_FROM_publishing_house_p>
            <DATA_RECORD>
                <old_id>8204</old_id>
                <name>The Society for the Study of Ethnic Relations and International Migration (ETMU)</name>
            </DATA_RECORD>
            <DATA_RECORD>
                <old_id>55</old_id>
                <name>Blackwell Publishing</name>
            </DATA_RECORD>
            <DATA_RECORD>
                <old_id>92</old_id>
                <name>Martinus Nijhoff Publishers</name>
            </DATA_RECORD>
        </SELECT_p_publishing_house_id_as_old_id_p_name_FROM_publishing_house_p>
    """

    mock_read_source_xml.return_value = ET.fromstring(mock_source_xml)
    mock_validate_record_list.return_value = [
        (True, None),
        (False, ["error"]),
        (True, None),
    ]

    publishers_import(MockContext(), "some/path.xml", 4, True)

    mock_create_record_list.assert_not_called()


@patch("scripts.publishers_import.create_record_list")
@patch("scripts.publishers_import.validate_record_list")
@patch("scripts.publishers_import.common_data.read_source_xml")
def test_publishers_import_when_apply_true_and_valid(
    mock_read_source_xml, mock_validate_record_list, mock_create_record_list
):
    mock_source_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <SELECT_p_publishing_house_id_as_old_id_p_name_FROM_publishing_house_p>
            <DATA_RECORD>
                <old_id>8204</old_id>
                <name>The Society for the Study of Ethnic Relations and International Migration (ETMU)</name>
            </DATA_RECORD>
            <DATA_RECORD>
                <old_id>55</old_id>
                <name>Blackwell Publishing</name>
            </DATA_RECORD>
            <DATA_RECORD>
                <old_id>92</old_id>
                <name>Martinus Nijhoff Publishers</name>
            </DATA_RECORD>
        </SELECT_p_publishing_house_id_as_old_id_p_name_FROM_publishing_house_p>
    """

    mock_read_source_xml.return_value = ET.fromstring(mock_source_xml)
    mock_validate_record_list.return_value = [
        (True, None),
        (True, None),
        (True, None),
    ]

    publishers_import(MockContext(), "some/path.xml", 4, True)

    mock_create_record_list.assert_called_once()
    transformed_records = mock_create_record_list.call_args.args[0]
    assert len(transformed_records) == 3
