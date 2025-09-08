import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch

import pytest

from cora.context import MockContext
from scripts.subjects_import import subjects_import


@patch("scripts.subjects_import.create_record_list")
@patch("scripts.subjects_import.validate_record_list")
@patch("scripts.subjects_import.common_data.read_source_xml")
def test_subjects_import_does_not_create_when_apply_false(
    mock_read_source_xml, mock_validate_record_list, mock_create_record_list
):

    # Setup mock return values
    mock_read_source_xml.return_value = ET.fromstring(mock_source_xml)
    mock_validate_record_list.return_value = [(True, None), (True, None), (True, None)]

    subjects_import(MockContext(), "some/path.xml", False)

    mock_create_record_list.assert_not_called()


@patch("scripts.subjects_import.create_record_list")
@patch("scripts.subjects_import.validate_record_list")
@patch("scripts.subjects_import.common_data.read_source_xml")
def test_subjects_import_does_not_create_when_apply_true_and_not_valid(
    mock_read_source_xml, mock_validate_record_list, mock_create_record_list
):

    mock_read_source_xml.return_value = ET.fromstring(mock_source_xml)
    mock_validate_record_list.return_value = [
        (True, None),
        (False, ["error"]),
        (True, None),
    ]

    subjects_import(MockContext(), "some/path.xml", True)

    mock_create_record_list.assert_not_called()


@patch("scripts.subjects_import.create_record_list")
@patch("scripts.subjects_import.validate_record_list")
@patch("scripts.subjects_import.common_data.read_source_xml")
def test_subjects_import_when_apply_true_and_valid(
    mock_read_source_xml, mock_validate_record_list, mock_create_record_list
):

    mock_read_source_xml.return_value = ET.fromstring(mock_source_xml)
    mock_validate_record_list.return_value = [
        (True, None),
        (True, None),
        (True, None),
    ]

    subjects_import(MockContext(), "some/path.xml", True)

    mock_create_record_list.assert_called_once()
    transformed_records = mock_create_record_list.call_args.args[0]
    assert len(transformed_records) == 3


mock_source_xml = """<?xml version="1.0" encoding="UTF-8"?>
<SELECT>
    <DATA_RECORD>
    <domain>varldskulturmuseerna</domain>
    <old_id>40100</old_id>
    <end_date></end_date>
    <name_swe>Hotade kulturarv</name_swe>
    <name_eng>Hotade kulturarv</name_eng>
    <broader_id></broader_id>
    <parent_subject_id></parent_subject_id>
    <earlier_id></earlier_id>
  </DATA_RECORD>
  <DATA_RECORD>
    <domain>varldskulturmuseerna</domain>
    <old_id>40101</old_id>
    <end_date></end_date>
    <name_swe>Proveniens och repatriering</name_swe>
    <name_eng>Proveniens och repatriering</name_eng>
    <broader_id></broader_id>
    <parent_subject_id></parent_subject_id>
    <earlier_id></earlier_id>
  </DATA_RECORD>
  <DATA_RECORD>
    <domain>varldskulturmuseerna</domain>
    <old_id>40103</old_id>
    <end_date></end_date>
    <name_swe>Digital humaniora</name_swe>
    <name_eng>Digital humaniora</name_eng>
    <broader_id></broader_id>
    <parent_subject_id></parent_subject_id>
    <earlier_id></earlier_id>
  </DATA_RECORD>
</SELECT>

"""


@patch("scripts.subjects_import.common_data.read_source_xml")
@patch("scripts.subjects_import.validate_record_list")
@patch("scripts.subjects_import.create_record_list")
def test_subjects_import_raises_error_when_invalid_source_data(
    mock_create_record_list, mock_validate_record_list, mock_read_source_xml
):
    subject_xml = ET.fromstring(
        """<?xml version="1.0" encoding="UTF-8"?>
        <SELECT>
            <DATA_RECORD>
                <domain>varldskulturmuseerna</domain>
                <old_id>40100</old_id>
                <end_date></end_date>
                <name_swe>Hotade kulturarv</name_swe>
                <name_eng>Hotade kulturarv</name_eng>
                <broader_id></broader_id>
                <parent_subject_id></parent_subject_id>
                <earlier_id></earlier_id>                
                <SOME_UNKNOWN_ELEMENT>Some unhandled value</SOME_UNKNOWN_ELEMENT>
            </DATA_RECORD>
            <DATA_RECORD>
                <domain>varldskulturmuseerna</domain>
                <old_id>40101</old_id>
                <end_date></end_date>
                <name_swe>Proveniens och repatriering</name_swe>
                <name_eng>Proveniens och repatriering</name_eng>
                <broader_id></broader_id>
                <parent_subject_id></parent_subject_id>
                <earlier_id></earlier_id>                
                <SOME_OTHER_UNKNOWN_ELEMENT>Some other unhandled value</SOME_OTHER_UNKNOWN_ELEMENT>
            </DATA_RECORD>
            <DATA_RECORD>
               <domain>varldskulturmuseerna</domain>
                <old_id>40103</old_id>
                <end_date></end_date>
                <name_swe>Digital humaniora</name_swe>
                <name_eng>Digital humaniora</name_eng>
                <broader_id></broader_id>
                <parent_subject_id></parent_subject_id>
                <earlier_id></earlier_id>
            </DATA_RECORD>
        </SELECT>
        """
    )

    mock_read_source_xml.return_value = subject_xml
    mock_validate_record_list.return_value = [(True, None), (True, None)]
    mock_context = MockContext()

    with pytest.raises(Exception):
        subjects_import(mock_context, "some/path", True)

    mock_validate_record_list.assert_not_called()
    mock_create_record_list.assert_not_called()
    mock_context.log.assert_any_call(  # pyright: ignore[reportAttributeAccessIssue]
        "Error transforming record with oldId 40100: Unknown child element <SOME_UNKNOWN_ELEMENT> found in <DATA_RECORD>",
        "error",
    )
    mock_context.log.assert_any_call(  # pyright: ignore[reportAttributeAccessIssue]
        "Error transforming record with oldId 40101: Unknown child element <SOME_OTHER_UNKNOWN_ELEMENT> found in <DATA_RECORD>",
        "error",
    )
