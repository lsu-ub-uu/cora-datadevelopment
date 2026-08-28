from cora.context import MockContext
from common.xml_utils import pretty_print_xml
from cora_to_cora.organisations_migrate import organisations_migrate
import pytest
from unittest.mock import patch
import json
import os
import xml.etree.ElementTree as ET
from cora.create import CreateRecordSuccessResult, CreateRecordFailureResult


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
):
    mock_context = MockContext()
    domain = "test_domain"

    requests_mock.get(
        f'https://cora.diva-portal.org/diva/rest/record/searchResult/publicOrganisationSearch?searchData={{"name":"search","children":[{{"name":"include","children":[{{"name":"includePart","children":[{{"name":"divaOrganisationDomainSearchTerm","value":"{domain}"}}]}}]}},{{"name":"rows","value":"1000"}}]}}',
        status_code=200,
        text='{"dataList": {"data":[], "fromNo": "0", "totalNo": "0", "containDataOfType": "mix", "toNo": "0"}}',
    )

    organisations_migrate(mock_context, domain)
    assert requests_mock.call_count == 1
    mock_context.log.assert_called_with(  # type: ignore
        "No organisations found to migrate from old Cora system."
    )
    assert create_record_mock.call_count == 0
    assert update_organisation_relations_mock.call_count == 0


def test_get_old_organisations_failed(requests_mock):
    mock_context = MockContext()
    domain = "test_domain"

    requests_mock.get(
        f'https://cora.diva-portal.org/diva/rest/record/searchResult/publicOrganisationSearch?searchData={{"name":"search","children":[{{"name":"include","children":[{{"name":"includePart","children":[{{"name":"divaOrganisationDomainSearchTerm","value":"{domain}"}}]}}]}},{{"name":"rows","value":"1000"}}]}}',
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
):
    mock_context = MockContext()
    domain = "test_domain"

    # Load test data from JSON file
    test_data = _read_json_file("data/old_cora_search_result_two_organisations.json")

    requests_mock.get(
        f'https://cora.diva-portal.org/diva/rest/record/searchResult/publicOrganisationSearch?searchData={{"name":"search","children":[{{"name":"include","children":[{{"name":"includePart","children":[{{"name":"divaOrganisationDomainSearchTerm","value":"{domain}"}}]}}]}},{{"name":"rows","value":"1000"}}]}}',
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
    mock_context.log.assert_any_call(  # type: ignore
        "Found 2 organisations to migrate from old Cora system."
    )
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
        f'https://cora.diva-portal.org/diva/rest/record/searchResult/publicOrganisationSearch?searchData={{"name":"search","children":[{{"name":"include","children":[{{"name":"includePart","children":[{{"name":"divaOrganisationDomainSearchTerm","value":"{domain}"}}]}}]}},{{"name":"rows","value":"1000"}}]}}',
        status_code=200,
        json=test_data,
    )

    transform_organisation_mock.return_value = ET.Element("organisation")

    with pytest.raises(
        Exception, match="Aborting migration due to create record failure."
    ):
        organisations_migrate(mock_context, domain)
        assert requests_mock.call_count == 1
        mock_context.log.assert_any_call(  # type: ignore
            "Found 2 organisations to migrate from old Cora system."
        )
        assert transform_organisation_mock.call_count == 2
        assert validate_record_mock.call_count == 0
        assert create_record_mock.call_count == 1

        mock_context.log.assert_any_call(  # type: ignore
            "Some records failed to be created. Aborting update of relations."
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
):
    mock_context = MockContext()
    domain = "test_domain"

    # Load test data from JSON file
    test_data = _read_json_file(
        "data/old_cora_search_result_two_organisations_and_root.json"
    )

    requests_mock.get(
        f'https://cora.diva-portal.org/diva/rest/record/searchResult/publicOrganisationSearch?searchData={{"name":"search","children":[{{"name":"include","children":[{{"name":"includePart","children":[{{"name":"divaOrganisationDomainSearchTerm","value":"{domain}"}}]}}]}},{{"name":"rows","value":"1000"}}]}}',
        status_code=200,
        json=test_data,
    )

    transform_organisation_mock.return_value = ET.Element("organisation")

    organisations_migrate(mock_context, domain)
    assert requests_mock.call_count == 1
    mock_context.log.assert_any_call(  # type: ignore
        "Found 1 organisations to migrate from old Cora system."
    )
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
):
    mock_context = MockContext()
    domain = "test_domain"

    test_data = _read_json_file("data/old_cora_search_result_two_organisations.json")

    requests_mock.get(
        f'https://cora.diva-portal.org/diva/rest/record/searchResult/publicOrganisationSearch?searchData={{"name":"search","children":[{{"name":"include","children":[{{"name":"includePart","children":[{{"name":"divaOrganisationDomainSearchTerm","value":"{domain}"}}]}}]}},{{"name":"rows","value":"1000"}}]}}',
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
    mock_context.log.assert_any_call(  # type: ignore
        "Found 2 organisations to migrate from old Cora system."
    )
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

