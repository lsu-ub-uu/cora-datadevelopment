from common.xml_utils import pretty_print_xml
from cora_to_cora.update_organisation_relations import (
    update_organisation_relations,
)
from xml.etree import ElementTree as ET
from typing import List, Tuple
from unittest.mock import patch
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
import pytest


@patch("cora_to_cora.update_organisation_relations.update_record")
def test_one_child_with_a_parent(mock_update_record):
    tuples: List[Tuple] = [
        create_mock_org_tuple("old-sub-id", "new-sub-id", ["old-top-id"], []),
        create_mock_org_tuple("old-top-id", "new-top-id", [], []),
    ]

    update_organisation_relations(tuples, MockContext())

    mock_update_record.assert_called_once()
    updated_organisation_xml = mock_update_record.call_args[0][0]
    assert_equal_for_xml_and_xml_string(
        updated_organisation_xml,
        """
        <organisation>
            <recordInfo>
                <id>new-sub-id</id>
                <oldId>old-sub-id</oldId>
            </recordInfo>
            <related type="parent">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>new-top-id</linkedRecordId>
                </organisation>
            </related>
        </organisation>
    """,
    )


@patch("cora_to_cora.update_organisation_relations.update_record")
def test_one_child_with_two_parents(mock_update_record):
    tuples: List[Tuple] = [
        create_mock_org_tuple(
            "old-sub-id", "new-sub-id", ["old-top-id", "other-old-top-id"], []
        ),
        create_mock_org_tuple("old-top-id", "new-top-id", [], []),
        create_mock_org_tuple("other-old-top-id", "other-new-top-id", [], []),
    ]

    with pytest.raises(AssertionError, match="Multiple parent organisations found"):
        update_organisation_relations(tuples, MockContext())
        mock_update_record.assert_not_called()


@patch("cora_to_cora.update_organisation_relations.update_record")
def test_one_child_with_earlier(mock_update_record):
    tuples: List[Tuple] = [
        create_mock_org_tuple(
            "old-sub-id", "new-sub-id", [], ["old-top-id", "other-old-top-id"]
        ),
        create_mock_org_tuple("old-top-id", "new-top-id", [], []),
        create_mock_org_tuple("other-old-top-id", "other-new-top-id", [], []),
    ]

    update_organisation_relations(tuples, MockContext())

    assert mock_update_record.call_count == 2
    updated_organisation_xml = mock_update_record.call_args[0][0]

    print(pretty_print_xml(updated_organisation_xml))
    assert_equal_for_xml_and_xml_string(
        updated_organisation_xml,
        """
        <organisation>
            <recordInfo>
                <id>new-sub-id</id>
                <oldId>old-sub-id</oldId>
            </recordInfo>
            <related type="earlier" repeatId="0">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>new-top-id</linkedRecordId>
                </organisation>
            </related>
            <related type="earlier" repeatId="1">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>other-new-top-id</linkedRecordId>
                </organisation>
            </related>
        </organisation>
    """,
    )


@patch("cora_to_cora.update_organisation_relations.update_record")
def test_one_child_with_a_parent_and_earlier(mock_update_record):
    tuples: List[Tuple] = [
        create_mock_org_tuple(
            "old-sub-id",
            "new-sub-id",
            ["old-parent-top-id"],
            ["other-earlier-old-top-id"],
        ),
        create_mock_org_tuple("old-parent-top-id", "new-parent-top-id", [], []),
        create_mock_org_tuple(
            "other-earlier-old-top-id", "other-earlier-new-top-id", [], []
        ),
    ]

    update_organisation_relations(tuples, MockContext())

    assert mock_update_record.call_count == 2
    updated_organisation_xml = mock_update_record.call_args[0][0]

    print(pretty_print_xml(updated_organisation_xml))
    assert_equal_for_xml_and_xml_string(
        updated_organisation_xml,
        """
        <organisation>
            <recordInfo>
                <id>new-sub-id</id>
                <oldId>old-sub-id</oldId>
            </recordInfo>
            <related type="earlier" repeatId="0">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>other-earlier-new-top-id</linkedRecordId>
                </organisation>
            </related>
            <related type="parent">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>new-parent-top-id</linkedRecordId>
                </organisation>
            </related>
        </organisation>
    """,
    )


def create_mock_org_tuple(
    old_id: str, new_id: str, parent_old_ids: List[str], earlier_old_ids: List[str]
) -> Tuple[dict, ET.Element]:
    old_org_children = [
        {
            "name": "recordInfo",
            "children": [
                {"name": "id", "value": old_id},
            ],
        },
    ]

    for repeat_id, parent_old_id in enumerate(parent_old_ids):
        old_org_children.append(
            {
                "name": "parentOrganisation",
                "repeatId": str(repeat_id),
                "children": [
                    {
                        "name": "organisationLink",
                        "children": [
                            {
                                "name": "linkedRecordId",
                                "value": parent_old_id,
                            },
                        ],
                    }
                ],
            }
        )

    for repeat_id, earlier_old_id in enumerate(earlier_old_ids):
        old_org_children.append(
            {
                "name": "earlierOrganisation",
                "repeatId": str(repeat_id),
                "children": [
                    {
                        "name": "organisationLink",
                        "children": [
                            {
                                "name": "linkedRecordId",
                                "value": earlier_old_id,
                            },
                        ],
                    }
                ],
            }
        )

    old_org = {
        "record": {
            "data": {
                "children": [{"name": "organisation", "children": old_org_children}],
            }
        }
    }

    new_org = ET.fromstring(
        f"""
         <organisation>
            <recordInfo>
                <id>{new_id}</id>
                <oldId>{old_id}</oldId>
            </recordInfo>
        </organisation>
    """
    )

    return old_org, new_org
