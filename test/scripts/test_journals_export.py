from argparse import Namespace
from unittest.mock import patch
import xml.etree.ElementTree as ET
import pytest
from scripts.journals_export import main
from datetime import datetime


@patch("scripts.journals_export.get_journals")
@patch("scripts.journals_export.save_to_file")
@patch("scripts.journals_export._get_now")
@patch("builtins.print")
@patch("scripts.journals_export.create_argument_parser")
def test_journals_export(
    mock_create_argument_parser,
    mock_print,
    mock_get_now,
    mock_save_to_file,
    mock_get_journals,
):
    mock_create_argument_parser.return_value.parse_args.return_value = Namespace(
        db_user="testuser",
        db_password="testpassword",
    )
    mock_journals = ET.Element("JOURNALS")
    mock_get_journals.return_value = mock_journals
    mock_get_now.return_value = datetime(2023, 1, 1, 12, 0, 0)

    main()

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
@patch("scripts.journals_export.create_argument_parser")
def test_database_query_failed(
    mock_create_argument_parser, mock_save_to_file, mock_get_journals
):
    mock_create_argument_parser.return_value.parse_args.return_value = Namespace(
        db_user="testuser",
        db_password="testpassword",
    )
    mock_get_journals.side_effect = Exception("Database query failed")

    with pytest.raises(Exception):
        main()

    mock_save_to_file.assert_not_called()


@patch("scripts.journals_export.get_journals")
@patch("scripts.journals_export.save_to_file")
@patch("scripts.journals_export.create_argument_parser")
def test_failed_to_save_file(
    mock_create_argument_parser, mock_save_to_file, mock_get_journals
):
    mock_create_argument_parser.return_value.parse_args.return_value = Namespace(
        db_user="testuser",
        db_password="testpassword",
    )
    mock_save_to_file.side_effect = Exception("Failed to save file")

    with pytest.raises(Exception):
        main()
