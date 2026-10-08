from cora.context import MockContext
from common.xml_utils import pretty_print_xml
from cora_to_cora.organisations_migrate import organisations_migrate
import pytest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse
import json
import os
import runpy
import xml.etree.ElementTree as ET
from cora.create import CreateRecordSuccessResult, CreateRecordFailureResult
from cora_to_cora.organisations_migrate import _get_old_cora_organisations
from scripts.organisations_migrate import main

SEARCH_URL = "https://cora.diva-portal.org/diva/rest/record/searchResult/publicOrganisationSearch"


def _search_data(request):
    return json.loads(parse_qs(urlparse(request.url).query)["searchData"][0])


@pytest.mark.parametrize("total", [0, 1000, 1001, 2000, 6015])
@pytest.mark.parametrize("domain", [None, 'Test_"Domain&'])
def test_fetches_every_page(requests_mock, total, domain):
    template = _read_json_file("data/old_cora_search_result_two_organisations.json")[
        "dataList"
    ]["data"][0]
    records = [{**template, "page_test_id": index} for index in range(total)]

    def respond(request, response_context):
        search = _search_data(request)
        children = {child["name"]: child for child in search["children"]}
        assert search["name"] == "search"
        assert children["rows"]["value"] == "1000"
        if domain is None:
            assert children["include"]["children"] == [
                {
                    "name": "includePart",
                    "children": [
                        {"name": "organisationGeneralSearchTerm", "value": "*"}
                    ],
                }
            ]
        else:
            assert children["include"]["children"] == [
                {
                    "name": "includePart",
                    "children": [
                        {"name": "divaOrganisationDomainSearchTerm", "value": domain}
                    ],
                }
            ]
        start = int(children["start"]["value"])
        return {
            "dataList": {
                "totalNo": str(total),
                "data": records[start - 1 : start + 999],
            }
        }

    requests_mock.get(SEARCH_URL, json=respond)

    assert _get_old_cora_organisations(MockContext(), domain) == records
    starts = [
        next(
            child["value"]
            for child in _search_data(request)["children"]
            if child["name"] == "start"
        )
        for request in requests_mock.request_history
    ]
    assert starts == [str(start) for start in range(1, max(total, 1) + 1, 1000)]


@pytest.mark.parametrize("failure", ["http", "empty"])
def test_later_page_failure_aborts_before_creation(requests_mock, failure):
    record = _read_json_file("data/old_cora_search_result_two_organisations.json")[
        "dataList"
    ]["data"][0]
    first_page = {"dataList": {"totalNo": "1001", "data": [record] * 1000}}
    if failure == "http":
        second_page = {"status_code": 503, "text": "Unavailable"}
        message = "Failed to fetch organisations from old Cora: 503 Unavailable"
    else:
        second_page = {"json": {"dataList": {"totalNo": "1001", "data": []}}}
        message = "Empty organisation page at start 1001"
    requests_mock.get(SEARCH_URL, [{"json": first_page}, second_page])

    with patch("cora_to_cora.organisations_migrate.create_record") as create_mock:
        with pytest.raises(Exception, match=message):
            organisations_migrate(MockContext())
        create_mock.assert_not_called()
    assert requests_mock.call_count == 2


def test_migrates_pages_and_filters_roots_before_updating_relations(
    requests_mock, mock_run_with_threads
):
    records = _read_json_file(
        "data/old_cora_search_result_two_organisations_and_root.json"
    )["dataList"]["data"]
    root = next(
        record for record in records if "rootOrganisation" in json.dumps(record)
    )
    organisation = next(record for record in records if record != root)
    requests_mock.get(
        SEARCH_URL,
        [
            {
                "json": {
                    "dataList": {
                        "totalNo": "1002",
                        "data": [root] * 999 + [organisation],
                    }
                }
            },
            {"json": {"dataList": {"totalNo": "1002", "data": [root, organisation]}}},
        ],
    )
    created = ET.Element("createdOrganisation")
    with (
        patch(
            "cora_to_cora.organisations_migrate.transform_organisation",
            return_value=ET.Element("organisation"),
        ) as transform_mock,
        patch(
            "cora_to_cora.organisations_migrate.create_record",
            return_value=CreateRecordSuccessResult(
                record_id="new", response_data=created
            ),
        ) as create_mock,
        patch(
            "cora_to_cora.organisations_migrate.update_organisation_relations"
        ) as relations_mock,
    ):
        context = MockContext()
        assert organisations_migrate(context) == 2
        assert transform_mock.call_count == 2
        assert create_mock.call_count == 2
        relations_mock.assert_called_once_with(
            [(organisation, created), (organisation, created)], context
        )
    assert requests_mock.call_count == 2


@pytest.mark.parametrize("domain", [None, "test_domain"])
def test_cli_accepts_optional_domain(domain):
    arguments = ["organisations-migrate", "--system", "minikube"]
    if domain is not None:
        arguments.extend(["--domain", domain])
    with (
        patch("sys.argv", arguments),
        patch("scripts.organisations_migrate.load_environment"),
        patch("scripts.organisations_migrate.configure_logging"),
        patch("scripts.organisations_migrate.CoraContext") as context_mock,
        patch("scripts.organisations_migrate.organisations_migrate") as migrate_mock,
    ):
        main()
        migrate_mock.assert_called_once_with(context_mock.return_value, domain)


def test_cli_runs_as_script_without_domain():
    with (
        patch("sys.argv", ["organisations-migrate", "--system", "minikube"]),
        patch("common.environment.load_environment"),
        patch("common.logging_config.configure_logging"),
        patch("cora.context.CoraContext") as context_mock,
        patch(
            "cora_to_cora.organisations_migrate.organisations_migrate"
        ) as migrate_mock,
    ):
        runpy.run_path(
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "../../src/scripts/organisations_migrate.py",
                )
            ),
            run_name="__main__",
        )
        migrate_mock.assert_called_once_with(context_mock.return_value, None)


@pytest.fixture
def mock_run_with_threads():
    """Fixture to mock run_with_threads to simply iterate instead of using threads."""
    with patch("cora_to_cora.organisations_migrate.run_with_threads") as mock:
        mock.side_effect = lambda items, func, workers, desc: [
            func(item) for item in items
        ]
        yield mock


@patch("cora_to_cora.organisations_migrate.create_record")
@patch("cora_to_cora.organisations_migrate.update_organisation_relations")
def test_organisations_migrate_apply_with_zero_results(
    create_record_mock,
    update_organisation_relations_mock,
    mock_run_with_threads,
    requests_mock,
    caplog,
):
    mock_context = MockContext()
    domain = "test_domain"

    requests_mock.get(
        SEARCH_URL,
        status_code=200,
        text='{"dataList": {"data":[], "fromNo": "0", "totalNo": "0", "containDataOfType": "mix", "toNo": "0"}}',
    )

    organisations_migrate(mock_context, domain)
    assert requests_mock.call_count == 1
    assert "No organisations found to migrate from old Cora system." in caplog.messages
    assert create_record_mock.call_count == 0
    assert update_organisation_relations_mock.call_count == 0


def test_get_old_organisations_failed(requests_mock):
    mock_context = MockContext()
    domain = "test_domain"

    requests_mock.get(
        SEARCH_URL,
        status_code=404,
        text="Some Cora Error",
    )

    with pytest.raises(
        Exception,
        match="Failed to fetch organisations from old Cora: 404 Some Cora Error",
    ):
        organisations_migrate(mock_context, domain)


@patch("cora_to_cora.organisations_migrate.update_organisation_relations")
@patch("cora_to_cora.organisations_migrate.create_record")
@patch("cora_to_cora.organisations_migrate.validate_record")
@patch("cora_to_cora.organisations_migrate.transform_organisation")
def test_creates_transformed_record_when_apply_and_two_results(
    transform_organisation_mock,
    validate_record_mock,
    create_record_mock,
    update_organisation_relations_mock,
    mock_run_with_threads,
    requests_mock,
    caplog,
):
    mock_context = MockContext()
    domain = "test_domain"

    # Load test data from JSON file
    test_data = _read_json_file("data/old_cora_search_result_two_organisations.json")

    requests_mock.get(
        SEARCH_URL,
        status_code=200,
        json=test_data,
    )

    transform_organisation_mock.return_value = ET.Element("organisation")

    # Set up create_record_mock to return success results
    create_record_mock.side_effect = [
        CreateRecordSuccessResult(
            record_id="new_id_1",
            response_data=ET.Element("created_org_1"),
        ),
        CreateRecordSuccessResult(
            record_id="new_id_2",
            response_data=ET.Element("created_org_2"),
        ),
    ]

    organisations_migrate(mock_context, domain)
    assert requests_mock.call_count == 1
    assert "Found 2 organisations to migrate from old Cora system." in caplog.messages
    assert transform_organisation_mock.call_count == 2
    assert validate_record_mock.call_count == 0
    assert create_record_mock.call_count == 2
    assert update_organisation_relations_mock.call_count == 1

    # Assert that update_organisation_relations is called with list of tuples
    call_args = update_organisation_relations_mock.call_args[0][0]
    assert len(call_args) == 2

    # Check first tuple: (old_org, created_org.response_data)
    old_org_1, created_org_1 = call_args[0]
    assert old_org_1 == test_data["dataList"]["data"][0]
    assert created_org_1.tag == "created_org_1"

    # Check second tuple: (old_org, created_org.response_data)
    old_org_2, created_org_2 = call_args[1]
    assert old_org_2 == test_data["dataList"]["data"][1]
    assert created_org_2.tag == "created_org_2"


@patch("cora_to_cora.organisations_migrate.update_organisation_relations")
@patch("cora_to_cora.organisations_migrate.create_record")
@patch("cora_to_cora.organisations_migrate.validate_record")
@patch("cora_to_cora.organisations_migrate.transform_organisation")
def test_aborts_migration_when_any_create_record_fails(
    transform_organisation_mock,
    validate_record_mock,
    create_record_mock,
    update_organisation_relations_mock,
    mock_run_with_threads,
    requests_mock,
    caplog,
):
    mock_context = MockContext()
    domain = "test_domain"

    create_record_mock.side_effect = [
        CreateRecordSuccessResult(
            record_id="some_id",
            response_data=ET.Element("response"),
        ),
        CreateRecordFailureResult(error="Failed to create record"),
    ]

    # Load test data from JSON file
    test_data = _read_json_file("data/old_cora_search_result_two_organisations.json")

    requests_mock.get(
        SEARCH_URL,
        status_code=200,
        json=test_data,
    )

    transform_organisation_mock.return_value = ET.Element("organisation")

    with pytest.raises(
        Exception, match="Aborting migration due to create record failure."
    ):
        organisations_migrate(mock_context, domain)
        assert requests_mock.call_count == 1
        assert (
            "Found 2 organisations to migrate from old Cora system." in caplog.messages
        )
        assert transform_organisation_mock.call_count == 2
        assert validate_record_mock.call_count == 0
        assert create_record_mock.call_count == 1

        assert (
            "Some records failed to be created. Aborting update of relations."
            in caplog.messages
        )

        assert update_organisation_relations_mock.call_count == 0


@patch("cora_to_cora.organisations_migrate.update_organisation_relations")
@patch("cora_to_cora.organisations_migrate.create_record")
@patch("cora_to_cora.organisations_migrate.validate_record")
@patch("cora_to_cora.organisations_migrate.transform_organisation")
def test_ignores_root_organisation(
    transform_organisation_mock,
    validate_record_mock,
    create_record_mock,
    update_organisation_relations_mock,
    mock_run_with_threads,
    requests_mock,
    caplog,
):
    mock_context = MockContext()
    domain = "test_domain"

    # Load test data from JSON file
    test_data = _read_json_file(
        "data/old_cora_search_result_two_organisations_and_root.json"
    )

    requests_mock.get(
        SEARCH_URL,
        status_code=200,
        json=test_data,
    )

    transform_organisation_mock.return_value = ET.Element("organisation")

    organisations_migrate(mock_context, domain)
    assert requests_mock.call_count == 1
    assert "Found 1 organisations to migrate from old Cora system." in caplog.messages
    assert transform_organisation_mock.call_count == 1
    assert validate_record_mock.call_count == 0
    assert create_record_mock.call_count == 1
    assert update_organisation_relations_mock.call_count == 1


@patch("cora_to_cora.organisations_migrate.update_organisation_relations")
@patch("cora_to_cora.organisations_migrate.create_record")
@patch("cora_to_cora.organisations_migrate.validate_record")
@patch("cora_to_cora.organisations_migrate.transform_organisation")
def test_skips_migrate_for_existing_organisation(
    transform_organisation_mock,
    validate_record_mock,
    create_record_mock,
    update_organisation_relations_mock,
    mock_run_with_threads,
    requests_mock,
    caplog,
):
    mock_context = MockContext()
    domain = "test_domain"

    test_data = _read_json_file("data/old_cora_search_result_two_organisations.json")

    requests_mock.get(
        SEARCH_URL,
        status_code=200,
        json=test_data,
    )

    create_record_mock.side_effect = [
        CreateRecordFailureResult(
            error="Failed to create record with status 409: The record could not be created as it fails unique validation with the following 1 error messages: [A record matching the unique rule with [key: oldId, value: 16205] already exists in the system]"
        ),
        CreateRecordSuccessResult(
            record_id="new_id_2",
            response_data=ET.Element("created_org_2"),
        ),
    ]

    transform_organisation_mock.return_value = ET.Element("organisation")

    organisations_migrate(mock_context, domain)
    assert requests_mock.call_count == 1
    assert "Found 2 organisations to migrate from old Cora system." in caplog.messages
    assert transform_organisation_mock.call_count == 2
    assert validate_record_mock.call_count == 0
    assert create_record_mock.call_count == 2
    assert update_organisation_relations_mock.call_count == 1

    call_args = update_organisation_relations_mock.call_args[0][0]
    assert len(call_args) == 1

    old_org, created_org = call_args[0]
    assert old_org == test_data["dataList"]["data"][1]
    assert created_org.tag == "created_org_2"


def _read_json_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), "r") as f:
        return json.load(f)
