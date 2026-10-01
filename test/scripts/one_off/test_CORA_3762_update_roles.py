from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET

import pytest

from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
from scripts.one_off.CORA_3762_update_roles import fix_record, fix_records


@patch("scripts.one_off.CORA_3762_update_roles.list_records")
@patch("scripts.one_off.CORA_3762_update_roles.update_record")
@patch("scripts.one_off.CORA_3762_update_roles.run_with_threads")
def test_updates_outputs_with_role_terms_repeat_id(
    mock_run_with_threads, mock_update_record, mock_list_records
):
    mock_run_with_threads.side_effect = lambda iterable, function, *args: [
        function(item) for item in iterable
    ]
    mock_update_record.return_value = Mock(success=True)

    mock_list_records.return_value = [
        ET.fromstring("""
            <record>
                <data>
                    <output>
                        <recordInfo>
                            <id>output-with-one-role-term</id>
                        </recordInfo>
                        <name type="personal">
                            <role>
                                <roleTerm repeatId="0">author</roleTerm>
                            </role>
                        </name>
                    </output>
                </data>
            </record>
        """),
        ET.fromstring("""
            <record>
                <data>
                    <output>
                        <recordInfo>
                            <id>output-with-two-role-terms</id>
                        </recordInfo>
                        <name type="personal">
                            <role>
                                <roleTerm repeatId="0">author</roleTerm>
                                <roleTerm repeatId="1">editor</roleTerm>
                            </role>
                        </name>
                    </output>
                </data>
            </record>
        """),
        ET.fromstring("""
            <record>
                <data>
                    <output>
                        <recordInfo>
                            <id>output-with-no-person</id>
                        </recordInfo>
                    </output>
                </data>
            </record>
        """),
    ]

    fix_records(MockContext(), apply=True)

    assert mock_update_record.call_count == 2

    assert_equal_for_xml_and_xml_string(
        mock_update_record.call_args_list[0].args[0],
        """
            <record>
                <data>
                    <output>
                        <recordInfo>
                            <id>output-with-one-role-term</id>
                        </recordInfo>
                        <name type="personal">
                            <role repeatId="0">
                                <roleTerm>author</roleTerm>
                            </role>
                        </name>
                    </output>
                </data>
            </record>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        mock_update_record.call_args_list[1].args[0],
        """
            <record>
                <data>
                    <output>
                        <recordInfo>
                            <id>output-with-two-role-terms</id>
                        </recordInfo>
                        <name type="personal">
                            <role repeatId="0">
                                <roleTerm>author</roleTerm>
                            </role>
                            <role repeatId="1">
                                <roleTerm>editor</roleTerm>
                            </role>
                        </name>
                    </output>
                </data>
            </record>
        """,
    )


@patch("scripts.one_off.CORA_3762_update_roles.update_record")
def test_skips_record_without_personal_name(mock_update_record):
    record = ET.fromstring("""
        <record>
            <data>
                <output>
                    <recordInfo>
                        <id>output-with-no-person</id>
                    </recordInfo>
                </output>
            </data>
        </record>
    """)

    result = fix_record(record, MockContext(), apply=True)

    assert result == "skipped"
    mock_update_record.assert_not_called()


@patch("scripts.one_off.CORA_3762_update_roles.update_record")
def test_skips_record_without_role_terms_to_migrate(mock_update_record):
    record = ET.fromstring("""
        <record>
            <data>
                <output>
                    <recordInfo>
                        <id>output-without-repeat_id</id>
                    </recordInfo>
                    <name type="personal">
                        <role>
                            <roleTerm>author</roleTerm>
                        </role>
                    </name>
                </output>
            </data>
        </record>
    """)

    result = fix_record(record, MockContext(), apply=True)

    assert result == "skipped"
    mock_update_record.assert_not_called()


@patch("scripts.one_off.CORA_3762_update_roles.update_record")
def test_skips_person_without_role_terms_to_migrate_and_updates_other_person(
    mock_update_record,
):
    mock_update_record.return_value = Mock(success=True)
    record = ET.fromstring("""
        <record>
            <data>
                <output>
                    <recordInfo>
                        <id>output-with-mixed-persons</id>
                    </recordInfo>
                    <name type="personal">
                        <role>
                            <roleTerm>author</roleTerm>
                        </role>
                    </name>
                    <name type="personal">
                        <role>
                            <roleTerm repeatId="0">editor</roleTerm>
                        </role>
                    </name>
                </output>
            </data>
        </record>
    """)

    result = fix_record(record, MockContext(), apply=True)

    assert result == "updated"
    mock_update_record.assert_called_once()
    assert_equal_for_xml_and_xml_string(
        mock_update_record.call_args.args[0],
        """
            <record>
                <data>
                    <output>
                        <recordInfo>
                            <id>output-with-mixed-persons</id>
                        </recordInfo>
                        <name type="personal">
                            <role>
                                <roleTerm>author</roleTerm>
                            </role>
                        </name>
                        <name type="personal">
                            <role repeatId="0">
                                <roleTerm>editor</roleTerm>
                            </role>
                        </name>
                    </output>
                </data>
            </record>
        """,
    )


@patch("scripts.one_off.CORA_3762_update_roles.update_record")
def test_skips_person_with_multiple_roles(mock_update_record):
    record = ET.fromstring("""
        <record>
            <data>
                <output>
                    <recordInfo>
                        <id>output-with-multiple-roles</id>
                    </recordInfo>
                    <name type="personal">
                        <role>
                            <roleTerm repeatId="0">author</roleTerm>
                        </role>
                        <role>
                            <roleTerm repeatId="1">editor</roleTerm>
                        </role>
                    </name>
                </output>
            </data>
        </record>
    """)

    result = fix_record(record, MockContext(), apply=True)

    assert result == "skipped"
    mock_update_record.assert_not_called()


def test_raises_when_failed_to_create_new_role():
    record = ET.fromstring("""
        <record>
            <data>
                <output>
                    <recordInfo>
                        <id>output-with-one-role-term</id>
                    </recordInfo>
                    <name type="personal">
                        <role>
                            <roleTerm repeatId="0">author</roleTerm>
                        </role>
                    </name>
                </output>
            </data>
        </record>
    """)

    def create_group_side_effect(name, *args, **kwargs):
        if name == "role":
            return None
        return ET.Element(name)

    with patch(
        "scripts.one_off.CORA_3762_update_roles.create_group",
        side_effect=create_group_side_effect,
    ):
        with pytest.raises(AssertionError, match="Failed to create new role element"):
            fix_record(record, MockContext(), apply=False)


@patch("scripts.one_off.CORA_3762_update_roles.update_record")
def test_does_not_update_record_when_apply_is_false(mock_update_record):
    record = ET.fromstring("""
        <record><data><output>
            <recordInfo><id>output-1</id></recordInfo>
            <name type="personal"><role>
                <roleTerm repeatId="0">author</roleTerm>
            </role></name>
        </output></data></record>
    """)

    result = fix_record(record, MockContext(), apply=False)

    assert result == "updated"
    mock_update_record.assert_not_called()
