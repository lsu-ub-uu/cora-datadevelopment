from unittest.mock import Mock, patch

from cora_to_cora.transform_person import (
    _get_organisation_id_from_person_domain_part_id,
    transform_person,
)
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_transform_minimal_person():
    minimal_old_person = {
        "record": {
            "data": {
                "name": "person",
                "children": [
                    {
                        "name": "recordInfo",
                        "children": [
                            {"name": "id", "value": "authority-person:11111"},
                            {
                                "name": "type",
                                "children": [
                                    {"name": "linkedRecordType", "value": "recordType"},
                                    {"name": "linkedRecordId", "value": "person"},
                                ],
                            },
                            {
                                "name": "dataDivider",
                                "children": [
                                    {"name": "linkedRecordType", "value": "system"},
                                    {"name": "linkedRecordId", "value": "diva"},
                                ],
                            },
                            {
                                "name": "tsCreated",
                                "value": "2017-04-26T06:20:31.886000Z",
                            },
                            {"name": "public", "value": "yes"},
                            {"name": "domain", "value": "smhi", "repeatId": "0"},
                        ],
                    },
                    {
                        "name": "authorisedName",
                        "children": [
                            {"name": "familyName", "value": "Andréasson"},
                            {"name": "givenName", "value": "David"},
                        ],
                    },
                ],
            }
        }
    }

    transformed_person = transform_person(minimal_old_person)

    assert_equal_for_xml_and_xml_string(
        transformed_person,
        """<person>
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
            </person>""",
    )


def test_transform_maximal_person():

    maximal_old_person = {
        "record": {
            "data": {
                "name": "person",
                "children": [
                    {
                        "name": "recordInfo",
                        "children": [
                            {"name": "id", "value": "authority-person:11111"},
                            {
                                "name": "type",
                                "children": [
                                    {"name": "linkedRecordType", "value": "recordType"},
                                    {"name": "linkedRecordId", "value": "person"},
                                ],
                            },
                            {
                                "name": "dataDivider",
                                "children": [
                                    {"name": "linkedRecordType", "value": "system"},
                                    {"name": "linkedRecordId", "value": "diva"},
                                ],
                            },
                            {
                                "name": "tsCreated",
                                "value": "2017-04-26T06:20:31.886000Z",
                            },
                            {"name": "public", "value": "yes"},
                            {"name": "domain", "value": "smhi", "repeatId": "0"},
                        ],
                    },
                    {
                        "name": "authorisedName",
                        "children": [
                            {"name": "familyName", "value": "Andréasson"},
                            {"name": "givenName", "value": "David"},
                        ],
                    },
                    {
                        "name": "alternativeName",
                        "children": [
                            {"name": "familyName", "value": "Andreasson"},
                            {"name": "givenName", "value": "David"},
                        ],
                        "repeatId": "0",
                    },
                    {
                        "name": "ORCID_ID",
                        "value": "0000-0002-1825-0097",
                        "repeatId": "0",
                    },
                ],
            }
        }
    }

    transformed_person = transform_person(maximal_old_person)

    assert_equal_for_xml_and_xml_string(
        transformed_person,
        """<person>
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
            <variant>
                <name type="personal">
                    <namePart type="given">David</namePart>
                    <namePart type="family">Andreasson</namePart>
                </name>
            </variant>
            <nameIdentifier type="orcid">0000-0002-1825-0097</nameIdentifier>
            </person>""",
    )

    """
                <location>
                    <url>https://example.com/profile</url>
                    <displayLabel>Profile page</displayLabel>
                </location>
                <email>email@example.com</email>
                <note type="biographical" lang="eng">Senior researcher in climate studies</note>    
                <nameIdentifier type="localId">diva-local-123</nameIdentifier>
                <nameIdentifier type="localId">diva-local-123</nameIdentifier>
                <nameIdentifier type="orcid">0000-0002-1825-0097</nameIdentifier>
                <nameIdentifier type="se-libr">LIBR-12345</nameIdentifier>
                <nameIdentifier type="openAlex">A1234567890</nameIdentifier>
                <nameIdentifier type="scopus">12345678901</nameIdentifier>
                <nameIdentifier type="wos">ABC-1234-5678</nameIdentifier>
                <nameIdentifier type="googleScholar">AbC123dEf45</nameIdentifier>
                <nameIdentifier type="viaf">12345678</nameIdentifier>
                <affiliation>
                    <organisation>
                        <linkedRecordType>diva-organisation</linkedRecordType>
                        <linkedRecordId>diva-org-123</linkedRecordId>
                    </organisation>
                    <namePart>Department of Meteorology</namePart>
                    <identifier type="ror">0abc12345</identifier>
                    <country>af</country>
                    <description>researchGroup</description>
                    <startDate>
                        <year>2020</year>
                        <month>09</month>
                        <day>15</day>
                    </startDate>
                    <endDate>
                        <year>2024</year>
                        <month>06</month>
                        <day>30</day>
                    </endDate>
                </affiliation>"""


@patch("cora_to_cora.transform_person.get_cora_id_by_old_id")
@patch("cora_to_cora.transform_person.requests.get")
def test_transform_domain_part(mock_requests_get, mock_get_cora_id_by_old_id):
    domainpart = {
        "name": "personDomainPart",
        "children": [
            {
                "name": "recordInfo",
                "children": [
                    {"name": "id", "value": "authority-person:101313:kau"},
                    {
                        "name": "type",
                        "children": [
                            {"name": "linkedRecordType", "value": "recordType"},
                            {"name": "linkedRecordId", "value": "personDomainPart"},
                        ],
                    },
                    {
                        "name": "dataDivider",
                        "children": [
                            {"name": "linkedRecordType", "value": "system"},
                            {"name": "linkedRecordId", "value": "diva"},
                        ],
                    },
                    {"name": "tsCreated", "value": "2022-03-24T13:19:58.934000Z"},
                    {"name": "domain", "value": "kau"},
                    {"name": "public", "value": "yes"},
                ],
            },
            {
                "name": "affiliation",
                "children": [
                    {
                        "name": "organisationLink",
                        "children": [
                            {"name": "linkedRecordType", "value": "organisation"},
                            {
                                "name": "linkedRecordId",
                                "value": "diva-organisation:11961",
                            },
                        ],
                    }
                ],
                "repeatId": "0",
            },
        ],
    }

    domain_old_person = {
        "record": {
            "data": {
                "name": "person",
                "children": [
                    {
                        "name": "recordInfo",
                        "children": [
                            {"name": "id", "value": "authority-person:11111"},
                            {
                                "name": "type",
                                "children": [
                                    {"name": "linkedRecordType", "value": "recordType"},
                                    {"name": "linkedRecordId", "value": "person"},
                                ],
                            },
                            {
                                "name": "dataDivider",
                                "children": [
                                    {"name": "linkedRecordType", "value": "system"},
                                    {"name": "linkedRecordId", "value": "diva"},
                                ],
                            },
                            {
                                "name": "tsCreated",
                                "value": "2017-04-26T06:20:31.886000Z",
                            },
                            {"name": "public", "value": "yes"},
                            {"name": "domain", "value": "smhi", "repeatId": "0"},
                        ],
                    },
                    {
                        "name": "authorisedName",
                        "children": [
                            {"name": "familyName", "value": "Andréasson"},
                            {"name": "givenName", "value": "David"},
                        ],
                    },
                    {
                        "name": "personDomainPart",
                        "children": [
                            {"name": "linkedRecordType", "value": "personDomainPart"},
                            {
                                "name": "linkedRecordId",
                                "value": "authority-person:44211:smhi",
                            },
                        ],
                        "repeatId": "0",
                    },
                ],
            }
        }
    }

    context = Mock()
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = domainpart
    mock_requests_get.return_value = mock_response
    mock_get_cora_id_by_old_id.return_value = "cora-diva-organisation:11961"

    transformed_person = transform_person(domain_old_person, context=context)

    mock_get_cora_id_by_old_id.assert_called_once_with(
        "diva-organisation:11961",
        record_type="diva-organisation",
        context=context,
    )

    assert_equal_for_xml_and_xml_string(
        transformed_person,
        """<person>
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
            <affiliation>
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>cora-diva-organisation:11961</linkedRecordId>
                </organisation>
            </affiliation>
            </person>""",
    )

    """ 
    person har
        personDomainPart -> recordLink
            authority-person:44211:smhi
            affiliation -> organisationLink
            den pekar på subOrganisation(partOfOrganisation) med classic id
      
    """


@patch("cora_to_cora.transform_person.get_cora_id_by_old_id")
@patch("cora_to_cora.transform_person.requests.get")
def test_get_organisation_id_by_person_domain_part_id(
    mock_requests_get, mock_get_cora_id_by_old_id
):
    mock_context = Mock()
    mock_context.get_base_url.return_value = (
        "https://cora.diva-portal.org/diva/rest/record/"
    )
    mock_context.get_auth_token.return_value = "token"

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "name": "personDomainPart",
        "children": [
            {
                "name": "recordInfo",
                "children": [
                    {"name": "id", "value": "authority-person:101313:kau"},
                    {
                        "name": "type",
                        "children": [
                            {"name": "linkedRecordType", "value": "recordType"},
                            {"name": "linkedRecordId", "value": "personDomainPart"},
                        ],
                    },
                    {
                        "name": "dataDivider",
                        "children": [
                            {"name": "linkedRecordType", "value": "system"},
                            {"name": "linkedRecordId", "value": "diva"},
                        ],
                    },
                    {"name": "tsCreated", "value": "2022-03-24T13:19:58.934000Z"},
                    {"name": "domain", "value": "kau"},
                    {"name": "public", "value": "yes"},
                ],
            },
            {
                "name": "affiliation",
                "children": [
                    {
                        "name": "organisationLink",
                        "children": [
                            {"name": "linkedRecordType", "value": "organisation"},
                            {
                                "name": "linkedRecordId",
                                "value": "diva-organisation:11961",
                            },
                        ],
                    }
                ],
                "repeatId": "0",
            },
        ],
    }
    mock_requests_get.return_value = mock_response
    mock_get_cora_id_by_old_id.return_value = "cora-diva-organisation:11961"

    result = _get_organisation_id_from_person_domain_part_id(
        "authority-person:101313:kau",
        mock_context,
    )

    assert result == "cora-diva-organisation:11961"
    mock_requests_get.assert_called_once_with(
        "https://cora.diva-portal.org/diva/rest/record/personDomainPart/authority-person:101313:kau",
        headers={"Accept": "application/json", "authToken": "token"},
    )
    mock_get_cora_id_by_old_id.assert_called_once_with(
        "diva-organisation:11961",
        record_type="diva-organisation",
        context=mock_context,
    )
