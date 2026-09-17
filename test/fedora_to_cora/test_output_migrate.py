import xml.etree.ElementTree as ET
from unittest.mock import patch
from common.test_helper import assert_equal_for_xml_and_xml_string
from common.xml_validate import XMLValidationError
from cora.create import CreateRecordFailureResult, CreateRecordSuccessResult
from fedora_to_cora.output_migrate import output_migrate
from cora.context import MockContext
from fedora_to_cora.output_migration_result import OutputRelation


@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.validate_xml")
def test_migrate_with_apply_false(
    mock_validate_xml, mock_create, mock_validate, mock_transform
):
    mock_context = MockContext()

    source_record = ET.fromstring("""
        <publication>
            <pid>diva2:12345</pid>
            <title>Test Publication</title>
        </publication>
        """)

    mock_cora_output = ET.fromstring("""
        <record>
            <recordInfo>
                <id>test-id</id>
            </recordInfo>
        </record>
        """)

    mock_transform.return_value = mock_cora_output
    mock_validate.return_value = (True, [])

    result = output_migrate(source_record, mock_context, apply=False)

    assert result.status == "SUCCESS"
    assert result.cora_id is None
    assert result.relations == []
    assert result.errors is None

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    mock_create.assert_not_called()


@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.attachments_migrate")
@patch("fedora_to_cora.output_migrate.validate_xml")
def test_success_migrate_with_apply_true_and_with_binaries_true(
    mock_validate_xml,
    mock_attachments_migrate,
    mock_create_record,
    mock_validate_record,
    mock_transform,
):
    mock_context = MockContext()

    source_record = ET.fromstring("""
        <publication>
            <pid>diva2:12345</pid>
            <title>Test Publication</title>
        </publication>
        """)

    mock_cora_output = ET.fromstring("""
        <record>
            <titleInfo>Test Publication</titleInfo>
            <oldId>diva2:12345</oldId>
        </record>
        """)

    mock_transform.return_value = mock_cora_output

    mock_validate_record.return_value = (True, [])

    mock_created_record = ET.Element("record")
    mock_create_record.return_value = CreateRecordSuccessResult(
        record_id="123", response_data=mock_created_record
    )

    mock_attachments_migrate.return_value = (True, [])

    result = output_migrate(source_record, mock_context, apply=True, with_binaries=True)

    assert result.status == "SUCCESS"
    assert result.cora_id == "123"
    assert result.errors is None

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate_record.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    mock_create_record.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    mock_attachments_migrate.assert_called_once_with(
        source_record, mock_created_record, mock_context, fedora_url=""
    )


@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.attachments_migrate")
@patch("fedora_to_cora.output_migrate.validate_xml")
@patch("fedora_to_cora.output_migrate.create_relations")
def test_success_migrate_with_apply_true_and_with_binaries_true_with_relations(
    mock_create_relations,
    mock_validate_xml,
    mock_attachments_migrate,
    mock_create_record,
    mock_validate_record,
    mock_transform,
):
    mock_context = MockContext()

    source_record = ET.fromstring("""
        <publication>
            <pid>diva2:12345</pid>
            <title>Test Publication</title>
        </publication>
        """)

    mock_cora_output = ET.fromstring("""
        <record>
            <titleInfo>Test Publication</titleInfo>
            <oldId>diva2:12345</oldId>
        </record>
        """)

    mock_transform.return_value = mock_cora_output

    mock_validate_record.return_value = (True, [])

    mock_relations = [OutputRelation(type="constituent", pid="someOtherPid")]

    mock_create_relations.return_value = mock_relations

    mock_created_record = ET.Element("record")
    mock_create_record.return_value = CreateRecordSuccessResult(
        record_id="123", response_data=mock_created_record
    )

    mock_attachments_migrate.return_value = (True, [])

    result = output_migrate(source_record, mock_context, apply=True, with_binaries=True)

    assert result.status == "SUCCESS"
    assert result.cora_id == "123"
    assert result.relations == mock_relations
    assert result.errors is None


@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.attachments_migrate")
@patch("fedora_to_cora.output_migrate.validate_xml")
def test_success_migrate_with_apply_true_and_with_binaries_false(
    mock_validate_xml,
    mock_attachments_migrate,
    mock_create_record,
    mock_validate_record,
    mock_transform,
):
    mock_context = MockContext()

    source_record = ET.fromstring("""
        <publication>
            <pid>diva2:12345</pid>
            <title>Test Publication</title>
        </publication>
        """)

    mock_cora_output = ET.fromstring("""
        <record>
            <titleInfo>Test Publication</titleInfo>
            <oldId>diva2:12345</oldId>
        </record>
        """)

    mock_transform.return_value = mock_cora_output

    mock_validate_record.return_value = (True, [])

    mock_created_record = ET.Element("record")
    mock_create_record.return_value = CreateRecordSuccessResult(
        record_id="123", response_data=mock_created_record
    )

    mock_attachments_migrate.return_value = (True, [])

    result = output_migrate(
        source_record, mock_context, apply=True, with_binaries=False
    )

    assert result.status == "SUCCESS"
    assert result.cora_id == "123"
    assert result.relations == []
    assert result.errors is None

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate_record.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    mock_create_record.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    mock_attachments_migrate.assert_not_called()


@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.attachments_migrate")
@patch("fedora_to_cora.output_migrate.validate_xml")
@patch("fedora_to_cora.output_migrate.create_relations")
def test_success_migrate_with_apply_true_and_with_binaries_false_with_relations(
    mock_create_relations,
    mock_validate_xml,
    mock_attachments_migrate,
    mock_create_record,
    mock_validate_record,
    mock_transform,
):
    mock_context = MockContext()

    source_record = ET.fromstring("""
        <publication>
            <pid>diva2:12345</pid>
            <title>Test Publication</title>
        </publication>
        """)

    mock_cora_output = ET.fromstring("""
        <record>
            <titleInfo>Test Publication</titleInfo>
            <oldId>diva2:12345</oldId>
        </record>
        """)

    mock_transform.return_value = mock_cora_output

    mock_validate_record.return_value = (True, [])

    mock_relations = [OutputRelation(type="constituent", pid="diva2:12345")]
    mock_create_relations.return_value = mock_relations

    mock_created_record = ET.Element("record")
    mock_create_record.return_value = CreateRecordSuccessResult(
        record_id="123", response_data=mock_created_record
    )

    mock_attachments_migrate.return_value = (True, [])

    result = output_migrate(
        source_record, mock_context, apply=True, with_binaries=False
    )

    assert result.status == "SUCCESS"
    assert result.cora_id == "123"
    assert result.relations == mock_relations
    assert result.errors is None


@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.attachments_migrate")
@patch("fedora_to_cora.output_migrate.delete_record")
@patch("fedora_to_cora.output_migrate.validate_xml")
def test_rollback_when_failed_to_migrate_attachment(
    mock_validate_xml,
    mock_delete_record,
    mock_attachments_migrate,
    mock_create,
    mock_validate,
    mock_transform,
):
    mock_context = MockContext()

    source_record = ET.fromstring("""
        <publication>
            <pid>diva2:12345</pid>
            <title>Test Publication</title>
        </publication>
        """)

    mock_cora_output = ET.fromstring("""
        <record>
            <titleInfo>Test Publication</titleInfo>
            <oldId>diva2:12345</oldId>
        </record>
        """)

    mock_transform.return_value = mock_cora_output
    mock_validate.return_value = (True, [])

    mock_created_record = ET.Element("record")
    mock_create.return_value = CreateRecordSuccessResult(
        record_id="123", response_data=mock_created_record
    )

    mock_attachments_migrate.return_value = (False, ["Failed to upload file"])

    result = output_migrate(source_record, mock_context, apply=True, with_binaries=True)

    assert result.status == "FAILED"
    assert result.cora_id == None
    assert result.relations == []
    assert result.errors == ["Failed to upload file"]
    mock_delete_record.assert_called_once_with(mock_created_record, mock_context)


@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.pretty_print_xml")
@patch("fedora_to_cora.output_migrate.validate_xml")
def test_migrate_with_classic_quality_apply_false(
    mock_validate_xml, mock_pretty_print, mock_create, mock_transform, mock_validate
):
    mock_context = MockContext()

    source_record = ET.fromstring("""
        <publication>
            <pid>12345</pid>
            <title>Test Publication</title>
        </publication>
        """)

    mock_cora_output = ET.fromstring("""
        <record>
            <recordInfo>
                <id>test-id</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>2026</dataQuality>
            <adminInfo>
                <note type="internal">Some internal note.</note>
            </adminInfo>
        </record>
        """)

    mock_transform.return_value = mock_cora_output

    expected_errors = ["Missing required field", "Invalid format"]
    mock_validate.side_effect = [(False, expected_errors), (True, [])]
    mock_pretty_print.return_value = "pretty printed xml"

    result = output_migrate(source_record, mock_context, apply=False)

    assert result.status == "CLASSIC_QUALITY"
    assert result.errors == expected_errors
    assert result.cora_id == None
    assert result.relations == []

    mock_transform.assert_called_once_with(source_record, mock_context)

    assert mock_validate.call_count == 2

    assert mock_create.call_count == 0

    # Assert classic quality record was validated
    validated_output = mock_validate.call_args_list[1][0][0]
    assert_equal_for_xml_and_xml_string(
        validated_output,
        """
        <record>
            <recordInfo>
                <id>test-id</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>classic_publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>classic</dataQuality>
            <adminInfo>
                <note type="internal">Some internal note.Record created with dataQuality "classic" due to validation errors during migration from DiVA Classic. Validation errors:- Missing required field- Invalid format</note>
            </adminInfo>
        </record>
        """,
    )


@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.pretty_print_xml")
@patch("fedora_to_cora.output_migrate.validate_xml")
def test_migrate_with_classic_quality_without_binaries(
    mock_validate_xml, mock_pretty_print, mock_create, mock_transform, mock_validate
):
    mock_context = MockContext()

    source_record = ET.fromstring("""
        <publication>
            <pid>12345</pid>
            <title>Test Publication</title>
        </publication>
        """)

    mock_cora_output = ET.fromstring("""
        <record>
            <recordInfo>
                <id>test-id</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>2026</dataQuality>
            <adminInfo>
                <note type="internal">Some internal note.</note>
            </adminInfo>
        </record>
        """)

    mock_transform.return_value = mock_cora_output

    expected_errors = ["Missing required field", "Invalid format"]
    mock_validate.return_value = (False, expected_errors)
    mock_pretty_print.return_value = "pretty printed xml"

    mock_created_record = ET.Element("record")
    mock_create.return_value = CreateRecordSuccessResult(
        record_id="123", response_data=mock_created_record
    )

    result = output_migrate(source_record, mock_context, apply=True)

    assert result.status == "CLASSIC_QUALITY"
    assert result.errors == expected_errors
    assert result.cora_id == "123"
    assert result.relations == []

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    # Check that pretty_print_xml was called
    mock_pretty_print.assert_called_once()

    assert mock_create.call_count == 1
    created_output = mock_create.call_args[0][0]
    assert_equal_for_xml_and_xml_string(
        created_output,
        """
        <record>
            <recordInfo>
                <id>test-id</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>classic_publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>classic</dataQuality>
            <adminInfo>
                <note type="internal">Some internal note.Record created with dataQuality "classic" due to validation errors during migration from DiVA Classic. Validation errors:- Missing required field- Invalid format</note>
            </adminInfo>
        </record>
        """,
    )


@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.pretty_print_xml")
@patch("fedora_to_cora.output_migrate.validate_xml")
@patch("fedora_to_cora.output_migrate.create_relations")
def test_migrate_with_classic_quality_without_binaries_with_relations(
    mock_create_relations,
    mock_validate_xml,
    mock_pretty_print,
    mock_create,
    mock_transform,
    mock_validate,
):
    mock_context = MockContext()

    source_record = ET.fromstring("""
        <publication>
            <pid>12345</pid>
            <title>Test Publication</title>
        </publication>
        """)

    mock_cora_output = ET.fromstring("""
        <record>
            <recordInfo>
                <id>test-id</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>2026</dataQuality>
            <adminInfo>
                <note type="internal">Some internal note.</note>
            </adminInfo>
        </record>
        """)

    mock_transform.return_value = mock_cora_output

    expected_errors = ["Missing required field", "Invalid format"]
    mock_validate.return_value = (False, expected_errors)
    mock_pretty_print.return_value = "pretty printed xml"

    mock_created_record = ET.Element("record")
    mock_create.return_value = CreateRecordSuccessResult(
        record_id="123", response_data=mock_created_record
    )

    mock_relations = [
        OutputRelation("constituent", "123"),
        OutputRelation("related", "456"),
    ]
    mock_create_relations.return_value = mock_relations

    result = output_migrate(source_record, mock_context, apply=True)

    assert result.status == "CLASSIC_QUALITY"
    assert result.errors == expected_errors
    assert result.cora_id == "123"
    assert result.relations == mock_relations


@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.attachments_migrate")
@patch("fedora_to_cora.output_migrate.pretty_print_xml")
@patch("fedora_to_cora.output_migrate.validate_xml")
def test_migrate_classic_quality_with_apply_true_and_with_binaries_true(
    mock_validate_xml,
    mock_pretty_print,
    mock_attachments_migrate,
    mock_create_record,
    mock_validate_record,
    mock_transform,
):
    mock_context = MockContext()

    source_record = ET.fromstring("""
        <publication>
            <pid>diva2:12345</pid>
            <title>Test Publication</title>
        </publication>
        """)

    mock_cora_output = ET.fromstring("""
        <record>
            <recordInfo>
                <id>test-id</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>2026</dataQuality>
            <adminInfo>
                <note type="internal">Some internal note.</note>
            </adminInfo>
        </record>
        """)

    mock_transform.return_value = mock_cora_output

    expected_errors = ["Missing required field", "Invalid format"]
    mock_validate_record.return_value = (False, expected_errors)

    mock_pretty_print.return_value = "pretty printed xml"

    mock_created_record = ET.Element("record")
    mock_create_record.return_value = CreateRecordSuccessResult(
        record_id="123", response_data=mock_created_record
    )

    mock_attachments_migrate.return_value = (True, [])

    result = output_migrate(source_record, mock_context, apply=True, with_binaries=True)

    assert result.status == "CLASSIC_QUALITY"
    assert result.errors == expected_errors
    assert result.cora_id == "123"
    assert result.relations == []

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate_record.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    assert mock_create_record.call_count == 1
    created_output = mock_create_record.call_args[0][0]
    assert_equal_for_xml_and_xml_string(
        created_output,
        """
        <record>
            <recordInfo>
                <id>test-id</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>classic_publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>classic</dataQuality>
            <adminInfo>
                <note type="internal">Some internal note.Record created with dataQuality "classic" due to validation errors during migration from DiVA Classic. Validation errors:- Missing required field- Invalid format</note>
            </adminInfo>
        </record>
        """,
    )

    mock_attachments_migrate.assert_called_once_with(
        source_record, mock_created_record, mock_context, fedora_url=""
    )


@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.attachments_migrate")
@patch("fedora_to_cora.output_migrate.pretty_print_xml")
@patch("fedora_to_cora.output_migrate.validate_xml")
@patch("fedora_to_cora.output_migrate.create_relations")
def test_migrate_classic_quality_with_apply_true_and_with_binaries_true_with_relations(
    mock_create_relations,
    mock_validate_xml,
    mock_pretty_print,
    mock_attachments_migrate,
    mock_create_record,
    mock_validate_record,
    mock_transform,
):
    mock_context = MockContext()

    source_record = ET.fromstring("""
        <publication>
            <pid>diva2:12345</pid>
            <title>Test Publication</title>
        </publication>
        """)

    mock_cora_output = ET.fromstring("""
        <record>
            <recordInfo>
                <id>test-id</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>2026</dataQuality>
            <adminInfo>
                <note type="internal">Some internal note.</note>
            </adminInfo>
        </record>
        """)

    mock_transform.return_value = mock_cora_output

    expected_errors = ["Missing required field", "Invalid format"]
    mock_validate_record.return_value = (False, expected_errors)

    mock_pretty_print.return_value = "pretty printed xml"

    mock_created_record = ET.Element("record")
    mock_create_record.return_value = CreateRecordSuccessResult(
        record_id="123", response_data=mock_created_record
    )

    mock_relations = [OutputRelation("constituent", "456")]
    mock_create_relations.return_value = mock_relations

    mock_attachments_migrate.return_value = (True, [])

    result = output_migrate(source_record, mock_context, apply=True, with_binaries=True)

    assert result.status == "CLASSIC_QUALITY"
    assert result.errors == expected_errors
    assert result.cora_id == "123"
    assert result.relations == mock_relations

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate_record.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    assert mock_create_record.call_count == 1
    created_output = mock_create_record.call_args[0][0]
    assert_equal_for_xml_and_xml_string(
        created_output,
        """
        <record>
            <recordInfo>
                <id>test-id</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>classic_publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>classic</dataQuality>
            <adminInfo>
                <note type="internal">Some internal note.Record created with dataQuality "classic" due to validation errors during migration from DiVA Classic. Validation errors:- Missing required field- Invalid format</note>
            </adminInfo>
        </record>
        """,
    )

    mock_attachments_migrate.assert_called_once_with(
        source_record, mock_created_record, mock_context, fedora_url=""
    )


@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.pretty_print_xml")
@patch("fedora_to_cora.output_migrate.validate_xml")
def test_migrate_with_classic_quality_failure(
    mock_validate_xml, mock_pretty_print, mock_create, mock_transform, mock_validate
):
    mock_context = MockContext()

    source_record = ET.fromstring("""
        <publication>
            <pid>12345</pid>
            <title>Test Publication</title>
        </publication>
        """)

    mock_cora_output = ET.fromstring("""
        <record>
            <recordInfo>
                <id>test-id</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>2026</dataQuality>
        </record>
        """)

    mock_transform.return_value = mock_cora_output

    mock_validate.return_value = (
        False,
        ["Missing required field", "Invalid format"],
    )
    mock_pretty_print.return_value = "pretty printed xml"

    mock_create.return_value = CreateRecordFailureResult(
        error="Failed to create record"
    )

    result = output_migrate(source_record, mock_context, apply=True)

    assert result.status == "FAILED"
    assert result.errors == [
        "Failed to create record",
    ]
    assert result.cora_id is None
    assert result.relations == []

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    assert mock_create.call_count == 1


@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.pretty_print_xml")
@patch("fedora_to_cora.output_migrate.validate_xml")
def test_migrate_skip_due_to_duplicate(
    mock_validate_xml, mock_pretty_print, mock_create, mock_transform, mock_validate
):
    mock_context = MockContext()

    source_record = ET.fromstring("""
        <publication>
            <pid>12345</pid>
            <title>Test Publication</title>
        </publication>
        """)

    mock_cora_output = ET.fromstring("""
        <record>
            <recordInfo>
                <id>test-id</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>2026</dataQuality>
            <adminInfo>
                <note type="internal">Some internal note.</note>
            </adminInfo>
        </record>
        """)

    mock_transform.return_value = mock_cora_output

    mock_validate.return_value = (
        False,
        [
            "A record matching the unique rule with [key: oldId, value: 12345] already exists in the system"
        ],
    )
    result = output_migrate(source_record, mock_context, apply=False)

    assert result.status == "SKIPPED"
    assert result.errors == [
        "A record with the same oldId already exists in the system"
    ]
    assert result.cora_id is None
    assert result.relations == []

    mock_transform.assert_called_once_with(source_record, mock_context)

    mock_validate.assert_called_once_with(
        mock_cora_output,
        record_type="diva-output",
        context=mock_context,
    )

    assert mock_create.call_count == 0


@patch("fedora_to_cora.output_migrate.validate_record")
@patch("fedora_to_cora.output_migrate.transform_to_cora_output")
@patch("fedora_to_cora.output_migrate.create_record")
@patch("fedora_to_cora.output_migrate.pretty_print_xml")
@patch(
    "fedora_to_cora.output_migrate.validate_xml",
)
def test_migrate_input_validation_failed(
    mock_validate_xml, mock_pretty_print, mock_create, mock_transform, mock_validate
):
    mock_validate_xml.side_effect = XMLValidationError("invalid xml")

    mock_context = MockContext()

    source_record = ET.fromstring("""
        <publication>
            <pid>12345</pid>
            <title>Test Publication</title>
        </publication>
        """)

    mock_cora_output = ET.fromstring("""
        <record>
            <recordInfo>
                <id>test-id</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>2026</dataQuality>
            <adminInfo>
                <note type="internal">Some internal note.</note>
            </adminInfo>
        </record>
        """)

    mock_transform.return_value = mock_cora_output

    result = output_migrate(source_record, mock_context, apply=False)

    assert result.status == "INPUT_VALIDATION_FAILED"
    assert result.errors == ["invalid xml"]
    assert result.cora_id is None
    assert result.relations == []

    mock_transform.assert_not_called()
    mock_validate.assert_not_called()
    mock_create.assert_not_called()
