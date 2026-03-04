import os
import json
import xml.etree.ElementTree as ET

from common.common_data import read_source_xml
from cora_to_cora.transform_organisation import transform_organisation
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_transform_top_organisation():
    with open("test/cora_to_cora/data/old_cora_top_organisation.json", "r") as f:
        old_top_organisation = json.load(f)
    transformed_organisation = transform_organisation(old_top_organisation)

    expected_xml = read_source_xml(
        os.path.join("test/cora_to_cora/data/new_cora_top_organisation.xml")
    )

    assert_equal_for_xml_and_xml_string(
        transformed_organisation,
        ET.tostring(expected_xml),
    )


def test_transform_sub_organisation():
    with open("test/cora_to_cora/data/old_cora_sub_organisation.json", "r") as f:
        old_sub_organisation = json.load(f)
    transformed_organisation = transform_organisation(old_sub_organisation)

    expected_xml = read_source_xml(
        os.path.join("test/cora_to_cora/data/new_cora_sub_organisation.xml")
    )

    assert_equal_for_xml_and_xml_string(
        transformed_organisation,
        ET.tostring(expected_xml),
    )


def test_transform_minimal_organisation():
    minimal_old_org = {
        "record": {
            "data": {
                "children": [
                    {
                        "children": [
                            {"name": "id", "value": "16501"},
                            {
                                "children": [
                                    {"name": "linkedRecordType", "value": "recordType"},
                                    {
                                        "name": "linkedRecordId",
                                        "value": "topOrganisation",
                                    },
                                ],
                                "name": "type",
                            },
                            {
                                "children": [
                                    {"name": "linkedRecordType", "value": "system"},
                                    {"name": "linkedRecordId", "value": "diva"},
                                ],
                                "name": "dataDivider",
                            },
                            {"name": "domain", "value": "smhi"},
                        ],
                        "name": "recordInfo",
                    },
                    {
                        "children": [
                            {"name": "name", "value": "Något namn"},
                            {"name": "language", "value": "sv"},
                        ],
                        "name": "organisationName",
                    },
                    {
                        "name": "organisationAlternativeName",
                        "children": [
                            {"name": "name", "value": "Some name"},
                            {"name": "language", "value": "en"},
                        ],
                    },
                ],
                "name": "organisation",
            },
        }
    }

    transformed_organisation = transform_organisation(minimal_old_org)

    assert_equal_for_xml_and_xml_string(
        transformed_organisation,
        """<organisation>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-topOrganisation</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>smhi</linkedRecordId>
                </permissionUnit>
                <oldId>16501</oldId>
            </recordInfo>
            <genre type="organisationType">topOrganisation</genre>
            <authority lang="swe" repeatId="swe">
                <name type="corporate">
                    <namePart>Något namn</namePart>
                </name>
            </authority>
            <authority lang="eng" repeatId="eng">
                <name type="corporate">
                    <namePart>Some name</namePart>
                </name>
            </authority>
        </organisation>""",
    )
