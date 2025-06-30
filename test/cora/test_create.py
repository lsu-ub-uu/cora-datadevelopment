from cora.create import create_record
from cora.context import MockContext
import xml.etree.ElementTree as ET
from common.xml_utils import inline_xml_string


def test_create_record_success(requests_mock):
    base_url = "https://mock.diva-portal.org/rest/record/"
    auth_token = "mock-token"
    record_type = "someRecordType"

    mock_context = MockContext(base_url, auth_token)
    requests_mock.post(base_url + record_type, status_code=201)

    record = ET.fromstring("<record><title>Test Record</title></record>")

    success, errors = create_record(
        record, record_type=record_type, context=mock_context
    )

    assert requests_mock.call_count == 1
    assert requests_mock.last_request.method == "POST"
    assert requests_mock.last_request.url == f"{base_url}{record_type}"
    assert requests_mock.last_request.headers["Authtoken"] == auth_token
    assert (
        requests_mock.last_request.headers["Content-Type"]
        == "application/vnd.cora.recordgroup+xml"
    )
    assert (
        requests_mock.last_request.headers["Accept"]
        == "application/vnd.cora.record+xml"
    )
    assert inline_xml_string(requests_mock.last_request.text) == inline_xml_string(
        '<?xml version="1.0" encoding="UTF-8"?><record><title>Test Record</title></record>'
    )
    assert success is True
    assert errors is None


def test_create_recrord_not_201(requests_mock):
    base_url = "https://mock.diva-portal.org/rest/record/"
    auth_token = "mock-token"
    record_type = "someRecordType"

    mock_context = MockContext(base_url, auth_token)

    requests_mock.post(
        base_url + record_type, status_code=500, text="Internal Server Error"
    )

    record = ET.fromstring("<record><title>Test Record</title></record>")

    success, errors = create_record(
        record, record_type=record_type, context=mock_context
    )

    assert success is False
    assert errors == ["Failed to create record with status 500: Internal Server Error"]
    mock_context.log.assert_called_with(  # type: ignore
        f"❌ Failed to create record for {record_type} with oldId N/A. \n\nStatus: 500\nInternal Server Error\n",
        "error",
    )
