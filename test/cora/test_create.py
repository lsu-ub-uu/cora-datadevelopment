from cora.create import create_record
from cora.context import MockContext
import xml.etree.ElementTree as ET
from common.xml_utils import inline_xml_string
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_record_success(requests_mock):
    base_url = "https://mock.diva-portal.org/rest/record/"
    auth_token = "mock-token"
    record_type = "someRecordType"

    mock_context = MockContext(base_url, auth_token)
    requests_mock.post(
        base_url + record_type,
        status_code=201,
        text="<output><data><recordInfo><id>12345</id></recordInfo></data></output>",
    )

    record = ET.fromstring("<record><title>Test Record</title></record>")

    result = create_record(record, record_type=record_type, context=mock_context)

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
    assert result.success is True
    assert result.error is None
    assert result.record_id == "12345"
    assert_equal_for_xml_and_xml_string(
        result.response_data,
        "<output><data><recordInfo><id>12345</id></recordInfo></data></output>",
    )


def test_create_record_not_201(requests_mock, caplog):
    base_url = "https://mock.diva-portal.org/rest/record/"
    auth_token = "mock-token"
    record_type = "someRecordType"

    mock_context = MockContext(base_url, auth_token)

    requests_mock.post(
        base_url + record_type, status_code=500, text="Internal Server Error"
    )

    record = ET.fromstring("<record><title>Test Record</title></record>")

    result = create_record(record, record_type=record_type, context=mock_context)

    assert result.success is False
    assert (
        result.error == "Failed to create record with status 500: Internal Server Error"
    )

    assert (
        "ERROR",
        f"❌ Failed to create record for {record_type} with oldId N/A. \n\nStatus: 500\nInternal Server Error\n",
    ) in [(record.levelname, record.getMessage()) for record in caplog.records]
