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


def test_create_record_not_201(requests_mock):
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

    mock_context.log.assert_called_with(  # type: ignore
        f"❌ Failed to create record for {record_type} with oldId N/A. \n\nStatus: 500\nInternal Server Error\n",
        "error",
    )


def test_create_record_retry_on_409_success(requests_mock):
    """Test that create_record successfully retries on 409 Conflict and succeeds on second attempt."""
    base_url = "https://mock.diva-portal.org/rest/record/"
    auth_token = "mock-token"
    record_type = "someRecordType"

    mock_context = MockContext(base_url, auth_token)

    # First call returns 409, second call returns 201
    requests_mock.post(
        base_url + record_type,
        [
            {"status_code": 409, "text": "Conflict"},
            {
                "status_code": 201,
                "text": "<output><data><recordInfo><id>12345</id></recordInfo></data></output>",
            },
        ],
    )

    record = ET.fromstring(
        "<record><oldId>test-123</oldId><title>Test Record</title></record>"
    )

    result = create_record(
        record,
        record_type=record_type,
        context=mock_context,
        max_retries=3,
        initial_delay=0.01,  # Very short delay for testing
    )

    # Should have made 2 requests
    assert requests_mock.call_count == 2

    # Should be successful
    assert result.success is True
    assert result.error is None
    assert result.record_id == "12345"

    # Should have logged the retry attempt and success
    mock_context.log.assert_any_call(  # type: ignore
        "⚠️ Conflict (409) for someRecordType with oldId test-123. Retrying in 0.01s (attempt 1/4)",
        "warning",
    )
    mock_context.log.assert_any_call(  # type: ignore
        "✅ Successfully created record for someRecordType with oldId test-123 on attempt 2",
        "info",
    )


def test_create_record_retry_on_409_max_retries_exceeded(requests_mock):
    """Test that create_record fails after max retries on repeated 409 Conflicts."""
    base_url = "https://mock.diva-portal.org/rest/record/"
    auth_token = "mock-token"
    record_type = "someRecordType"

    mock_context = MockContext(base_url, auth_token)

    # All calls return 409
    requests_mock.post(base_url + record_type, status_code=409, text="Conflict")

    record = ET.fromstring(
        "<record><oldId>test-456</oldId><title>Test Record</title></record>"
    )

    result = create_record(
        record,
        record_type=record_type,
        context=mock_context,
        max_retries=2,
        initial_delay=0.01,  # Very short delay for testing
    )

    # Should have made 3 requests (initial + 2 retries)
    assert requests_mock.call_count == 3

    # Should fail
    assert result.success is False
    assert result.error == "Failed to create record with status 409: Conflict"

    # Should have logged the retry attempts
    mock_context.log.assert_any_call(  # type: ignore
        "⚠️ Conflict (409) for someRecordType with oldId test-456. Retrying in 0.01s (attempt 1/3)",
        "warning",
    )
    mock_context.log.assert_any_call(  # type: ignore
        "⚠️ Conflict (409) for someRecordType with oldId test-456. Retrying in 0.02s (attempt 2/3)",
        "warning",
    )
