import pytest
from unittest.mock import patch
from requests.exceptions import HTTPError

from classic.get_authority_person import get_authority_person


@patch("classic.get_authority_person.os.getenv", return_value=None)
def test_raises_value_error_when_no_authority_service_url_from_param_or_env(
    mock_getenv,
):
    with pytest.raises(
        ValueError, match="AUTHORITY_SERVICE_URL environment variable is not set"
    ):
        get_authority_person("some_authority_pid")


@patch("classic.get_authority_person.os.getenv", return_value="http://example.com")
@patch("classic.get_authority_person.requests.get")
def test_calls_api_with_url_from_env(
    mock_requests_get,
    mock_getenv,
):

    get_authority_person("some_authority_pid")
    mock_requests_get.assert_called_once_with(
        "http://example.com/authority/rest/authority/person/some_authority_pid"
    )


@patch("classic.get_authority_person.os.getenv", return_value="http://example.com")
@patch("classic.get_authority_person.requests.get")
def test_calls_api_with_url_from_param(
    mock_requests_get,
    mock_getenv,
):

    get_authority_person(
        "some_authority_pid", authority_service_url="http://urlfromparam.com"
    )
    mock_requests_get.assert_called_once_with(
        "http://urlfromparam.com/authority/rest/authority/person/some_authority_pid"
    )


def test_raises_for_non_200_status(
    requests_mock,
):
    requests_mock.get(
        "http://example.com/authority/rest/authority/person/some_authority_pid",
        status_code=404,
    )
    with pytest.raises(HTTPError):
        get_authority_person(
            "some_authority_pid", authority_service_url="http://example.com"
        )


def test_returns_json_on_success(requests_mock):
    expected_json = {"id": "some_authority_pid", "name": "Some Authority"}
    requests_mock.get(
        "http://example.com/authority/rest/authority/person/some_authority_pid",
        status_code=200,
        json=expected_json,
    )
    response = get_authority_person(
        "some_authority_pid", authority_service_url="http://example.com"
    )
    assert response == expected_json
