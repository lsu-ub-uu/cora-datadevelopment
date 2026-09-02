from unittest.mock import patch
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
from cora.create import CreateRecordSuccessResult
from db_to_cora.funders_migrate import funders_migrate


@patch("db_to_cora.funders_migrate.get_funders")
@patch(
    "db_to_cora.records_import.create_record",
)
def test_migrate_a_funder(mock_create_record, mock_get_funders):
    mock_get_funders.return_value = ET.fromstring(
        """
            <SELECT>
                <DATA_RECORD>
                    <old_id>1234</old_id>
                    <name_swe>Ett namn</name_swe>
                    <name_eng>A name</name_eng>
                </DATA_RECORD>
            </SELECT>
    """
    )

    mock_create_record.return_value = CreateRecordSuccessResult(
        "diva-funder:1234",
        ET.fromstring(
            """
              <record>
                <data>
                    <recordInfo>
                        <id>diva-funder:1234</id>
                    </recordInfo>
                </data> 
              </record>                   
            """
        ),
    )

    number_of_records = funders_migrate(MockContext(), "localhost", 5432, "auradb", "db_user", "db_password")

    assert number_of_records == 1
    mock_create_record.assert_called_once()
    created_record = mock_create_record.call_args.args[0]

    assert_equal_for_xml_and_xml_string(
        created_record,
        """
            <funder>
                <recordInfo>
                    <validationType>
                        <linkedRecordType>validationType</linkedRecordType>
                        <linkedRecordId>diva-funder</linkedRecordId>
                    </validationType>
                    <dataDivider>
                        <linkedRecordType>system</linkedRecordType>
                        <linkedRecordId>divaData</linkedRecordId>
                    </dataDivider>
                    <oldId>1234</oldId>
                </recordInfo>
                <authority lang="swe" repeatId="swe">
                    <name type="corporate">
                        <namePart>Ett namn</namePart>
                    </name>
                </authority>
                <authority lang="eng" repeatId="eng">
                    <name type="corporate">
                        <namePart>A name</namePart>
                    </name>
                </authority>
            </funder>
            """,
    )
