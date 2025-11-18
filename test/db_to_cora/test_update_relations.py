import xml.etree.ElementTree as ET
from db_to_cora.update_relations import update_relations
from cora.context import MockContext
from unittest.mock import patch
from common.test_helper import assert_equal_for_xml_and_xml_string


@patch("db_to_cora.update_relations.update_record")
def test_update_relations(mock_update_record):
    old_child = ET.fromstring(
        """
        <record>
            <old_id>1</old_id>
            <parent_id>2</parent_id>
        </record>
    """
    )
    old_parent = ET.fromstring(
        """
        <record>
            <old_id>2</old_id>
        </record>
    """
    )

    new_child = ET.fromstring(
        """
        <record>
            <data>
                <foo>
                    <recordInfo>
                        <id>100</id>
                        <oldId>1</oldId>
                    </recordInfo>
                </foo>
            </data>
        </record>
    """
    )

    new_parent = ET.fromstring(
        """
        <record>
            <data>
                <foo>
                    <recordInfo>
                        <id>200</id>
                        <oldId>2</oldId>
                    </recordInfo>
                </foo>
            </data>
        </record>
    """
    )

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
            <relatedItem type="parent">
                <foo>
                    <linkedRecordType>diva-foo</linkedRecordType>
                    <id>200</id>
                </foo>
            </relatedItem>
        </foo>
        """,
    )
