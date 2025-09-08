from unittest.mock import patch
import xml.etree.ElementTree as ET

import pytest
from cora.context import MockContext
from scripts.journals_import import journals_import


@patch("scripts.journals_import.common_data.read_source_xml")
@patch("scripts.journals_import.validate_record_list")
@patch("scripts.journals_import.create_record_list")
def test_journals_import_does_not_create_when_not_apply(
    mock_create_record_list, mock_validate_record_list, mock_read_source_xml
):
    mock_read_source_xml.return_value = mock_source_data

    mock_validate_record_list.return_value = [(True, None), (True, None)]

    journals_import(MockContext(), "some/data.xml", False)

    mock_create_record_list.assert_not_called()


@patch("scripts.journals_import.common_data.read_source_xml")
@patch("scripts.journals_import.validate_record_list")
@patch("scripts.journals_import.create_record_list")
def test_journals_import_does_not_create_records_when_invalid(
    mock_create_record_list, mock_validate_record_list, mock_read_source_xml
):
    mock_read_source_xml.return_value = mock_source_data

    mock_validate_record_list.return_value = [(False, "Invalid"), (True, None)]

    journals_import(MockContext(), "some/data.xml", True)

    mock_create_record_list.assert_not_called()


@patch("scripts.journals_import.common_data.read_source_xml")
@patch("scripts.journals_import.validate_record_list")
@patch("scripts.journals_import.create_record_list")
def test_journals_import_does_create_when_valid_and_apply(
    mock_create_record_list, mock_validate_record_list, mock_read_source_xml
):
    mock_read_source_xml.return_value = mock_source_data

    mock_validate_record_list.return_value = [(True, None), (True, None)]

    journals_import(MockContext(), "some/data.xml", True)

    mock_create_record_list.assert_called_once()


mock_source_data = ET.fromstring(
    """
       <SELECT>
            <DATA_RECORD>
                <old_id>12505</old_id>
                <title>Journal of Development Economics</title>
                <subtitle />
                <end_date />
                <identifier_eissn>1872-6089</identifier_eissn>
                <identifier_pissn>0304-3878</identifier_pissn>
                <url />
            </DATA_RECORD>
            <DATA_RECORD>
                <old_id>9739</old_id>
                <title>Arthritis Research &amp; Therapy</title>
                <subtitle />
                <end_date />
                <identifier_eissn>1478-6362</identifier_eissn>
                <identifier_pissn />
                <url>https://arthritis-research.biomedcentral.com/</url>
            </DATA_RECORD>
        </SELECT>
    """
)


@patch("scripts.journals_import.common_data.read_source_xml")
@patch("scripts.journals_import.validate_record_list")
@patch("scripts.journals_import.create_record_list")
def test_journals_import_raises_error_when_invalid_source_data(
    mock_create_record_list, mock_validate_record_list, mock_read_source_xml
):
    funder_xml = ET.fromstring(
        """<?xml version="1.0" encoding="UTF-8"?>
        <SELECT>
            <DATA_RECORD>
                <old_id>103</old_id>
                <title>Journal of Development Economics</title>
                <subtitle />
                <end_date />
                <identifier_eissn>1872-6089</identifier_eissn>
                <identifier_pissn>0304-3878</identifier_pissn>
                <url />
                <SOME_UNKNOWN_ELEMENT>Some unhandled value</SOME_UNKNOWN_ELEMENT>
            </DATA_RECORD>
            <DATA_RECORD>
               <old_id>401</old_id>
                <title>Journal of Development Economics</title>
                <subtitle />
                <end_date />
                <identifier_eissn>1872-6089</identifier_eissn>
                <identifier_pissn>0304-3878</identifier_pissn>
                <url />
                <SOME_OTHER_UNKNOWN_ELEMENT>Some other unhandled value</SOME_OTHER_UNKNOWN_ELEMENT>
            </DATA_RECORD>
            <DATA_RECORD>
                <old_id>200</old_id>
                <title>Journal of Development Economics</title>
                <subtitle />
                <end_date />
                <identifier_eissn>1872-6089</identifier_eissn>
                <identifier_pissn>0304-3878</identifier_pissn>
                <url />
            </DATA_RECORD>
        </SELECT>
        """
    )

    mock_read_source_xml.return_value = funder_xml
    mock_validate_record_list.return_value = [(True, None), (True, None)]
    mock_context = MockContext()

    with pytest.raises(Exception):
        journals_import(mock_context, "some/path", True)

    mock_validate_record_list.assert_not_called()
    mock_create_record_list.assert_not_called()
    mock_context.log.assert_any_call(  # pyright: ignore[reportAttributeAccessIssue]
        "Error transforming record with oldId 103: Unknown child element <SOME_UNKNOWN_ELEMENT> found in <DATA_RECORD>",
        "error",
    )
    mock_context.log.assert_any_call(  # pyright: ignore[reportAttributeAccessIssue]
        "Error transforming record with oldId 401: Unknown child element <SOME_OTHER_UNKNOWN_ELEMENT> found in <DATA_RECORD>",
        "error",
    )
