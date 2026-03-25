from unittest.mock import patch
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
from cora.create import CreateRecordSuccessResult
from db_to_cora.courses_migrate import courses_migrate


@patch("db_to_cora.courses_migrate.get_courses")
@patch(
    "db_to_cora.records_import.create_record",
)
def test_migrate_a_course_without_relations(mock_create_record, mock_get_courses):
    mock_get_courses.return_value = ET.fromstring(
        """
            <SELECT>
                <DATA_RECORD>
                    <domain>somedomain</domain>
                    <old_id>40103</old_id>
                    <end_date></end_date>
                    <name_swe>Digital humaniora</name_swe>
                    <name_eng>Digital humanities</name_eng>
                    <broader_id></broader_id>
                    <parent_subject_id></parent_subject_id>
                    <earlier_id></earlier_id>
                </DATA_RECORD>
            </SELECT>
    """
    )

    mock_create_record.return_value = CreateRecordSuccessResult(
        "diva-course:40103",
        ET.fromstring(
            """
              <record>
                <data>
                    <recordInfo>
                        <id>diva-course:40103</id>
                    </recordInfo>
                </data> 
              </record>                   
            """
        ),
    )

    number_of_records = courses_migrate(
        MockContext(), "db_user", "db_password", "somedomain"
    )

    assert number_of_records == 1
    mock_create_record.assert_called_once()
    created_record = mock_create_record.call_args.args[0]

    assert_equal_for_xml_and_xml_string(
        created_record,
        """
            <course>
                <recordInfo>
                    <validationType>
                        <linkedRecordType>validationType</linkedRecordType>
                        <linkedRecordId>diva-course</linkedRecordId>
                    </validationType>
                    <dataDivider>
                        <linkedRecordType>system</linkedRecordType>
                        <linkedRecordId>divaData</linkedRecordId>
                    </dataDivider>
                    <permissionUnit>
                        <linkedRecordType>permissionUnit</linkedRecordType>
                        <linkedRecordId>somedomain</linkedRecordId>
                    </permissionUnit>
                    <oldId>40103</oldId>
                </recordInfo>
                <authority lang="swe" repeatId="swe">
                    <topic>Digital humaniora</topic>
                </authority>
                <authority lang="eng" repeatId="eng">
                    <topic>Digital humanities</topic>
                </authority>
            </course>
            """,
    )


@patch("db_to_cora.courses_migrate.get_courses")
@patch(
    "db_to_cora.records_import.create_record",
)
@patch("db_to_cora.update_relations.update_record")
def test_migrates_a_course_with_relations(
    mock_update_record, mock_create_record, mock_get_courses
):
    mock_get_courses.return_value = ET.fromstring(
        """
            <SELECT>
                <DATA_RECORD>
                    <domain>somedomain</domain>
                    <old_id>1</old_id>
                    <end_date></end_date>
                    <name_swe>Barnkurs</name_swe>
                    <name_eng>Child Course</name_eng>
                    <broader_id>2</broader_id>
                    <earlier_id>3</earlier_id>
                </DATA_RECORD>
                <DATA_RECORD>
                    <domain>somedomain</domain>
                    <old_id>2</old_id>
                    <end_date></end_date>
                    <name_swe>Bredare kurs</name_swe>
                    <name_eng>Broader Course</name_eng>
                    <broader_id></broader_id>
                    <earlier_id></earlier_id>
                </DATA_RECORD>
                <DATA_RECORD>
                    <domain>somedomain</domain>
                    <old_id>3</old_id>
                    <end_date></end_date>
                    <name_swe>Föräldrakurs</name_swe>
                    <name_eng>Parent Course</name_eng>
                    <earlier_id></earlier_id>
                </DATA_RECORD>
            </SELECT>
    """
    )

    def create_record_side_effect(record, record_type, context):
        old_id = record.findtext(".//oldId")
        return CreateRecordSuccessResult(
            f"diva-course:{old_id}",
            ET.fromstring(
                f"""
                <record>
                    <data>
                        <course>
                            <recordInfo>
                                <id>diva-course:{old_id}</id>
                                <oldId>{old_id}</oldId>
                            </recordInfo>
                        </course>
                    </data> 
                </record>                   
                """
            ),
        )

    mock_create_record.side_effect = create_record_side_effect

    number_of_records = courses_migrate(
        MockContext(), "db_user", "db_password", "somedomain"
    )

    assert number_of_records == 3
    assert mock_create_record.call_count == 3
    assert mock_update_record.call_count == 1
    assert_equal_for_xml_and_xml_string(
        mock_update_record.call_args_list[0].args[0],
        """
        <course>
            <recordInfo>
                <id>diva-course:1</id>
                <oldId>1</oldId>
            </recordInfo>
            <related type="broader" repeatId="0">
                <course>
                    <linkedRecordType>diva-course</linkedRecordType>
                    <linkedRecordId>diva-course:2</linkedRecordId>
                </course>
            </related>
            <related type="earlier" repeatId="0">
                <course>
                    <linkedRecordType>diva-course</linkedRecordType>
                    <linkedRecordId>diva-course:3</linkedRecordId>
                </course>
            </related>
        </course>
    """,
    )
