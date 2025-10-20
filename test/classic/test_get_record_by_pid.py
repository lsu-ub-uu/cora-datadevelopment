import re

from xml.etree import ElementTree as ET
from classic.get_classic_publications import _get_record_by_pid
from unittest.mock import MagicMock
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_get_record_by_pid_calls_on_success(requests_mock):
    pid = "some-pid"
    requests_mock.get(
        re.compile(f"https?://[^/]+/fedora/get/{pid}/MODEL_NOREF"),
        text="<record></record>",
    )
    mock_on_success = MagicMock()
    mock_on_error = MagicMock()

    _get_record_by_pid(pid, on_success=mock_on_success, on_error=mock_on_error)

    # assert_equal_for_xml_and_xml_string(result, "<record></record>")
    mock_on_success.assert_called_once()
    assert mock_on_success.call_args[0][0] == pid
    assert_equal_for_xml_and_xml_string(
        mock_on_success.call_args[0][1], "<record></record>"
    )
    mock_on_error.assert_not_called()


def test_get_record_by_pid_calls_on_error(requests_mock):
    pid = "some-pid"

    requests_mock.get(
        re.compile(f"https?://[^/]+/fedora/get/{pid}/MODEL_NOREF"),
        status_code=404,
        text="Not Found",
    )
    mock_on_success = MagicMock()
    mock_on_error = MagicMock()

    _get_record_by_pid(pid, on_success=mock_on_success, on_error=mock_on_error)

    mock_on_success.assert_not_called()
    mock_on_error.assert_called_once()
    assert (
        mock_on_error.call_args[0][0] == f"Error fetching record {pid}: 404 - Not Found"
    )
