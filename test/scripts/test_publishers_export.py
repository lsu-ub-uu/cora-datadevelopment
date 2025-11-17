from unittest.mock import patch
from argparse import Namespace
import xml.etree.ElementTree as ET
import pytest
from scripts.publishers_export import main
from datetime import datetime


@patch("scripts.publishers_export.get_publishers")
@patch("scripts.publishers_export.save_to_file")
@patch("builtins.print")
@patch("scripts.publishers_export._get_now")
@patch("scripts.publishers_export.create_argument_parser")
def test_publishers_export(
    mock_create_argument_parser,
    mock_get_now,
    mock_print,
    mock_save_to_file,
    mock_get_publishers,
):
    mock_create_argument_parser.return_value.parse_args.return_value = Namespace(
        db_user="testuser",
        db_password="testpassword",
    )
    mock_publishers = ET.Element("PUBLISHERS")
    mock_get_publishers.return_value = mock_publishers
    mock_get_now.return_value = datetime(2023, 1, 1, 12, 0, 0)

    main()

    mock_get_publishers.assert_called_once_with(
        db_user="testuser", db_password="testpassword"
    )
    mock_save_to_file.assert_called_once_with(
        mock_publishers, "data/db_xml/publishers_2023-01-01T12:00:00.xml"
    )
    mock_print.assert_any_call("Password entered. Starting export...")
    mock_print.assert_any_call(
        "--- Successfully exported publishers to data/db_xml/publishers_2023-01-01T12:00:00.xml ---"
    )


@patch("scripts.publishers_export.get_publishers")
@patch("scripts.publishers_export.save_to_file")
@patch("builtins.print")
@patch("scripts.publishers_export.create_argument_parser")
def test_publishers_export_no_user(
    mock_input,
    mock_getpass,
    mock_print,
    mock_save_to_file,
    mock_get_publishers,
    mock_create_argument_parser,
):
    mock_create_argument_parser.return_value.parse_args.return_value = Namespace(
        db_user="",
        db_password="testpassword",
    )

    main()

    mock_print.assert_any_call("No DB user entered")
    mock_get_publishers.assert_not_called()
    mock_save_to_file.assert_not_called()


@patch("scripts.publishers_export.get_publishers")
@patch("scripts.publishers_export.save_to_file")
@patch("builtins.print")
@patch("getpass.getpass")
@patch("builtins.input")
def test_publishers_export_no_password(
    mock_input, mock_getpass, mock_print, mock_save_to_file, mock_get_publishers
):
    mock_input.return_value = "testuser"
    mock_getpass.return_value = None

    main()

    mock_print.assert_any_call("No password entered")
    mock_get_publishers.assert_not_called()
    mock_save_to_file.assert_not_called()


@patch("scripts.publishers_export.get_publishers")
@patch("scripts.publishers_export.save_to_file")
@patch("builtins.print")
@patch("getpass.getpass")
@patch("builtins.input")
def test_publishers_export_empty_password(
    mock_input, mock_getpass, mock_print, mock_save_to_file, mock_get_publishers
):
    mock_input.return_value = "testuser"
    mock_getpass.return_value = ""

    main()

    mock_print.assert_any_call("No password entered")
    mock_get_publishers.assert_not_called()
    mock_save_to_file.assert_not_called()


@patch("scripts.publishers_export.get_publishers")
@patch("scripts.publishers_export.save_to_file")
@patch("getpass.getpass")
@patch("builtins.input")
def test_database_query_failed(
    mock_input, mock_getpass, mock_save_to_file, mock_get_publishers
):
    mock_input.return_value = "testuser"
    mock_getpass.return_value = "testpassword"
    mock_get_publishers.side_effect = Exception("Database query failed")

    with pytest.raises(Exception):
        main()

    mock_save_to_file.assert_not_called()


@patch("scripts.publishers_export.get_publishers")
@patch("scripts.publishers_export.save_to_file")
@patch("getpass.getpass")
@patch("builtins.input")
def test_failed_to_save_file(
    mock_input, mock_getpass, mock_save_to_file, mock_get_publishers
):
    mock_input.return_value = "testuser"
    mock_getpass.return_value = "testpassword"
    mock_save_to_file.side_effect = Exception("Failed to save file")

    with pytest.raises(Exception):
        main()
