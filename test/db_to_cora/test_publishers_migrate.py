from unittest.mock import patch
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
from cora.create import CreateRecordSuccessResult
from db_to_cora.publishers_migrate import publishers_migrate


@patch("db_to_cora.publishers_migrate.get_publishers")
@patch(
    "db_to_cora.records_import.create_record",
)
def test_migrate_a_publisher(mock_create_record, mock_get_publishers):
    mock_get_publishers.return_value = ET.fromstring(
        """
            <SELECT>
                <DATA_RECORD>
                    <old_id>1234</old_id>
                    <name>Some publisher name</name>
                </DATA_RECORD>
            </SELECT>
    """
    )

    mock_create_record.return_value = CreateRecordSuccessResult(
        "diva-publisher:1234",
        ET.fromstring(
            """
              <record>
                <data>
                    <recordInfo>
                        <id>diva-publisher:1234</id>
                    </recordInfo>
                </data> 
              </record>                   
            """
        ),
    )

    number_of_records = publishers_migrate(MockContext(), "localhost", 5432, "auradb", "db_user", "db_password")

    assert number_of_records == 1
    mock_create_record.assert_called_once()
    created_record = mock_create_record.call_args.args[0]

    assert_equal_for_xml_and_xml_string(
        created_record,
        """
            <publisher>
                <recordInfo>
                    <validationType>
                        <linkedRecordType>validationType</linkedRecordType>
                        <linkedRecordId>diva-publisher</linkedRecordId>
                    </validationType>
                    <dataDivider>
                        <linkedRecordType>system</linkedRecordType>
                        <linkedRecordId>divaData</linkedRecordId>
                    </dataDivider>
                    <oldId>1234</oldId>
                </recordInfo>
                <name type="corporate">
                    <namePart>Some publisher name</namePart>
                </name>
            </publisher>
            """,
    )
