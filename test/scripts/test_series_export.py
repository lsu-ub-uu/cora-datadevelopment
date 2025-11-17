from argparse import Namespace
from unittest.mock import patch
import xml.etree.ElementTree as ET
import pytest
from scripts.series_export import main
from datetime import datetime


@patch("scripts.series_export.get_series")
@patch("scripts.series_export.save_to_file")
@patch("scripts.series_export._get_now")
@patch("builtins.print")
@patch("scripts.series_export.create_argument_parser")
def test_series_export(
    mock_create_argument_parser,
    mock_print,
    mock_get_now,
    mock_save_to_file,
    mock_get_series,
):
    mock_create_argument_parser.return_value.parse_args.return_value = Namespace(
        domain="norden",
        db_user="testuser",
        db_password="testpassword",
    )
    mock_series = ET.Element("SERIES")
    mock_get_series.return_value = mock_series
    mock_get_now.return_value = datetime(2023, 1, 1, 12, 0, 0)

    main()

    mock_get_series.assert_called_once_with(
        domain="norden", db_user="testuser", db_password="testpassword"
    )
    mock_save_to_file.assert_called_once_with(
        mock_series, "data/db_xml/series_2023-01-01T12:00:00.xml"
    )
    mock_print.assert_any_call("Password entered. Starting export...")
    mock_print.assert_any_call(
        "--- Successfully exported series to data/db_xml/series_2023-01-01T12:00:00.xml ---"
    )


@patch("scripts.series_export.get_series")
@patch("scripts.series_export.save_to_file")
@patch("scripts.series_export.create_argument_parser")
def test_database_query_failed(
    mock_create_argument_parser,
    mock_save_to_file,
    mock_get_series,
):
    mock_create_argument_parser.return_value.parse_args.return_value = Namespace(
        domain="norden",
        db_user="testuser",
        db_password="testpassword",
    )

    mock_get_series.side_effect = Exception("Database query failed")

    with pytest.raises(Exception):
        main()

    mock_save_to_file.assert_not_called()


@patch("scripts.series_export.get_series")
@patch("scripts.series_export.save_to_file")
@patch("scripts.series_export.create_argument_parser")
def test_failed_to_save_file(
    mock_create_argument_parser,
    mock_save_to_file,
    mock_get_series,
):
    mock_create_argument_parser.return_value.parse_args.return_value = Namespace(
        domain="norden",
        db_user="testuser",
        db_password="testpassword",
    )
    mock_save_to_file.side_effect = Exception("Failed to save file")

    with pytest.raises(Exception):
        main()
