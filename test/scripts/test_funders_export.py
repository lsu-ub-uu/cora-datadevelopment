from argparse import Namespace
from unittest.mock import patch
import xml.etree.ElementTree as ET
import pytest
from scripts.funders_export import main
from datetime import datetime


@patch("scripts.funders_export.get_funders")
@patch("scripts.funders_export.save_to_file")
@patch("scripts.funders_export._get_now")
@patch("builtins.print")
@patch("scripts.funders_export.create_argument_parser")
def test_funders_export(
    mock_create_argument_parser,
    mock_print,
    mock_get_now,
    mock_save_to_file,
    mock_get_funders,
):
    mock_create_argument_parser.return_value.parse_args.return_value = Namespace(
        db_user="testuser",
        db_password="testpassword",
    )
    mock_funders = ET.Element("FUNDERS")
    mock_get_funders.return_value = mock_funders
    mock_get_now.return_value = datetime(2023, 1, 1, 12, 0, 0)

    main()

    mock_get_funders.assert_called_once_with(
        db_user="testuser", db_password="testpassword"
    )
    mock_save_to_file.assert_called_once_with(
        mock_funders, "data/db_xml/funders_2023-01-01T12:00:00.xml"
    )
    mock_print.assert_any_call("Password entered. Starting export...")
    mock_print.assert_any_call(
        "--- Successfully exported funders to data/db_xml/funders_2023-01-01T12:00:00.xml ---"
    )


@patch("scripts.funders_export.get_funders")
@patch("scripts.funders_export.save_to_file")
@patch("scripts.funders_export.create_argument_parser")
def test_database_query_failed(
    mock_create_argument_parser, mock_save_to_file, mock_get_funders
):
    mock_create_argument_parser.return_value.parse_args.return_value = Namespace(
        db_user="testuser",
        db_password="testpassword",
    )
    mock_get_funders.side_effect = Exception("Database query failed")

    with pytest.raises(Exception):
        main()

    mock_save_to_file.assert_not_called()


@patch("scripts.funders_export.get_funders")
@patch("scripts.funders_export.save_to_file")
@patch("scripts.funders_export.create_argument_parser")
def test_failed_to_save_file(
    mock_create_argument_parser, mock_save_to_file, mock_get_funders
):
    mock_create_argument_parser.return_value.parse_args.return_value = Namespace(
        db_user="testuser",
        db_password="testpassword",
    )
    mock_save_to_file.side_effect = Exception("Failed to save file")

    with pytest.raises(Exception):
        main()
