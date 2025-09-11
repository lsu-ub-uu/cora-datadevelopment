from unittest.mock import patch
import xml.etree.ElementTree as ET
import pytest
from scripts.journals_export import main
from datetime import datetime


@patch("scripts.journals_export.get_journals")
@patch("scripts.journals_export.save_to_file")
@patch("scripts.journals_export._get_now")
@patch("builtins.print")
@patch("getpass.getpass")
@patch("builtins.input")
def test_journals_export(
    mock_input,
    mock_getpass,
    mock_print,
    mock_get_now,
    mock_save_to_file,
    mock_get_journals,
):
    mock_input.return_value = "testuser"
    mock_getpass.return_value = "testpassword"
    mock_journals = ET.Element("JOURNALS")
    mock_get_journals.return_value = mock_journals
    mock_get_now.return_value = datetime(2023, 1, 1, 12, 0, 0)

    main()

    mock_input.assert_called_once_with("Enter DB user: ")
    mock_getpass.assert_called_once_with("Enter DB password: ")
    mock_get_journals.assert_called_once_with(
        db_user="testuser", db_password="testpassword"
    )
    mock_save_to_file.assert_called_once_with(
        mock_journals, "data/db_xml/journals_2023-01-01T12:00:00.xml"
    )
    mock_print.assert_any_call("Password entered. Starting export...")
    mock_print.assert_any_call(
        "--- Successfully exported journals to data/db_xml/journals_2023-01-01T12:00:00.xml ---"
    )


@patch("scripts.journals_export.get_journals")
@patch("scripts.journals_export.save_to_file")
@patch("builtins.print")
@patch("getpass.getpass")
@patch("builtins.input")
def test_journals_export_no_user(
    mock_input, mock_getpass, mock_print, mock_save_to_file, mock_get_journals
):
    mock_input.return_value = None
    mock_getpass.return_value = "testpassword"

    main()

    mock_print.assert_any_call("No DB user entered")
    mock_get_journals.assert_not_called()
    mock_save_to_file.assert_not_called()


@patch("scripts.journals_export.get_journals")
@patch("scripts.journals_export.save_to_file")
@patch("builtins.print")
@patch("getpass.getpass")
@patch("builtins.input")
def test_journals_export_no_password(
    mock_input, mock_getpass, mock_print, mock_save_to_file, mock_get_journals
):
    mock_input.return_value = "testuser"
    mock_getpass.return_value = None

    main()

    mock_print.assert_any_call("No password entered")
    mock_get_journals.assert_not_called()
    mock_save_to_file.assert_not_called()


@patch("scripts.journals_export.get_journals")
@patch("scripts.journals_export.save_to_file")
@patch("builtins.print")
@patch("getpass.getpass")
@patch("builtins.input")
def test_journals_export_empty_password(
    mock_input, mock_getpass, mock_print, mock_save_to_file, mock_get_journals
):
    mock_input.return_value = "testuser"
    mock_getpass.return_value = ""

    main()

    mock_print.assert_any_call("No password entered")
    mock_get_journals.assert_not_called()
    mock_save_to_file.assert_not_called()


@patch("scripts.journals_export.get_journals")
@patch("scripts.journals_export.save_to_file")
@patch("getpass.getpass")
@patch("builtins.input")
def test_database_query_failed(
    mock_input, mock_getpass, mock_save_to_file, mock_get_journals
):
    mock_input.return_value = "testuser"
    mock_getpass.return_value = "testpassword"
    mock_get_journals.side_effect = Exception("Database query failed")

    with pytest.raises(Exception):
        main()

    mock_save_to_file.assert_not_called()


@patch("scripts.journals_export.get_journals")
@patch("scripts.journals_export.save_to_file")
@patch("getpass.getpass")
@patch("builtins.input")
def test_failed_to_save_file(
    mock_input, mock_getpass, mock_save_to_file, mock_get_journals
):
    mock_input.return_value = "testuser"
    mock_getpass.return_value = "testpassword"
    mock_save_to_file.side_effect = Exception("Failed to save file")

    with pytest.raises(Exception):
        main()
