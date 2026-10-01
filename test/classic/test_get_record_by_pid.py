import re
import pytest

from xml.etree import ElementTree as ET
from classic.get_classic_publications import _get_record_by_pid
from unittest.mock import MagicMock, patch
from common.test_helper import assert_equal_for_xml_and_xml_string

FEDORA_URL = "http://localhost:8088"


def test_missing_fedora_url_fails_before_request(monkeypatch):
    monkeypatch.delenv("FEDORA_URL", raising=False)
    with patch("classic.get_classic_publications.requests.get") as request:
        with pytest.raises(ValueError, match="FEDORA_URL"):
            _get_record_by_pid("pid", MagicMock(), MagicMock(), fedora_url=None)
    request.assert_not_called()


def test_fedora_url_resolves_from_environment(monkeypatch, requests_mock):
    monkeypatch.setenv("FEDORA_URL", FEDORA_URL)
    requests_mock.get(f"{FEDORA_URL}/fedora/get/pid/MODEL_NOREF", text="<record/>")

    on_success = MagicMock()
    _get_record_by_pid("pid", on_success, MagicMock(), fedora_url=None)

    on_success.assert_called_once()


def test_get_record_by_pid_calls_on_success(requests_mock):
    pid = "some-pid"
    requests_mock.get(
        re.compile(f"https?://[^/]+/fedora/get/{pid}/MODEL_NOREF"),
        text="<record></record>",
    )
    mock_on_success = MagicMock()
    mock_on_error = MagicMock()

    _get_record_by_pid(
        pid, on_success=mock_on_success, on_error=mock_on_error, fedora_url=FEDORA_URL
    )

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

    _get_record_by_pid(
        pid, on_success=mock_on_success, on_error=mock_on_error, fedora_url=FEDORA_URL
    )

    mock_on_success.assert_not_called()
    mock_on_error.assert_called_once()
    assert (
        mock_on_error.call_args[0][0] == f"Error fetching record {pid}: 404 - Not Found"
    )
