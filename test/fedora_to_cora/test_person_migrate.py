import json
from unittest.mock import patch
import xml.etree.ElementTree as ET
from requests.exceptions import HTTPError
from requests_mock import mock

from common.test_helper import assert_equal_for_xml_and_xml_string
from common.xml_utils import create_group
from cora.context import MockContext
from fedora_to_cora.authority_person_json_validate import (
    AuthorityPersonJSONValidationError,
)
from fedora_to_cora.person_migrate import migrate_person
from cora.create import CreateRecordFailureResult, CreateRecordSuccessResult


@patch("fedora_to_cora.person_migrate.get_authority_person")
def test_returns_error_when_failed_to_fetch_authority_pid(mock_get_authority_person):
    mock_get_authority_person.side_effect = HTTPError("Connection refused")

    result = migrate_person("authority-person:11111", MockContext())

    assert result.status == "FAILED"
    assert result.cora_person_id is None
    assert result.error == "Failed to fetch authority person: Connection refused"


@patch("fedora_to_cora.person_migrate.get_authority_person")
@patch("fedora_to_cora.person_migrate.create_record")
def test_returns_error_when_create_record_fails(
    mock_create_record, mock_get_authority_person
):
    mock_get_authority_person.return_value = json.loads("""
        {
            "authorityPerson": {
                "defaultName": {
                    "lastname": "Andréasson",
                    "firstname": "David",
                    "addition": "",
                    "number": ""
                },
                  "pid": "authority-person:11111"
            }
        }
    """)

    mock_create_record.return_value = CreateRecordFailureResult("Unauthorized")

    result = migrate_person("authority-person:11111", MockContext())

    assert result.status == "FAILED"
    assert result.cora_person_id is None
    assert result.error == "Failed to create person record: Unauthorized"


@patch("fedora_to_cora.person_migrate.get_authority_person")
@patch("fedora_to_cora.person_migrate.create_record")
def test_returns_skipped_when_person_already_exists(
    mock_create_record, mock_get_authority_person
):

    mock_get_authority_person.return_value = json.loads("""
        {
            "authorityPerson": {
                "defaultName": {
                    "lastname": "Andréasson",
                    "firstname": "David",
                    "addition": "",
                    "number": ""
                },
                  "pid": "authority-person:11111"
            }
        }
    """)
    mock_create_record.return_value = CreateRecordFailureResult(
        "The record could not be created as it fails unique validation with the following 1 error messages: [A record matching the unique rule with [key: oldId, value: authority-person:11111] already exists in the system]"
    )
    result = migrate_person("authority-person:11111", MockContext())

    assert result.status == "SKIPPED"
    assert result.cora_person_id is None
    assert result.error == "Cora diva-person record already exists"


@patch("fedora_to_cora.person_migrate.get_authority_person")
@patch("fedora_to_cora.person_migrate.create_record")
def test_calls_create_person_with_transformed_person_and_returns_created_person(
    mock_create_record, mock_get_authority_person
):
    mock_get_authority_person.return_value = json.loads("""
        {
            "authorityPerson": {
                "defaultName": {
                    "lastname": "Andréasson",
                    "firstname": "David",
                    "addition": "",
                    "number": ""
                },
                  "pid": "authority-person:11111"
            }
        }
    """)

    expected_cora_person = """
    <person>
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>diva-person</linkedRecordId>
            </validationType>
        <dataDivider>
            <linkedRecordType>system</linkedRecordType>
            <linkedRecordId>divaData</linkedRecordId>
        </dataDivider>
        <oldId>authority-person:11111</oldId>
        </recordInfo>
        <authority>
            <name type="personal">
                <namePart type="given">David</namePart>
                <namePart type="family">Andréasson</namePart>
            </name>
        </authority>
    </person>
    """

    mock_create_record.return_value = CreateRecordSuccessResult(
        "some_cora_id",
        ET.Element("record"),
        201,
    )

    result = migrate_person("authority-person:11111", MockContext())

    assert result.status == "CREATED"
    assert mock_create_record.call_count == 1
    assert_equal_for_xml_and_xml_string(
        mock_create_record.call_args[0][0], expected_cora_person
    )
    assert result.cora_person_id == "some_cora_id"
