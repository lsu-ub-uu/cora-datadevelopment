import xml.etree.ElementTree as ET
from db_to_cora.update_relations import update_relations
from cora.context import MockContext
from unittest.mock import patch
from common.test_helper import assert_equal_for_xml_and_xml_string


@patch("db_to_cora.update_relations.update_record")
def test_update_relations(mock_update_record):
    (old_child, new_child) = _create_mock_record("1", "100", parents=["2"])
    (old_parent, new_parent) = _create_mock_record("2", "200")

    record_mapping = [
        (old_child, new_child),
        (old_parent, new_parent),
    ]

    relations_mapping = [
        ("parent_id", "parent"),
    ]

    update_relations(
        record_mapping, relations_mapping, "diva-foo", "foo", MockContext()
    )

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
            <relatedItem type="parent" repeatId="0">
                <foo>
                    <linkedRecordType>diva-foo</linkedRecordType>
                    <linkedRecordId>200</linkedRecordId>
                </foo>
            </relatedItem>
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

    record_mapping = [
        (old_child, new_child),
        (old_earlier1, new_earlier1),
        (old_earlier2, new_earlier2),
        (old_parent, new_parent),
    ]

    relations_mapping = [
        ("parent_id", "parent"),
        ("earlier_id", "earlier"),
    ]

    update_relations(
        record_mapping, relations_mapping, "diva-foo", "foo", MockContext()
    )

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
            <relatedItem type="parent" repeatId="0">
                <foo>
                    <linkedRecordType>diva-foo</linkedRecordType>
                    <linkedRecordId>200</linkedRecordId>
                </foo>
            </relatedItem>
            <relatedItem type="earlier" repeatId="0">
                <foo>
                    <linkedRecordType>diva-foo</linkedRecordType>
                    <linkedRecordId>300</linkedRecordId>
                </foo>
            </relatedItem>
            <relatedItem type="earlier" repeatId="1">
                <foo>
                    <linkedRecordType>diva-foo</linkedRecordType>
                    <linkedRecordId>400</linkedRecordId>
                </foo>
            </relatedItem>
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
