import xml.etree.ElementTree as ET
from unittest.mock import patch

from cora.context import MockContext
from scripts.funders_import import funders_import

funder_xml = ET.fromstring(
    """<?xml version="1.0" encoding="UTF-8"?>
        <SELECT_f_funder_id_as_old_id_f_funder_name_as_name_swe_fn_funder_name_as_name_eng_f_closed_date_as_end_date_f_orgnumber_as_identifier_organisationNumber_f_doi_as_identifier_doi_f_funder_name_locale_as_locale_swe_fn_locale_as_locale_eng_fn_funder_name_id_from_funder_f_left_join_funder_name_fn_on_f_funder_id_fn_funder_id_>
            <DATA_RECORD>
                <old_id>103</old_id>
                <name_swe>Sida - Styrelsen för internationellt utvecklingssamarbete</name_swe>
                <name_eng>Sida - Swedish International Development Cooperation Agency</name_eng>
                <end_date></end_date>
                <identifier_organisationNumber>202100-4789</identifier_organisationNumber>
                <identifier_doi>10.13039/100004441</identifier_doi>
                <locale_swe>sv</locale_swe>
                <locale_eng>en</locale_eng>
                <funder_name_id>15</funder_name_id>
            </DATA_RECORD>
            <DATA_RECORD>
                <old_id>99</old_id>
                <name_swe>Cancerfonden</name_swe>
                <name_eng>Swedish Cancer Society</name_eng>
                <end_date></end_date>
                <identifier_organisationNumber>802005-3370</identifier_organisationNumber>
                <identifier_doi>10.13039/501100002794</identifier_doi>
                <locale_swe>sv</locale_swe>
                <locale_eng>en</locale_eng>
                <funder_name_id>12</funder_name_id>
            </DATA_RECORD>
        </SELECT_f_funder_id_as_old_id_f_funder_name_as_name_swe_fn_funder_name_as_name_eng_f_closed_date_as_end_date_f_orgnumber_as_identifier_organisationNumber_f_doi_as_identifier_doi_f_funder_name_locale_as_locale_swe_fn_locale_as_locale_eng_fn_funder_name_id_from_funder_f_left_join_funder_name_fn_on_f_funder_id_fn_funder_id_>
        """
)


@patch("scripts.funders_import.common_data.read_source_xml")
@patch("scripts.funders_import.validate_record_list")
@patch("scripts.funders_import.create_record_list")
def test_funders_import_does_not_create_records_when_not_apply(
    mock_create_record_list, mock_validate_record_list, mock_read_source_xml
):
    mock_read_source_xml.return_value = funder_xml
    mock_validate_record_list.return_value = [(True, None), (True, None)]

    funders_import("some/path", 16, MockContext(), False)

    mock_validate_record_list.assert_called_once()
    mock_create_record_list.assert_not_called()


@patch("scripts.funders_import.common_data.read_source_xml")
@patch("scripts.funders_import.validate_record_list")
@patch("scripts.funders_import.create_record_list")
def test_funders_import_does_not_create_records_when_invalid(
    mock_create_record_list, mock_validate_record_list, mock_read_source_xml
):
    mock_read_source_xml.return_value = funder_xml
    mock_validate_record_list.return_value = [(True, None), (False, ["Invalid record"])]

    funders_import("some/path", 16, MockContext(), True)

    mock_validate_record_list.assert_called_once()
    mock_create_record_list.assert_not_called()


@patch("scripts.funders_import.common_data.read_source_xml")
@patch("scripts.funders_import.validate_record_list")
@patch("scripts.funders_import.create_record_list")
def test_funders_import_does_create_records_when_valid_and_apply(
    mock_create_record_list, mock_validate_record_list, mock_read_source_xml
):
    mock_read_source_xml.return_value = funder_xml
    mock_validate_record_list.return_value = [(True, None), (True, None)]

    funders_import("some/path", 16, MockContext(), True)

    mock_validate_record_list.assert_called_once()
    mock_create_record_list.assert_called_once()
