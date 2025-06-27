from cora.get_organisation_by_old_id import get_organisation_id_by_old_id, _cache
from common.xml_utils import inline_xml_string
import pytest
from cora.error import LinkedRecordNotFoundError
from logging import Logger
from unittest.mock import MagicMock

base_url = "https://pre.diva-portal.org/rest/record/"
test_token = "test-token"

logger = Logger("test_logger")


def test_get_organisation_by_old_id(requests_mock):
    old_id = "878550"
    expected_cora_id = "123"

    requests_mock.get(
        f"https://pre.diva-portal.org/rest/record/searchResult/diva-organisationSearch?searchData={create_search_data(old_id)}",
        request_headers={"Authtoken": test_token},
        text=create_mock_response(expected_cora_id),
    )

    response = get_organisation_id_by_old_id(
        old_id, base_url=base_url, auth_token=test_token, logger=logger
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

    response1 = get_organisation_id_by_old_id(
        old_id, base_url=base_url, auth_token=test_token, logger=logger
    )
    response2 = get_organisation_id_by_old_id(
        old_id, base_url=base_url, auth_token=test_token, logger=logger
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

    response1 = get_organisation_id_by_old_id(
        old_id, base_url=base_url, auth_token=test_token, logger=logger
    )
    response2 = get_organisation_id_by_old_id(
        old_id2, base_url=base_url, auth_token=test_token, logger=logger
    )
    assert requests_mock.call_count == 2
    assert response1 == expected_cora_id
    assert response2 == expected_cora_id2


def test_raises_error_when_no_result(requests_mock):
    old_id_not_found = "404404"

    requests_mock.get(
        f"https://pre.diva-portal.org/rest/record/searchResult/diva-organisationSearch?searchData={create_search_data(old_id_not_found)}",
        request_headers={"Authtoken": test_token},
        text="<dataList><data></data></dataList>",
    )

    with pytest.raises(LinkedRecordNotFoundError) as exc_info:
        get_organisation_id_by_old_id(
            old_id_not_found, base_url=base_url, auth_token=test_token, logger=logger
        )
    assert "diva-organisation not found for old ID: 404404" == str(exc_info.value)
    assert requests_mock.call_count == 1


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

    mock_logger = MagicMock(spec=Logger)

    response = get_organisation_id_by_old_id(
        old_id_multiple, base_url=base_url, auth_token=test_token, logger=mock_logger
    )
    assert requests_mock.call_count == 1
    assert response == expected_cora_id  # Assuming the first ID is returned
    mock_logger.warning.assert_called_once_with(
        f"Warning: Multiple organisations found for old ID '{old_id_multiple}'. Using the first one."
    )


def test_raises_error_when_not_ok_response(requests_mock):
    old_id = "878550"

    requests_mock.get(
        f"https://pre.diva-portal.org/rest/record/searchResult/diva-organisationSearch",
        request_headers={"Authtoken": test_token},
        status_code=500,  # Simulating a server error
    )

    with pytest.raises(Exception) as exc_info:
        get_organisation_id_by_old_id(
            old_id, base_url=base_url, auth_token=test_token, logger=logger
        )
    assert "Failed to fetch organisation ID: 500" in str(exc_info.value)
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
