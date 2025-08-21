import xml.etree.ElementTree as ET
import pytest
from cora.context import MockContext
from cora.delete import delete_record


def test_delete_record_success(requests_mock):
    request_url = "https://mock.diva-portal.org/rest/record/someRecordType/12345"
    record = ET.fromstring(
        f"""
        <record>
            <actionLinks>
                <delete>
                    <url>{request_url}</url>
                    <method>DELETE</method>
                </delete>
            </actionLinks>
        </record>
    """
    )

    requests_mock.delete(
        request_url,
        status_code=200,
    )

    mock_context = MockContext()

    delete_record(record, mock_context)

    assert requests_mock.call_count == 1
    assert requests_mock.last_request.method == "DELETE"
    assert requests_mock.last_request.url == request_url
    assert (
        requests_mock.last_request.headers["Authtoken"] == mock_context.get_auth_token()
    )


def test_delete_record_failure(requests_mock):
    request_url = "https://mock.diva-portal.org/rest/record/someRecordType/12345"
    record = ET.fromstring(
        f"""
        <record>
            <actionLinks>
                <delete>
                    <url>{request_url}</url>
                    <method>DELETE</method>
                </delete>
            </actionLinks>
        </record>
    """
    )

    requests_mock.delete(
        request_url,
        status_code=500,
        text="Internal Server Error",
    )

    with pytest.raises(Exception) as exc_info:
        delete_record(record, MockContext())

    assert "500" in str(exc_info.value) and "Internal Server Error" in str(
        exc_info.value
    )
