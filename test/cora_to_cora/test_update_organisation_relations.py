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


@pytest.fixture
def mock_run_with_threads():
    """Fixture to mock run_with_threads to simply iterate instead of using threads."""
    with patch("cora_to_cora.update_organisation_relations.run_with_threads") as mock:
        mock.side_effect = lambda items, func, workers, desc: [
            func(item) for item in items
        ]
        yield mock


@patch("cora_to_cora.update_organisation_relations.update_record")
def test_one_child_with_a_parent(mock_update_record, mock_run_with_threads):
    orgs: List[Tuple] = [
        _create_mock_org(
            old_id="old-sub-id", new_id="new-sub-id", parents=["old-top-id"]
        ),
        _create_mock_org(old_id="old-top-id", new_id="new-top-id"),
    ]

    update_organisation_relations(orgs, MockContext())

    mock_update_record.assert_called_once()
    updated_organisation_xml = mock_update_record.call_args.args[0]
    assert_equal_for_xml_and_xml_string(
        updated_organisation_xml,
        """
        <record>
            <data>
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
            </data>
        </record>
    """,
    )


@patch("cora_to_cora.update_organisation_relations.update_record")
def test_one_child_with_two_parents(mock_update_record, mock_run_with_threads):
    orgs: List[Tuple] = [
        _create_mock_org(
            "old-sub-id", "new-sub-id", ["old-top-id", "other-old-top-id"], []
        ),
        _create_mock_org(old_id="old-top-id", new_id="new-top-id"),
        _create_mock_org(old_id="other-old-top-id", new_id="other-new-top-id"),
    ]

    with pytest.raises(AssertionError, match="Multiple parent organisations found"):
        update_organisation_relations(orgs, MockContext())
        mock_update_record.assert_not_called()


@patch("cora_to_cora.update_organisation_relations.update_record")
def test_one_child_with_earlier(mock_update_record, mock_run_with_threads):
    orgs: List[Tuple] = [
        _create_mock_org(
            old_id="old-sub-id",
            new_id="new-sub-id",
            earlier=["old-top-id", "other-old-top-id"],
        ),
        _create_mock_org(old_id="old-top-id", new_id="new-top-id"),
        _create_mock_org(old_id="other-old-top-id", new_id="other-new-top-id"),
    ]

    update_organisation_relations(orgs, MockContext())

    mock_update_record.assert_called_once()
    updated_organisation_xml = mock_update_record.call_args.args[0]

    print(pretty_print_xml(updated_organisation_xml))
    assert_equal_for_xml_and_xml_string(
        updated_organisation_xml,
        """
        <record>
            <data>
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
            </data>
        </record>
    """,
    )


@patch("cora_to_cora.update_organisation_relations.update_record")
def test_one_child_with_a_parent_and_earlier(mock_update_record, mock_run_with_threads):
    orgs: List[Tuple] = [
        _create_mock_org(
            old_id="old-sub-id",
            new_id="new-sub-id",
            parents=["old-parent-top-id"],
            earlier=["other-earlier-old-top-id"],
        ),
        _create_mock_org(old_id="old-parent-top-id", new_id="new-parent-top-id"),
        _create_mock_org(
            old_id="other-earlier-old-top-id", new_id="other-earlier-new-top-id"
        ),
    ]

    update_organisation_relations(orgs, MockContext())

    mock_update_record.assert_called_once()
    updated_organisation_xml = mock_update_record.call_args.args[0]

    print(pretty_print_xml(updated_organisation_xml))
    assert_equal_for_xml_and_xml_string(
        updated_organisation_xml,
        """
        <record>
            <data>
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
            </data>
        </record>
    """,
    )


@patch("cora_to_cora.update_organisation_relations.update_record")
def test_child_and_earlier_with_same_parent(mock_update_record, mock_run_with_threads):
    orgs = [
        _create_mock_org(
            old_id="child-old",
            new_id="child-new",
            parents=["parent-old"],
            earlier=["earlier-old"],
        ),
        _create_mock_org(
            old_id="earlier-old",
            new_id="earlier-new",
            parents=["parent-old"],
        ),
        _create_mock_org(old_id="parent-old", new_id="parent-new"),
    ]

    update_organisation_relations(orgs, MockContext())

    assert mock_update_record.call_count == 2
    updated_organisation_child_xml = mock_update_record.call_args_list[0].args[0]
    updated_organisation_earlier_xml = mock_update_record.call_args_list[1].args[0]

    assert_equal_for_xml_and_xml_string(
        updated_organisation_child_xml,
        """
        <record>
            <data>
                <organisation>
                    <recordInfo>
                        <id>child-new</id>
                        <oldId>child-old</oldId>
                    </recordInfo>
                    <related type="earlier" repeatId="0">
                        <organisation>
                            <linkedRecordType>diva-organisation</linkedRecordType>
                            <linkedRecordId>earlier-new</linkedRecordId>
                        </organisation>
                    </related>
                    <related type="parent">
                        <organisation>
                            <linkedRecordType>diva-organisation</linkedRecordType>
                            <linkedRecordId>parent-new</linkedRecordId>
                        </organisation>
                    </related>
                </organisation>
            </data>
        </record>
    """,
    )

    assert_equal_for_xml_and_xml_string(
        updated_organisation_earlier_xml,
        """
        <record>
            <data>
                <organisation>
                    <recordInfo>
                        <id>earlier-new</id>
                        <oldId>earlier-old</oldId>
                    </recordInfo>
                    <related type="parent">
                        <organisation>
                            <linkedRecordType>diva-organisation</linkedRecordType>
                            <linkedRecordId>parent-new</linkedRecordId>
                        </organisation>
                    </related>
                </organisation>
            </data>
        </record>
    """,
    )


@patch("cora_to_cora.update_organisation_relations.update_record")
def test_deep_tree(mock_update_record, mock_run_with_threads):
    """
    top
        ├── child 1
        │     ├── grandchild 1.1
        │     └── grandchild 1.2
        └── child 2
            └── grandchild 2.1

    """

    orgs = [
        _create_mock_org(
            old_id="top_old",
            new_id="top_new",
        ),
        _create_mock_org(
            old_id="child_1_old",
            new_id="child_1_new",
            parents=["top_old"],
        ),
        _create_mock_org(
            old_id="child_2_old",
            new_id="child_2_new",
            parents=["top_old"],
        ),
        _create_mock_org(
            old_id="grandchild_1_1_old",
            new_id="grandchild_1_1_new",
            parents=["child_1_old"],
        ),
        _create_mock_org(
            old_id="grandchild_1_2_old",
            new_id="grandchild_1_2_new",
            parents=["child_1_old"],
        ),
        _create_mock_org(
            old_id="grandchild_2_1_old",
            new_id="grandchild_2_1_new",
            parents=["child_2_old"],
        ),
    ]

    update_organisation_relations(orgs, MockContext())

    assert mock_update_record.call_count == 5

    updated_organisation_0_xml = mock_update_record.call_args_list[0].args[0]
    updated_organisation_1_xml = mock_update_record.call_args_list[1].args[0]
    updated_organisation_2_xml = mock_update_record.call_args_list[2].args[0]
    updated_organisation_3_xml = mock_update_record.call_args_list[3].args[0]
    updated_organisation_4_xml = mock_update_record.call_args_list[4].args[0]
    assert (
        updated_organisation_0_xml.findtext(
            "./data/organisation/related/organisation/linkedRecordId"
        )
        == "top_new"
    )
    assert (
        updated_organisation_1_xml.findtext(
            "./data/organisation/related/organisation/linkedRecordId"
        )
        == "top_new"
    )
    assert (
        updated_organisation_2_xml.findtext(
            "./data/organisation/related/organisation/linkedRecordId"
        )
        == "child_1_new"
    )
    assert (
        updated_organisation_3_xml.findtext(
            "./data/organisation/related/organisation/linkedRecordId"
        )
        == "child_1_new"
    )
    assert (
        updated_organisation_4_xml.findtext(
            "./data/organisation/related/organisation/linkedRecordId"
        )
        == "child_2_new"
    )


def _create_mock_org(
    old_id: str,
    new_id: str,
    parents: List[str] = [],
    earlier: List[str] = [],
) -> Tuple[dict, ET.Element]:
    old_org_children = [
        {
            "name": "recordInfo",
            "children": [
                {"name": "id", "value": old_id},
            ],
        },
    ]

    for repeat_id, parent_old_id in enumerate(parents):
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

    for repeat_id, earlier_old_id in enumerate(earlier):
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
                "name": "organisation",
                "children": old_org_children,
            }
        }
    }

    new_org = ET.fromstring(
        f"""
        <record>
            <data>
                <organisation>
                    <recordInfo>
                        <id>{new_id}</id>
                        <oldId>{old_id}</oldId>
                    </recordInfo>
                </organisation>
            </data>
        </record>
    """
    )

    return old_org, new_org
