from cora.get_cora_id_by_old_id import get_cora_id_by_old_id, _cache
from common.xml_utils import inline_xml_string
import pytest
from logging import Logger
from unittest.mock import MagicMock
from cora.context import MockContext


base_url = "https://pre.diva-portal.org/rest/record/"
test_token = "test-token"
mock_context = MockContext(base_url, test_token)

logger = Logger("test_logger")


def test_get_cora_id_by_old_id(requests_mock):
    old_id = "878550"
    expected_cora_id = "123"

    requests_mock.get(
        f"https://pre.diva-portal.org/rest/record/searchResult/diva-organisationSearch?searchData={create_search_data(old_id)}",
        request_headers={"Authtoken": test_token},
        text=create_mock_response(expected_cora_id),
    )

    response = get_cora_id_by_old_id(
        old_id,
        record_type="diva-organisation",
        context=mock_context,
    )
    assert requests_mock.called == True
    assert requests_mock.call_count == 1
    assert response == expected_cora_id


def test_return_cache_when_id_exists(requests_mock):
    old_id = "878550"
    expected_cora_id = "123"
    requests_mock.get(
        f"https://pre.diva-portal.org/rest/record/searchResult/diva-organisationSearch?searchData={create_search_data(old_id)}",
        request_headers={"Authtoken": test_token},
        text=create_mock_response(expected_cora_id),
    )

    response1 = get_cora_id_by_old_id(
        old_id,
        record_type="diva-organisation",
        context=mock_context,
    )
    response2 = get_cora_id_by_old_id(
        old_id,
        record_type="diva-organisation",
        context=mock_context,
    )
    assert requests_mock.call_count == 1
    assert response1 == response2 == expected_cora_id


def test_get_two_different_organisations(requests_mock):
    old_id = "878550"
    old_id2 = "878551"
    expected_cora_id = "123"
    expected_cora_id2 = "456"

    requests_mock.get(
        f"https://pre.diva-portal.org/rest/record/searchResult/diva-organisationSearch?searchData={create_search_data(old_id)}",
        request_headers={"Authtoken": test_token},
        text=create_mock_response(expected_cora_id),
    )

    requests_mock.get(
        f"https://pre.diva-portal.org/rest/record/searchResult/diva-organisationSearch?searchData={create_search_data(old_id2)}",
        request_headers={"Authtoken": test_token},
        text=create_mock_response(expected_cora_id2),
    )

    response1 = get_cora_id_by_old_id(
        old_id,
        record_type="diva-organisation",
        context=mock_context,
    )
    response2 = get_cora_id_by_old_id(
        old_id2,
        record_type="diva-organisation",
        context=mock_context,
    )
    assert requests_mock.call_count == 2
    assert response1 == expected_cora_id
    assert response2 == expected_cora_id2


def test_returns_error_text_when_no_result(requests_mock):
    old_id_not_found = "404404"

    requests_mock.get(
        f"https://pre.diva-portal.org/rest/record/searchResult/diva-organisationSearch?searchData={create_search_data(old_id_not_found)}",
        request_headers={"Authtoken": test_token},
        text="<dataList><data></data></dataList>",
    )

    response = get_cora_id_by_old_id(
        old_id_not_found,
        record_type="diva-organisation",
        context=mock_context,
    )

    assert response == "diva-organisation not found for old ID: 404404"


def test_logs_warning_and_returns_first_id_when_multiple_results(
    requests_mock,
):
    old_id_multiple = "222222"
    expected_cora_id = "123"

    requests_mock.get(
        f"https://pre.diva-portal.org/rest/record/searchResult/diva-organisationSearch",
        request_headers={"Authtoken": test_token},
        text=f"""
        <dataList>
            <data>
                <record>
                    <data>
                        <organisation>
                            <recordInfo>
                                <id>{expected_cora_id}</id>
                            </recordInfo>
                        </organisation>
                    </data>
                </record>
                <record>
                    <data>
                        <organisation>
                            <recordInfo>
                                <id>000</id>
                            </recordInfo>
                        </organisation>
                    </data>
                </record>
            </data>
        </dataList>
        """,
    )

    response = get_cora_id_by_old_id(
        old_id_multiple,
        record_type="diva-organisation",
        context=mock_context,
    )
    assert requests_mock.call_count == 1
    assert response == expected_cora_id
    mock_context.log.assert_called_with(  # type: ignore
        f"Warning: Multiple diva-organisations found for old ID '{old_id_multiple}'. Using the first one.",
        "warning",
    )


def test_raises_error_when_not_ok_response(requests_mock):
    old_id = "878550"

    requests_mock.get(
        f"https://pre.diva-portal.org/rest/record/searchResult/diva-organisationSearch",
        request_headers={"Authtoken": test_token},
        status_code=500,  # Simulating a server error
    )

    with pytest.raises(Exception) as exc_info:
        get_cora_id_by_old_id(
            old_id,
            record_type="diva-organisation",
            context=mock_context,
        )
    assert "Failed to fetch diva-organisation ID: 500" in str(exc_info.value)
    assert requests_mock.call_count == 1


@pytest.fixture(autouse=True)
def with_cache_clear():
    yield
    _cache.clear()


def create_search_data(old_id):
    return inline_xml_string(
        f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <search>
                <include>
                    <includePart>
                        <oldIdSearchTerm>{old_id}</oldIdSearchTerm>
                    </includePart>
                </include>
            </search>
        """
    )


def create_mock_response(expected_cora_id):
    return f"""
        <dataList>
            <data>
                <record>
                    <data>
                        <organisation>
                            <recordInfo>
                                <id>{expected_cora_id}</id>
                            </recordInfo>
                        </organisation>
                    </data>
                </record>
            </data>
        </dataList>
    """
