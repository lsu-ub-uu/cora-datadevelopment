from unittest.mock import patch
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
from cora.create import CreateRecordSuccessResult
from db_to_cora.programmes_migrate import programmes_migrate


@patch("db_to_cora.programmes_migrate.get_programmes")
@patch(
    "db_to_cora.records_import.create_record",
)
def test_migrate_a_programme_without_relations(mock_create_record, mock_get_programmes):
    mock_get_programmes.return_value = ET.fromstring(
        """
            <SELECT>
                <DATA_RECORD>
                    <domain>somedomain</domain>
                    <old_id>40103</old_id>
                    <end_date></end_date>
                    <name_swe>Digital humaniora</name_swe>
                    <name_eng>Digital humanities</name_eng>
                    <broader_id></broader_id>
                    <earlier_id></earlier_id>
                </DATA_RECORD>
            </SELECT>
    """
    )

    mock_create_record.return_value = CreateRecordSuccessResult(
        "diva-programme:40103",
        ET.fromstring(
            """
              <record>
                <data>
                    <recordInfo>
                        <id>diva-programme:40103</id>
                    </recordInfo>
                </data> 
              </record>                   
            """
        ),
    )

    number_of_records = programmes_migrate(
        MockContext(), "localhost", 5432, "auradb", "db_user", "db_password", "somedomain"
    )

    assert number_of_records == 1
    mock_create_record.assert_called_once()
    created_record = mock_create_record.call_args.args[0]

    assert_equal_for_xml_and_xml_string(
        created_record,
        """
            <programme>
                <recordInfo>
                    <validationType>
                        <linkedRecordType>validationType</linkedRecordType>
                        <linkedRecordId>diva-programme</linkedRecordId>
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
            </programme>
            """,
    )


@patch("db_to_cora.programmes_migrate.get_programmes")
@patch(
    "db_to_cora.records_import.create_record",
)
@patch("db_to_cora.update_relations.update_record")
def test_migrates_a_programme_with_relations(
    mock_update_record, mock_create_record, mock_get_programmes
):
    mock_get_programmes.return_value = ET.fromstring(
        """
            <SELECT>
                <DATA_RECORD>
                    <domain>somedomain</domain>
                    <old_id>1</old_id>
                    <end_date></end_date>
                    <name_swe>Barnprogram</name_swe>
                    <name_eng>Child Programme</name_eng>
                    <broader_id>2</broader_id>
                    <earlier_id>3</earlier_id>
                </DATA_RECORD>
                <DATA_RECORD>
                    <domain>somedomain</domain>
                    <old_id>2</old_id>
                    <end_date></end_date>
                    <name_swe>Bredare program</name_swe>
                    <name_eng>Broader Programme</name_eng>
                    <broader_id></broader_id>
                    <earlier_id></earlier_id>
                </DATA_RECORD>
                <DATA_RECORD>
                    <domain>somedomain</domain>
                    <old_id>3</old_id>
                    <end_date></end_date>
                    <name_swe>Tidigare program</name_swe>
                    <name_eng>Earlier Programme</name_eng>
                    <broader_id></broader_id>
                    <earlier_id></earlier_id>
                </DATA_RECORD>
            </SELECT>
    """
    )

    def create_record_side_effect(record, record_type, context):
        old_id = record.findtext(".//oldId")
        return CreateRecordSuccessResult(
            f"diva-programme:{old_id}",
            ET.fromstring(
                f"""
                <record>
                    <data>
                        <programme>
                            <recordInfo>
                                <id>diva-programme:{old_id}</id>
                                <oldId>{old_id}</oldId>
                            </recordInfo>
                        </programme>
                    </data> 
                </record>                   
                """
            ),
        )

    mock_create_record.side_effect = create_record_side_effect

    number_of_records = programmes_migrate(
        MockContext(), "localhost", 5432, "auradb", "db_user", "db_password", "somedomain"
    )

    assert number_of_records == 3
    assert mock_create_record.call_count == 3
    assert mock_update_record.call_count == 1
    assert_equal_for_xml_and_xml_string(
        mock_update_record.call_args_list[0].args[0],
        """
        <programme>
            <recordInfo>
                <id>diva-programme:1</id>
                <oldId>1</oldId>
            </recordInfo>
            <related type="broader" repeatId="0">
                <programme>
                    <linkedRecordType>diva-programme</linkedRecordType>
                    <linkedRecordId>diva-programme:2</linkedRecordId>
                </programme>
            </related>
            <related type="earlier" repeatId="0">
                <programme>
                    <linkedRecordType>diva-programme</linkedRecordType>
                    <linkedRecordId>diva-programme:3</linkedRecordId>
                </programme>
            </related>
        </programme>
    """,
    )
