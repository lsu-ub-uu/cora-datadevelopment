from fedora_to_cora.output_relations_migrate import (
    migrate_output_relations,
    OutputRelationMigrationResult,
)
from fedora_to_cora.output_migration_result import OutputMigrationResult, OutputRelation
from cora.update import UpdateRecordResult
from unittest.mock import patch
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext


def test_no_relations():
    output_migration_result = OutputMigrationResult(
        status="SUCCESS", pid="diva2:123456", cora_id="123", errors=[], relations=[]
    )
    result = migrate_output_relations(output_migration_result, MockContext())
    assert result.status == "NO_RELATIONS"
    assert result.pid == "diva2:123456"
    assert result.cora_id == "123"


@patch("fedora_to_cora.output_relations_migrate.get_cora_id_by_old_id")
@patch("fedora_to_cora.output_relations_migrate.get_record")
@patch("fedora_to_cora.output_relations_migrate.update_record")
def test_migrates_output_constituent_relation(
    mock_update_cora_record, mock_get_cora_record, mock_get_cora_id_by_old_id
):
    output_migration_result = OutputMigrationResult(
        status="SUCCESS",
        pid="diva2:123456",
        cora_id="123",
        errors=[],
        relations=[OutputRelation(type="constituent", pid="diva2:654321")],
    )

    mock_get_cora_record.side_effect = lambda context, record_type, record_id: (
        ET.fromstring("""
            <record>
                <data>
                    <output>
                        <recordInfo>
                            <id>123</id>
                        </recordInfo>
                    </output>
                </data>
            </record>
    """) if record_type == "diva-output" and record_id == "123" else None
    )

    mock_get_cora_id_by_old_id.side_effect = lambda old_id, record_type, context: (
        "456" if old_id == "diva2:654321" else None
    )

    mock_update_cora_record.return_value = UpdateRecordResult(success=True)

    result = migrate_output_relations(output_migration_result, MockContext())

    assert result.status == "UPDATED"
    assert result.pid == "diva2:123456"
    assert result.cora_id == "123"

    assert mock_get_cora_record.call_count == 1
    assert mock_get_cora_id_by_old_id.call_count == 1
    assert mock_update_cora_record.call_count == 1

    updated_xml = mock_update_cora_record.call_args[0][0]
    assert_equal_for_xml_and_xml_string(
        updated_xml,
        """
            <record>
                <data>
                    <output>
                        <recordInfo>
                            <id>123</id>
                        </recordInfo>
                        <related type="constituent" repeatId="0">
                            <output>
                                <linkedRecordType>diva-output</linkedRecordType>
                                <linkedRecordId>456</linkedRecordId>
                            </output>
                        </related>
                    </output>
                </data>
            </record>
    """,
    )


@patch("fedora_to_cora.output_relations_migrate.get_cora_id_by_old_id")
@patch("fedora_to_cora.output_relations_migrate.get_record")
@patch("fedora_to_cora.output_relations_migrate.update_record")
def test_migrates_output_related_relation(
    mock_update_cora_record, mock_get_cora_record, mock_get_cora_id_by_old_id
):
    output_migration_result = OutputMigrationResult(
        status="SUCCESS",
        pid="diva2:123456",
        cora_id="123",
        errors=[],
        relations=[OutputRelation(type="related", pid="diva2:654321")],
    )

    mock_get_cora_record.side_effect = lambda context, record_type, record_id: (
        ET.fromstring("""
            <record>
                <data>
                    <output>
                        <recordInfo>
                            <id>123</id>
                        </recordInfo>
                    </output>
                </data>
            </record>
    """) if record_type == "diva-output" and record_id == "123" else None
    )

    mock_get_cora_id_by_old_id.side_effect = lambda old_id, record_type, context: (
        "456" if old_id == "diva2:654321" else None
    )

    mock_update_cora_record.return_value = UpdateRecordResult(success=True)

    result = migrate_output_relations(output_migration_result, MockContext())

    assert result.status == "UPDATED"
    assert result.pid == "diva2:123456"
    assert result.cora_id == "123"

    assert mock_get_cora_record.call_count == 1
    assert mock_get_cora_id_by_old_id.call_count == 1
    assert mock_update_cora_record.call_count == 1

    updated_xml = mock_update_cora_record.call_args[0][0]
    assert_equal_for_xml_and_xml_string(
        updated_xml,
        """
            <record>
                <data>
                    <output>
                        <recordInfo>
                            <id>123</id>
                        </recordInfo>
                        <related repeatId="0">
                            <output>
                                <linkedRecordType>diva-output</linkedRecordType>
                                <linkedRecordId>456</linkedRecordId>
                            </output>
                        </related>
                    </output>
                </data>
            </record>
    """,
    )


@patch("fedora_to_cora.output_relations_migrate.get_cora_id_by_old_id")
@patch("fedora_to_cora.output_relations_migrate.get_record")
@patch("fedora_to_cora.output_relations_migrate.update_record")
def test_migrates_multiple_relations(
    mock_update_cora_record, mock_get_cora_record, mock_get_cora_id_by_old_id
):
    output_migration_result = OutputMigrationResult(
        status="SUCCESS",
        pid="diva2:123456",
        cora_id="123",
        errors=[],
        relations=[
            OutputRelation(type="constituent", pid="diva2:222222"),
            OutputRelation(type="constituent", pid="diva2:333333"),
            OutputRelation(type="related", pid="diva2:444444"),
            OutputRelation(type="related", pid="diva2:555555"),
        ],
    )

    mock_get_cora_record.side_effect = lambda context, record_type, record_id: (
        ET.fromstring("""
            <record>
                <data>
                    <output>
                        <recordInfo>
                            <id>123</id>
                        </recordInfo>
                    </output>
                </data>
            </record>
    """) if record_type == "diva-output" and record_id == "123" else None
    )

    mock_get_cora_id_by_old_id.side_effect = lambda old_id, record_type, context: (
        "222"
        if old_id == "diva2:222222"
        else (
            "333"
            if old_id == "diva2:333333"
            else (
                "444"
                if old_id == "diva2:444444"
                else "555" if old_id == "diva2:555555" else None
            )
        )
    )

    mock_update_cora_record.return_value = UpdateRecordResult(success=True)

    result = migrate_output_relations(output_migration_result, MockContext())

    assert result.status == "UPDATED"
    assert result.pid == "diva2:123456"
    assert result.cora_id == "123"

    assert mock_get_cora_record.call_count == 1
    assert mock_get_cora_id_by_old_id.call_count == 4
    assert mock_update_cora_record.call_count == 1

    updated_xml = mock_update_cora_record.call_args[0][0]
    assert_equal_for_xml_and_xml_string(
        updated_xml,
        """
            <record>
                <data>
                    <output>
                        <recordInfo>
                            <id>123</id>
                        </recordInfo>
                        <related type="constituent" repeatId="0">
                            <output>
                                <linkedRecordType>diva-output</linkedRecordType>
                                <linkedRecordId>222</linkedRecordId>
                            </output>
                        </related>
                        <related type="constituent" repeatId="1">
                            <output>
                                <linkedRecordType>diva-output</linkedRecordType>
                                <linkedRecordId>333</linkedRecordId>
                            </output>
                        </related>
                        <related repeatId="2">
                            <output>
                                <linkedRecordType>diva-output</linkedRecordType>
                                <linkedRecordId>444</linkedRecordId>
                            </output>
                        </related>
                        <related repeatId="3">
                            <output>
                                <linkedRecordType>diva-output</linkedRecordType>
                                <linkedRecordId>555</linkedRecordId>
                            </output>
                        </related>
                    </output>
                </data>
            </record>
    """,
    )


@patch("fedora_to_cora.output_relations_migrate.get_cora_id_by_old_id")
@patch("fedora_to_cora.output_relations_migrate.get_record")
@patch("fedora_to_cora.output_relations_migrate.update_record")
def test_failed_to_get_cora_record(
    mock_update_cora_record, mock_get_cora_record, mock_get_cora_id_by_old_id
):
    output_migration_result = OutputMigrationResult(
        status="SUCCESS",
        pid="diva2:123456",
        cora_id="123",
        errors=[],
        relations=[OutputRelation(type="related", pid="diva2:654321")],
    )

    mock_get_cora_record.side_effect = Exception(
        "❌ An error occurred while fetching record diva-output with id 123: Failed to get Cora record"
    )

    mock_get_cora_id_by_old_id.side_effect = lambda old_id, record_type, context: (
        "456" if old_id == "diva2:654321" else None
    )

    mock_update_cora_record.return_value = UpdateRecordResult(success=True)

    result = migrate_output_relations(output_migration_result, MockContext())

    assert result.status == "FAILED"
    assert result.pid == "diva2:123456"
    assert result.cora_id == "123"
    assert (
        result.error
        == "❌ An error occurred while fetching record diva-output with id 123: Failed to get Cora record"
    )

    assert mock_get_cora_record.call_count == 1
    assert mock_get_cora_id_by_old_id.call_count == 0
    assert mock_update_cora_record.call_count == 0


@patch("fedora_to_cora.output_relations_migrate.get_cora_id_by_old_id")
@patch("fedora_to_cora.output_relations_migrate.get_record")
@patch("fedora_to_cora.output_relations_migrate.update_record")
def test_failed_to_get_cora_id_by_old_id(
    mock_update_cora_record, mock_get_cora_record, mock_get_cora_id_by_old_id
):
    output_migration_result = OutputMigrationResult(
        status="SUCCESS",
        pid="diva2:123456",
        cora_id="123",
        errors=[],
        relations=[OutputRelation(type="related", pid="diva2:654321")],
    )

    mock_get_cora_record.side_effect = lambda context, record_type, record_id: (
        ET.fromstring("""
                <record>
                    <data>
                        <output>
                            <recordInfo>
                                <id>123</id>
                            </recordInfo>
                        </output>
                    </data>
                </record>
        """) if record_type == "diva-output" and record_id == "123" else None
    )

    mock_get_cora_id_by_old_id.side_effect = Exception("Failed to get id by old id")

    mock_update_cora_record.return_value = UpdateRecordResult(success=True)

    result = migrate_output_relations(output_migration_result, MockContext())

    assert result.status == "FAILED"
    assert result.pid == "diva2:123456"
    assert result.cora_id == "123"
    assert result.error == "Failed to get id by old id"

    assert mock_get_cora_record.call_count == 1
    assert mock_get_cora_id_by_old_id.call_count == 1
    assert mock_update_cora_record.call_count == 0


@patch("fedora_to_cora.output_relations_migrate.get_cora_id_by_old_id")
@patch("fedora_to_cora.output_relations_migrate.get_record")
@patch("fedora_to_cora.output_relations_migrate.update_record")
def test_failed_to_update_record(
    mock_update_cora_record, mock_get_cora_record, mock_get_cora_id_by_old_id
):
    output_migration_result = OutputMigrationResult(
        status="SUCCESS",
        pid="diva2:123456",
        cora_id="123",
        errors=[],
        relations=[OutputRelation(type="related", pid="diva2:654321")],
    )

    mock_get_cora_record.side_effect = lambda context, record_type, record_id: (
        ET.fromstring("""
                <record>
                    <data>
                        <output>
                            <recordInfo>
                                <id>123</id>
                            </recordInfo>
                        </output>
                    </data>
                </record>
        """) if record_type == "diva-output" and record_id == "123" else None
    )

    mock_get_cora_id_by_old_id.side_effect = lambda old_id, record_type, context: (
        "456" if old_id == "diva2:654321" else None
    )
    mock_update_cora_record.return_value = UpdateRecordResult(
        success=False, error="because reasons"
    )

    result = migrate_output_relations(output_migration_result, MockContext())

    assert result.status == "FAILED"
    assert result.pid == "diva2:123456"
    assert result.cora_id == "123"
    assert result.error == "Failed to update record: because reasons"

    assert mock_get_cora_record.call_count == 1
    assert mock_get_cora_id_by_old_id.call_count == 1
    assert mock_update_cora_record.call_count == 1
