import xml.etree.ElementTree as ET
from unittest.mock import  patch

import pytest

from cora.context import MockContext
from scripts.series_import import series_import


@patch("scripts.series_import.create_record_list")
@patch("scripts.series_import.validate_record_list")
@patch("scripts.series_import.common_data.read_source_xml")
def test_series_import_does_not_create_when_apply_false(
    mock_read_source_xml, mock_validate_record_list, mock_create_record_list
):
    mock_read_source_xml.return_value = ET.fromstring(mock_source_xml)
    mock_validate_record_list.return_value = [(True, None), (True, None)]

    series_import(MockContext(), "some/path.xml", False)

    mock_create_record_list.assert_not_called()


@patch("scripts.series_import.create_record_list")
@patch("scripts.series_import.validate_record_list")
@patch("scripts.series_import.common_data.read_source_xml")
def test_series_import_does_not_create_when_apply_true_and_not_valid(
    mock_read_source_xml, mock_validate_record_list, mock_create_record_list
):

    mock_read_source_xml.return_value = ET.fromstring(mock_source_xml)
    mock_validate_record_list.return_value = [
        (True, None),
        (False, ["error"]),
    ]

    series_import(MockContext(), "some/path.xml", True)

    mock_create_record_list.assert_not_called()


@patch("scripts.series_import.create_record_list")
@patch("scripts.series_import.validate_record_list")
@patch("scripts.series_import.common_data.read_source_xml")
def test_series_import_when_apply_true_and_valid(
    mock_read_source_xml, mock_validate_record_list, mock_create_record_list
):

    mock_read_source_xml.return_value = ET.fromstring(mock_source_xml)
    mock_validate_record_list.return_value = [
        (True, None),
        (True, None),
    ]

    series_import(MockContext(), "some/path.xml", True)

    mock_create_record_list.assert_called_once()
    transformed_records = mock_create_record_list.call_args.args[0]
    assert len(transformed_records) == 2


mock_source_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <SELECT_s_domain_s_series_id_as_old_id_st_main_title_as_title_st_subtitle_as_subTitle_sat_main_title_as_alternative_title_sat_subtitle_as_alternative_subtitle_s_closed_date_as_end_date_s_issn_as_identifier_pissn_s_eissn_as_identifier_eissn_s_format_id_f_format_code_s_url_s_notes_as_external_note_s_publication_type_id_pt_publication_type_code_srp_relation_type_id_srp_relative_id_as_relative_id_host_srp_series_id_sre_relation_type_id_string_agg_sre_relative_id_text_as_relative_id_preceding_sre_series_id_s_organisation_id_from_series_s_left_join_series_title_st_on_s_series_id_st_series_id_left_join_series_alternative_title_sat_on_s_series_id_sat_series_id_left_join_format_f_on_s_format_id_f_format_id_left_join_series_relation_srp_on_s_series_id_srp_series_id_and_srp_relation_type_id_52_left_join_series_relation_sre_on_s_series_id_sre_series_id_and_sre_relation_type_id_50_left_join_publication_type_pt_on_s_publication_type_id_pt_publication_type_id_borde_vara_string_agg_where_s_domain_smhi_group_by_s_domain_s_series_id_st_main_title_st_subtitle_sat_main_title_sat_subtitle_s_closed_date_s_issn_s_eissn_s_format_id_f_format_code_s_url_s_notes_s_publication_type_id_pt_publication_type_code_srp_relation_type_id_srp_relative_id_srp_series_id_sre_relation_type_id_sre_series_id_s_organisation_id>
            <DATA_RECORD>
                <domain>smhi</domain>
                <old_id>12555</old_id>
                <title>RMK, Rapport Meteorologi och Klimatologi</title>
                <subtitle></subtitle>
                <alternative_title>RMK: Report Meteorology and Climatology</alternative_title>
                <alternative_subtitle></alternative_subtitle>
                <end_date></end_date>
                <identifier_pissn>0347-2116</identifier_pissn>
                <identifier_eissn></identifier_eissn>
                <url></url>
                <external_note></external_note>
                <publication_type_id></publication_type_id>
                <relative_id_host></relative_id_host>
                <relative_id_preceding></relative_id_preceding>
                <organisation_id></organisation_id>
            </DATA_RECORD>
            <DATA_RECORD>
                <domain>smhi</domain>
                <old_id>12556</old_id>
                <title>RO, Rapport Oceanografi</title>
                <subtitle></subtitle>
                <alternative_title>RO, Report Oceanography</alternative_title>
                <alternative_subtitle></alternative_subtitle>
                <end_date></end_date>
                <identifier_pissn>0283-1112</identifier_pissn>
                <identifier_eissn></identifier_eissn>
                <url></url>
                <external_note></external_note>
                <publication_type_id></publication_type_id>
                <relative_id_host></relative_id_host>
                <relative_id_preceding></relative_id_preceding>
                <organisation_id></organisation_id>
            </DATA_RECORD>
        </SELECT_s_domain_s_series_id_as_old_id_st_main_title_as_title_st_subtitle_as_subTitle_sat_main_title_as_alternative_title_sat_subtitle_as_alternative_subtitle_s_closed_date_as_end_date_s_issn_as_identifier_pissn_s_eissn_as_identifier_eissn_s_format_id_f_format_code_s_url_s_notes_as_external_note_s_publication_type_id_pt_publication_type_code_srp_relation_type_id_srp_relative_id_as_relative_id_host_srp_series_id_sre_relation_type_id_string_agg_sre_relative_id_text_as_relative_id_preceding_sre_series_id_s_organisation_id_from_series_s_left_join_series_title_st_on_s_series_id_st_series_id_left_join_series_alternative_title_sat_on_s_series_id_sat_series_id_left_join_format_f_on_s_format_id_f_format_id_left_join_series_relation_srp_on_s_series_id_srp_series_id_and_srp_relation_type_id_52_left_join_series_relation_sre_on_s_series_id_sre_series_id_and_sre_relation_type_id_50_left_join_publication_type_pt_on_s_publication_type_id_pt_publication_type_id_borde_vara_string_agg_where_s_domain_smhi_group_by_s_domain_s_series_id_st_main_title_st_subtitle_sat_main_title_sat_subtitle_s_closed_date_s_issn_s_eissn_s_format_id_f_format_code_s_url_s_notes_s_publication_type_id_pt_publication_type_code_srp_relation_type_id_srp_relative_id_srp_series_id_sre_relation_type_id_sre_series_id_s_organisation_id>
    """


@patch("scripts.series_import.common_data.read_source_xml")
@patch("scripts.series_import.validate_record_list")
@patch("scripts.series_import.create_record_list")
def test_series_import_raises_error_when_invalid_source_data(
    mock_create_record_list, mock_validate_record_list, mock_read_source_xml
):
    series_xml = ET.fromstring(
        """<?xml version="1.0" encoding="UTF-8"?>
        <SELECT>
            <DATA_RECORD>
               <domain>norden</domain>
                <old_id>103</old_id>
                <title>Policy Papers</title>
                <subtitle></subtitle>
                <alternative_title></alternative_title>
                <alternative_subtitle></alternative_subtitle>
                <end_date></end_date>
                <identifier_pissn>1504-8640</identifier_pissn>
                <identifier_eissn></identifier_eissn>
                <url></url>
                <external_note></external_note>
                <publication_type_id></publication_type_id>
                <relative_id_host></relative_id_host>
                <relative_id_preceding></relative_id_preceding>
                <organisation_id></organisation_id>
                <SOME_UNKNOWN_ELEMENT>Some unhandled value</SOME_UNKNOWN_ELEMENT>
            </DATA_RECORD>
            <DATA_RECORD>
                <domain>norden</domain>
                <old_id>401</old_id>
                <title>Nordregio Policy Brief</title>
                <subtitle></subtitle>
                <alternative_title>Nordregio Policy Brief</alternative_title>
                <alternative_subtitle></alternative_subtitle>
                <end_date></end_date>
                <identifier_pissn>2001-3876</identifier_pissn>
                <identifier_eissn></identifier_eissn>
                <url></url>
                <external_note></external_note>
                <publication_type_id></publication_type_id>
                <relative_id_host></relative_id_host>
                <relative_id_preceding></relative_id_preceding>
                <organisation_id></organisation_id>
                <SOME_OTHER_UNKNOWN_ELEMENT>Some other unhandled value</SOME_OTHER_UNKNOWN_ELEMENT>
            </DATA_RECORD>
            <DATA_RECORD>
                <domain>norden</domain>
                <old_id>10851</old_id>
                <title>Nordregio Report</title>
                <subtitle></subtitle>
                <alternative_title>Nordregio Report</alternative_title>
                <alternative_subtitle></alternative_subtitle>
                <end_date></end_date>
                <identifier_pissn>1403-2503</identifier_pissn>
                <identifier_eissn></identifier_eissn>
                <url></url>
                <external_note></external_note>
                <publication_type_id></publication_type_id>
                <relative_id_host></relative_id_host>
                <relative_id_preceding></relative_id_preceding>
                <organisation_id></organisation_id>
            </DATA_RECORD>
        </SELECT>
        """
    )

    mock_read_source_xml.return_value = series_xml
    mock_validate_record_list.return_value = [(True, None), (True, None)]
    mock_context = MockContext()

    with pytest.raises(Exception):
        series_import(mock_context, "some/path", True)

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
