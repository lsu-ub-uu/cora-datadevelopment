from xml.etree import ElementTree as ET

import pytest
from cora_python_client import CoraClient, CoraHTTPError, CoraRecord, CoraRecordList
from unittest.mock import Mock

from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id, _cache


def test_get_cora_id_by_old_id():
    mock_cora_client = Mock(CoraClient)
    old_id = "878550"
    expected_cora_id = "123"

    mock_cora_client.search_records.return_value = create_mock_response(
        expected_cora_id
    )

    response = get_cora_id_by_old_id(
        old_id,
        record_type="diva-organisation",
        cora_client=mock_cora_client,
    )
    mock_cora_client.search_records.assert_called_once()
    assert (
        mock_cora_client.search_records.call_args.kwargs["search_id"]
        == "diva-organisationSearch"
    )
    captured_search_data = mock_cora_client.search_records.call_args.kwargs[
        "search_data"
    ]
    assert_equal_for_xml_and_xml_string(
        captured_search_data, create_expected_search_data(old_id)
    )

    assert response == expected_cora_id


@pytest.mark.parametrize("record_id", ["old-record:123", None])
def test_get_old_record_id(record_id):
    mock_cora_client = Mock(CoraClient)
    old_id = "diva2:123"
    mock_cora_client.search_records.return_value = create_mock_response(record_id)

    result = get_cora_id_by_old_id(
        old_id, record_type="diva-oldRecord", cora_client=mock_cora_client
    )

    assert result == (record_id or f"diva-oldRecord not found for old ID: {old_id}")
    mock_cora_client.search_records.assert_called_once()
    assert (
        mock_cora_client.search_records.call_args.kwargs["search_id"]
        == "diva-oldRecordSearch"
    )


def test_return_cache_when_id_exists():
    mock_cora_client = Mock(CoraClient)
    old_id = "878550"
    expected_cora_id = "123"
    mock_cora_client.search_records.return_value = create_mock_response(
        expected_cora_id
    )

    response1 = get_cora_id_by_old_id(
        old_id,
        record_type="diva-organisation",
        cora_client=mock_cora_client,
    )
    response2 = get_cora_id_by_old_id(
        old_id,
        record_type="diva-organisation",
        cora_client=mock_cora_client,
    )
    mock_cora_client.search_records.assert_called_once()
    assert response1 == response2 == expected_cora_id


def test_get_two_different_organisations():
    mock_cora_client = Mock(CoraClient)
    old_id = "878550"
    old_id2 = "878551"
    expected_cora_id = "123"
    expected_cora_id2 = "456"
    mock_cora_client.search_records.side_effect = [
        create_mock_response(expected_cora_id),
        create_mock_response(expected_cora_id2),
    ]

    response1 = get_cora_id_by_old_id(
        old_id,
        record_type="diva-organisation",
        cora_client=mock_cora_client,
    )
    response2 = get_cora_id_by_old_id(
        old_id2,
        record_type="diva-organisation",
        cora_client=mock_cora_client,
    )
    assert mock_cora_client.search_records.call_count == 2
    assert response1 == expected_cora_id
    assert response2 == expected_cora_id2


def test_returns_error_text_when_no_result():
    mock_cora_client = Mock(CoraClient)
    old_id_not_found = "404404"
    mock_cora_client.search_records.return_value = CoraRecordList([])

    response = get_cora_id_by_old_id(
        old_id_not_found,
        record_type="diva-organisation",
        cora_client=mock_cora_client,
    )

    assert response == "diva-organisation not found for old ID: 404404"
    mock_cora_client.search_records.assert_called_once()


def test_logs_warning_and_returns_first_id_when_multiple_results(
    caplog,
):
    mock_cora_client = Mock(CoraClient)
    old_id_multiple = "222222"
    expected_cora_id = "123"
    mock_cora_client.search_records.return_value = CoraRecordList(
        [create_mock_record(expected_cora_id), create_mock_record("000")]
    )

    response = get_cora_id_by_old_id(
        old_id_multiple,
        record_type="diva-organisation",
        cora_client=mock_cora_client,
    )
    mock_cora_client.search_records.assert_called_once()
    assert response == expected_cora_id
    assert (
        "WARNING",
        f"Warning: Multiple diva-organisations found for old ID '{old_id_multiple}'. Using the first one.",
    ) in [(record.levelname, record.getMessage()) for record in caplog.records]


def test_get_cora_id_by_old_id_for_diva_person():
    mock_cora_client = Mock(CoraClient)
    old_id = "diva2:878550"
    expected_cora_id = "123"
    mock_cora_client.search_records.return_value = create_mock_response(
        expected_cora_id
    )

    response = get_cora_id_by_old_id(
        old_id,
        record_type="diva-person",
        cora_client=mock_cora_client,
    )
    mock_cora_client.search_records.assert_called_once()
    search_call = mock_cora_client.search_records.call_args.kwargs
    assert search_call["search_id"] == "diva-personSearch"
    assert_equal_for_xml_and_xml_string(
        search_call["search_data"], create_generic_id_search_data(old_id)
    )
    assert response == expected_cora_id


def test_get_cora_id_by_old_id_for_diva_output():
    mock_cora_client = Mock(CoraClient)
    old_id = "diva2:878550"
    expected_cora_id = "123"
    mock_cora_client.search_records.return_value = create_mock_response(
        expected_cora_id
    )

    response = get_cora_id_by_old_id(
        old_id,
        record_type="diva-output",
        cora_client=mock_cora_client,
    )
    mock_cora_client.search_records.assert_called_once()
    search_call = mock_cora_client.search_records.call_args.kwargs
    assert search_call["search_id"] == "outputPublicSearch"
    assert_equal_for_xml_and_xml_string(
        search_call["search_data"], create_generic_id_search_data(old_id)
    )
    assert response == expected_cora_id


def test_propagates_cora_client_error():
    mock_cora_client = Mock(CoraClient)
    old_id = "878550"
    error = CoraHTTPError(code=500, message="Internal server error")
    mock_cora_client.search_records.side_effect = error

    with pytest.raises(CoraHTTPError) as exc_info:
        get_cora_id_by_old_id(
            old_id,
            record_type="diva-organisation",
            cora_client=mock_cora_client,
        )
    assert exc_info.value is error
    mock_cora_client.search_records.assert_called_once()


@pytest.fixture(autouse=True)
def with_cache_clear():
    yield
    _cache.clear()


def create_expected_search_data(old_id: str) -> str:
    return f"""
            <search>
                <include>
                    <includePart>
                        <oldIdSearchTerm>{old_id}</oldIdSearchTerm>
                    </includePart>
                </include>
            </search>
        """


def create_generic_id_search_data(old_id: str) -> str:
    return f"""
            <search>
                <include>
                    <includePart>
                        <genericIdSearchTerm>{old_id.replace(":", "?")}</genericIdSearchTerm>
                    </includePart>
                </include>
            </search>
        """


def create_mock_response(expected_cora_id: str | None) -> CoraRecordList:
    if expected_cora_id is None:
        return CoraRecordList([])
    return CoraRecordList([create_mock_record(expected_cora_id)])


def create_mock_record(record_id: str) -> CoraRecord:
    return CoraRecord(xml=ET.fromstring(f"""
                <record>
                    <data>
                        <organisation>
                            <recordInfo>
                                <id>{record_id}</id>
                            </recordInfo>
                        </organisation>
                    </data>
                </record>
    """))
