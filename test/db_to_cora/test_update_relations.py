import xml.etree.ElementTree as ET

import pytest
from db_to_cora.update_relations import (
    RelationMapping,
    RelationMapping,
    update_relations,
)
from cora.context import MockContext
from unittest.mock import patch
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.update import UpdateRecordResult


@patch("db_to_cora.update_relations.update_record")
def test_update_relations_update_failed(mock_update_record):
    mock_update_record.return_value = UpdateRecordResult(
        success=False, error="Update failed"
    )

    (old_child, new_child) = _create_mock_record("1", "100", parents=["2"])
    (old_parent, new_parent) = _create_mock_record("2", "200")

    record_mapping: list[tuple[ET.Element, ET.Element | None]] = [
        (old_child, new_child),
        (old_parent, new_parent),
    ]

    relation_mappings = [
        RelationMapping(
            old_relation_tag="parent_id",
            new_relation_link="foo",
            new_relation_type="parent",
        ),
    ]

    with pytest.raises(Exception):
        update_relations(record_mapping, relation_mappings, "diva-foo", MockContext())


@patch("db_to_cora.update_relations.update_record")
def test_update_relations(mock_update_record):
    (old_child, new_child) = _create_mock_record("1", "100", parents=["2"])
    (old_parent, new_parent) = _create_mock_record("2", "200")

    record_mapping: list[tuple[ET.Element, ET.Element | None]] = [
        (old_child, new_child),
        (old_parent, new_parent),
    ]

    relation_mappings = [
        RelationMapping(
            old_relation_tag="parent_id",
            new_relation_link="foo",
            new_relation_type="parent",
        ),
    ]

    update_relations(record_mapping, relation_mappings, "diva-foo", MockContext())

    assert mock_update_record.call_count == 1
    updated_record_xml = mock_update_record.call_args.args[0]

    assert_equal_for_xml_and_xml_string(
        updated_record_xml,
        """
            <foo>
                <recordInfo>
                    <id>100</id>
                    <oldId>1</oldId>
                </recordInfo>
                <related type="parent" repeatId="0">
                    <foo>
                        <linkedRecordType>diva-foo</linkedRecordType>
                        <linkedRecordId>200</linkedRecordId>
                    </foo>
                </related>
            </foo>
        """,
    )


@patch("db_to_cora.update_relations.update_record")
def test_update_relations_multiple(mock_update_record):
    (old_child, new_child) = _create_mock_record(
        "1", "100", parents=["2"], earlier=["3", "4"]
    )
    (old_earlier1, new_earlier1) = _create_mock_record("3", "300")
    (old_earlier2, new_earlier2) = _create_mock_record("4", "400")
    (old_parent, new_parent) = _create_mock_record("2", "200")

    record_mapping: list[tuple[ET.Element, ET.Element | None]] = [
        (old_child, new_child),
        (old_earlier1, new_earlier1),
        (old_earlier2, new_earlier2),
        (old_parent, new_parent),
    ]

    relation_mappings = [
        RelationMapping(
            old_relation_tag="parent_id",
            new_relation_link="foo",
            new_relation_type="parent",
        ),
        RelationMapping(
            old_relation_tag="earlier_id",
            new_relation_link="foo",
            new_relation_type="earlier",
        ),
    ]

    update_relations(record_mapping, relation_mappings, "diva-foo", MockContext())

    assert mock_update_record.call_count == 1
    updated_record_xml = mock_update_record.call_args.args[0]

    assert_equal_for_xml_and_xml_string(
        updated_record_xml,
        """
            <foo>
                <recordInfo>
                    <id>100</id>
                    <oldId>1</oldId>
                </recordInfo>
                <related type="parent" repeatId="0">
                    <foo>
                        <linkedRecordType>diva-foo</linkedRecordType>
                        <linkedRecordId>200</linkedRecordId>
                    </foo>
                </related>
                <related type="earlier" repeatId="0">
                    <foo>
                        <linkedRecordType>diva-foo</linkedRecordType>
                        <linkedRecordId>300</linkedRecordId>
                    </foo>
                </related>
                <related type="earlier" repeatId="1">
                    <foo>
                        <linkedRecordType>diva-foo</linkedRecordType>
                        <linkedRecordId>400</linkedRecordId>
                    </foo>
                </related>
            </foo>
        """,
    )


def _create_mock_record(
    old_id: str,
    new_id: str,
    parents: list[str] = [],
    earlier: list[str] = [],
) -> tuple[ET.Element, ET.Element]:
    old = ET.fromstring(
        f"""
        <record>
            <old_id>{old_id}</old_id>
        </record>
    """
    )

    if len(parents) > 0:
        parent_org = ET.Element("parent_id")
        parent_org.text = ",".join(parents)
        old.append(parent_org)

    if len(earlier) > 0:
        earlier_org = ET.Element("earlier_id")
        earlier_org.text = ",".join(earlier)
        old.append(earlier_org)

    new = ET.fromstring(
        f"""
        <record>
            <data>
                <foo>
                    <recordInfo>
                        <id>{new_id}</id>
                        <oldId>{old_id}</oldId>
                    </recordInfo>
                </foo>
            </data>
        </record>
    """
    )

    return old, new
